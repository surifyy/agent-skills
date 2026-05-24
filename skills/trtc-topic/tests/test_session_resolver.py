"""Regression tests for the session-path resolver shared by all topic CLIs.

Background:
    Before commit 1981bac, init_slice_queue.py / next_slice.py / apply.py
    each computed their default `--session` path as `HERE.parents[4] /
    ".trtc-session.yaml"` — i.e. the skill repo root. That's wrong:
    `.trtc-session.yaml` lives in the *user project* (e.g. `demo-0518/`),
    not in the skill repo. When AI ran the script from the user project
    without passing `--session`, it errored with:

        error: session file not found at <skill-repo>/.trtc-session.yaml

    Fix: each CLI now resolves the session path the same way the
    PreToolUse hooks already did:

        1. --session flag, if given (explicit override)
        2. $TRTC_SESSION_PATH env var
        3. $CLAUDE_PROJECT_DIR/.trtc-session.yaml
        4. ./.trtc-session.yaml (cwd fallback)

These tests pin the chain so a future refactor can't silently break it
again. We exercise the actual subprocess (not the import-level resolver)
because the bug surfaced at the subprocess boundary — the shipped script
is what AI invokes.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
INIT = ROOT / "scripts" / "init_slice_queue.py"
NEXT = ROOT / "scripts" / "next_slice.py"
APPLY = ROOT / "scripts" / "apply.py"


def _seed_session(project_root: Path, confirmed_plan=None) -> Path:
    """Drop a minimal .trtc-session.yaml into project_root and return its path."""
    project_root.mkdir(parents=True, exist_ok=True)
    session = project_root / ".trtc-session.yaml"
    session.write_text(
        yaml.safe_dump(
            {
                "schema_version": 1,
                "status": "active",
                "product": "conference",
                "platform": "web",
                "intent": "integrate-scenario",
                "scenario": "general-conference",
                "confirmed_plan": confirmed_plan or ["conference/login-auth"],
                "project_state": {"project_root": str(project_root)},
            },
            sort_keys=False,
            allow_unicode=True,
        )
    )
    return session


def _run(script: Path, *cli_args, cwd: Path, env: dict | None = None) -> subprocess.CompletedProcess:
    """Run a topic CLI with a clean env (so parent-process env vars don't leak in)."""
    base_env = {"PATH": "/usr/bin:/bin"}
    if env:
        base_env.update(env)
    return subprocess.run(
        [sys.executable, str(script), *map(str, cli_args)],
        cwd=str(cwd),
        text=True,
        capture_output=True,
        env=base_env,
    )


# ---------- Resolver chain --------------------------------------------------


class TestSessionResolverChain:
    """The four resolution paths, in priority order."""

    def test_cwd_fallback_finds_session_in_user_project(self, tmp_path):
        """AI's typical setup: cd to user project, no flag, no env vars.

        This is the exact bug the user hit on demo-0518. Without the
        cwd fallback, the script looked at the skill repo root and
        errored.
        """
        project = tmp_path / "demo-0518"
        _seed_session(project)

        # No --session, no env vars, cwd = user project.
        r = _run(INIT, cwd=project)
        assert r.returncode == 0, (
            f"cwd fallback should let init find ./trtc-session.yaml; "
            f"stderr={r.stderr}"
        )
        assert "queue initialised" in r.stdout

    def test_claude_project_dir_env_resolves_when_cwd_is_elsewhere(self, tmp_path):
        """Claude Code sets $CLAUDE_PROJECT_DIR to the user project root.

        The CLI must honour that even when AI's cwd is somewhere else
        (e.g. the skill repo, or `/tmp`). We use init_slice_queue here
        because its output is deterministic ("queue initialised — N slices");
        next_slice.py status would also work but emits "queue not
        initialised" — which would still prove session resolution worked,
        but the assertion is fuzzier.
        """
        project = tmp_path / "user-proj"
        _seed_session(project)

        r = _run(
            INIT,
            cwd=tmp_path,  # not the project
            env={"CLAUDE_PROJECT_DIR": str(project)},
        )
        assert r.returncode == 0, r.stderr
        assert "queue initialised" in r.stdout
        assert "conference/login-auth" in r.stdout

    def test_trtc_session_path_env_wins_over_claude_project_dir(self, tmp_path):
        """Explicit env var beats $CLAUDE_PROJECT_DIR.

        Useful for tests, custom setups, multi-project workflows.
        Strategy: point $TRTC_SESSION_PATH at a real session and
        $CLAUDE_PROJECT_DIR at a project that *has no session file at all*.
        If $CLAUDE_PROJECT_DIR is consulted first the script will error
        with "session file not found"; if $TRTC_SESSION_PATH wins, init
        succeeds.
        """
        real_project = tmp_path / "real"
        _seed_session(real_project)
        bogus_project = tmp_path / "bogus"
        bogus_project.mkdir()  # exists but contains no .trtc-session.yaml

        r = _run(
            INIT,
            cwd=tmp_path,
            env={
                "TRTC_SESSION_PATH": str(real_project / ".trtc-session.yaml"),
                "CLAUDE_PROJECT_DIR": str(bogus_project),
            },
        )
        assert r.returncode == 0, (
            f"$TRTC_SESSION_PATH should take precedence; stderr={r.stderr}"
        )
        assert "queue initialised" in r.stdout

    def test_explicit_session_flag_wins_over_envs(self, tmp_path):
        """--session is the highest-priority override."""
        real_project = tmp_path / "real"
        _seed_session(real_project)

        r = _run(
            NEXT,
            "--session",
            str(real_project / ".trtc-session.yaml"),
            "status",
            cwd=tmp_path,
            env={
                "TRTC_SESSION_PATH": str(tmp_path / "nonexistent.yaml"),
                "CLAUDE_PROJECT_DIR": str(tmp_path / "also-nonexistent"),
            },
        )
        assert r.returncode == 0, (
            f"--session flag should override env vars; stderr={r.stderr}"
        )

    def test_no_session_anywhere_errors_with_actionable_hint(self, tmp_path):
        """When nothing resolves, the error must tell the user what to fix.

        This replaces the silent skill-repo lookup that AI had no way to
        diagnose.
        """
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        r = _run(NEXT, "status", cwd=empty_dir)
        assert r.returncode == 1
        # The error must point at the resolved path AND tell the user how
        # to fix it. We check both halves so paraphrasing the message
        # later doesn't drop the actionable bit.
        assert "session file not found" in r.stderr
        assert (
            "CLAUDE_PROJECT_DIR" in r.stderr
            or "TRTC_SESSION_PATH" in r.stderr
            or "cd to the user project" in r.stderr
        ), (
            f"stderr should hint how to point the script at the session; "
            f"got: {r.stderr}"
        )


# ---------- All three CLIs honour the chain ---------------------------------


class TestAllCLIsUseSameResolver:
    """Sanity check: init_slice_queue / next_slice / apply all behave the same.

    They each reimplement `_resolve_session_path` (no shared module yet)
    so we test all three to catch the case where one drifts.
    """

    @pytest.mark.parametrize("script,subcmd", [
        (INIT, []),
        (NEXT, ["status"]),
    ])
    def test_cli_finds_session_via_cwd(self, script, subcmd, tmp_path):
        project = tmp_path / "user-proj"
        _seed_session(project)
        r = _run(script, *subcmd, cwd=project)
        assert r.returncode == 0, f"{script.name}: {r.stderr}"

    @pytest.mark.parametrize("script,subcmd", [
        (INIT, []),
        (NEXT, ["status"]),
    ])
    def test_cli_finds_session_via_claude_project_dir(self, script, subcmd, tmp_path):
        project = tmp_path / "user-proj"
        _seed_session(project)
        r = _run(
            script,
            *subcmd,
            cwd=tmp_path,
            env={"CLAUDE_PROJECT_DIR": str(project)},
        )
        assert r.returncode == 0, f"{script.name}: {r.stderr}"

    def test_apply_finds_session_via_cwd(self, tmp_path):
        """apply.py needs more setup (state machine seeded to code_written)
        before it'll do anything useful, so it gets its own test rather
        than the parametrised pair above."""
        project = tmp_path / "user-proj"
        session = _seed_session(project)
        # Seed state to code_written so apply.py reaches the project scan.
        sys.path.insert(0, str(ROOT / "scripts" / "lib"))
        try:
            import state_machine
            state_machine.init_queue(session)
            state_machine.advance(session, "mark_slice_read")
            state_machine.advance(session, "mark_code_written")
        finally:
            sys.path.pop(0)

        # apply.py: no --session, no env, cwd = project. Should resolve
        # session via cwd fallback. The actual apply result will be fail
        # (no src/) — but rc != 2 (usage error), and importantly it does
        # NOT error with "session file not found".
        r = _run(APPLY, "--slice", "conference/login-auth", cwd=project)
        assert "session file not found" not in r.stderr, (
            f"apply.py should resolve session via cwd; got: {r.stderr}"
        )
        # rc 1 = apply fail (expected — no src/), rc 0 = apply pass
        # (unexpected here), rc 2 = usage error (regression).
        assert r.returncode in (0, 1), (
            f"unexpected rc={r.returncode}; stderr={r.stderr}"
        )
