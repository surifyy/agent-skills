"""Tests for apply.py — the executable apply gate.

Contract:

    apply.py --slice <slice_id> [--session PATH] [--project PATH]

Runs MUST-rule grep over the project's src/ tree for the given slice, writes
``.trtc-apply-evidence/{slice_safename}.json`` next to the session file, and
advances the state machine:

    pass → mark_apply_passed
    fail → mark_apply_failed

Exit codes:
    0 — pass
    1 — fail
    2 — usage / config error (missing slice id, project root, etc.)
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

APPLY_SCRIPT = (
    Path(__file__).resolve().parents[1] / "scripts" / "apply.py"
)
STATE_MACHINE_DIR = Path(__file__).resolve().parents[1] / "scripts" / "lib"
sys.path.insert(0, str(STATE_MACHINE_DIR))
import state_machine  # noqa: E402
sys.path.pop(0)


def _run_apply(slice_id: str, session_path: Path, project_root: Path | None = None) -> subprocess.CompletedProcess:
    args = [sys.executable, str(APPLY_SCRIPT), "--slice", slice_id, "--session", str(session_path)]
    if project_root is not None:
        args += ["--project", str(project_root)]
    return subprocess.run(args, text=True, capture_output=True)


def _seed_to_code_written(session_path: Path) -> None:
    state_machine.init_queue(session_path)
    state_machine.advance(session_path, "mark_slice_read")
    state_machine.advance(session_path, "mark_code_written")


_PASSING_VUE = '''<template><div /></template>
<script setup lang="ts">
import { useLoginState, LoginEvent } from "@trtc/tuikit-atomicx-vue3";
const { login, setSelfInfo, subscribeEvent } = useLoginState();
await login({ sdkAppId: 0, userId: "u", userSig: "x" });
setSelfInfo({ nickName: "Alice" });
subscribeEvent(LoginEvent.onLoginExpired, () => { /* refresh */ });
subscribeEvent(LoginEvent.onKickedOffline, () => { /* re-login */ });
</script>
'''

_PARTIAL_VUE = '''<template><div /></template>
<script setup lang="ts">
import { useLoginState } from "@trtc/tuikit-atomicx-vue3";
const { login } = useLoginState();
await login({ sdkAppId: 0, userId: "u", userSig: "x" });
</script>
'''


class TestApplyHappyPath:
    def test_pass_advances_state_and_writes_evidence(
        self, session_factory, project_factory
    ):
        path = session_factory()
        proj = project_factory()
        (proj / "src" / "views").mkdir(parents=True, exist_ok=True)
        (proj / "src" / "views" / "MeetingRoom.vue").write_text(_PASSING_VUE)

        _seed_to_code_written(path)
        result = _run_apply("conference/login-auth", path, proj)
        assert result.returncode == 0, f"stdout={result.stdout}\nstderr={result.stderr}"

        _, _, state = state_machine.current_slice(path)
        assert state == "apply_passed"

        ev_dir = path.parent / ".trtc-apply-evidence"
        assert ev_dir.exists()
        ev_files = list(ev_dir.glob("*.json"))
        assert len(ev_files) == 1
        ev = json.loads(ev_files[0].read_text())
        assert ev["status"] == "pass"
        assert ev["slice_id"] == "conference/login-auth"
        assert ev["rules_checked"] >= 1


class TestApplyFailure:
    def test_fail_advances_to_apply_failed_with_issue_list(
        self, session_factory, project_factory
    ):
        path = session_factory()
        proj = project_factory()
        (proj / "src" / "views").mkdir(parents=True, exist_ok=True)
        (proj / "src" / "views" / "MeetingRoom.vue").write_text(_PARTIAL_VUE)

        _seed_to_code_written(path)
        result = _run_apply("conference/login-auth", path, proj)
        assert result.returncode == 1, f"stdout={result.stdout}\nstderr={result.stderr}"

        _, _, state = state_machine.current_slice(path)
        assert state == "apply_failed"

        ev_files = list((path.parent / ".trtc-apply-evidence").glob("*.json"))
        ev = json.loads(ev_files[0].read_text())
        assert ev["status"] == "fail"
        assert ev["issues"], "expected at least one issue listed"
        joined = json.dumps(ev["issues"], ensure_ascii=False)
        assert "setSelfInfo" in joined or "MUST" in joined


class TestApplyDemoTest2Regressions:
    """Regression tests for the two real bugs from demo-test-2.

    Both bugs come from the same loophole pair:

      1. apply.py was checking patterns by literal substring grep.
      2. The fail output / evidence JSON listed the literal patterns.

    AI saw the patterns in fail output → AI wrote those patterns into a
    `// comment` to satisfy the next grep. apply.py passed; the code
    didn't actually call the API.

    Fix kept after the V2 walk-back:
      a) `_strip_comments_and_strings` runs before substring grep, so a
         pattern hidden in `// foo`, `/* foo */`, `"foo"`, `'foo'`, or
         `` `foo` `` is invisible to the matcher.
      b) Fail output / evidence JSON list the rule **text** only, never
         the literal `patterns`. AI cannot copy a string it never saw.
    """

    def test_pattern_in_comment_does_not_pass(
        self, session_factory, project_factory
    ):
        """A `.vue` whose only mention of the API is in `// comments` must FAIL.

        Without `_strip_comments_and_strings`, a literal substring grep
        would match the comment text and pass — that was the demo-test-2
        bug. After the fix, the comment is whitespaced before grep so the
        rule's `setSelfInfo` / `subscribeEvent` patterns are not found.
        """
        path = session_factory()
        proj = project_factory()
        (proj / "src" / "views").mkdir(parents=True, exist_ok=True)

        # login() is called for real; the rest is comment-stuffed.
        comment_stuffed = '''<template><div /></template>
<script setup lang="ts">
import { useLoginState } from "@trtc/tuikit-atomicx-vue3";
const { login } = useLoginState();
await login({ sdkAppId: 0, userId: "u", userSig: "x" });
// setSelfInfo({ nickName: "Alice" });
// subscribeEvent(LoginEvent.onLoginExpired, () => {});
// subscribeEvent(LoginEvent.onKickedOffline, () => {});
/*
  setSelfInfo({ nickName: "Bob" });
  subscribeEvent(LoginEvent.onLoginExpired, () => {});
*/
</script>
'''
        (proj / "src" / "views" / "MeetingRoom.vue").write_text(comment_stuffed)

        _seed_to_code_written(path)
        result = _run_apply("conference/login-auth", path, proj)
        assert result.returncode == 1, (
            "comment-stuffed code must fail apply — comments are stripped "
            "before grep so the pattern can't hide there. "
            f"stdout={result.stdout}\nstderr={result.stderr}"
        )

        _, _, state = state_machine.current_slice(path)
        assert state == "apply_failed"

    def test_pattern_in_string_literal_does_not_pass(
        self, session_factory, project_factory
    ):
        """A `.vue` whose only mention of the API is inside string literals must FAIL.

        Same bug class as the comment case: AI could stuff the pattern
        into `"setSelfInfo({...})"` to game substring grep. The string
        literal stripper neutralises this too.
        """
        path = session_factory()
        proj = project_factory()
        (proj / "src" / "views").mkdir(parents=True, exist_ok=True)

        string_stuffed = '''<template><div /></template>
<script setup lang="ts">
import { useLoginState } from "@trtc/tuikit-atomicx-vue3";
const { login } = useLoginState();
await login({ sdkAppId: 0, userId: "u", userSig: "x" });
const dummy = "setSelfInfo({ nickName: 'Alice' })";
const dummy2 = 'subscribeEvent(LoginEvent.onLoginExpired, () => {})';
const dummy3 = `subscribeEvent(LoginEvent.onKickedOffline, () => {})`;
</script>
'''
        (proj / "src" / "views" / "MeetingRoom.vue").write_text(string_stuffed)

        _seed_to_code_written(path)
        result = _run_apply("conference/login-auth", path, proj)
        assert result.returncode == 1, (
            "string-literal-stuffed code must fail apply — strings are "
            "stripped before grep. "
            f"stdout={result.stdout}\nstderr={result.stderr}"
        )

    def test_fail_output_does_not_leak_literal_patterns(
        self, session_factory, project_factory
    ):
        """Evidence JSON `issues[]` must not contain a `patterns` field.

        Why: surfacing the parser's clean list of patterns in fail output
        is what taught AI to comment-stuff. The contract after walk-back is
        that issues carry rule **text** + type only, not the extracted
        pattern list. The rule_text itself may contain inline backticks
        (they're part of the slice's human-readable MUST line) — the lever
        we pull is removing the *separate, clean* `patterns` array.
        """
        path = session_factory()
        proj = project_factory()
        (proj / "src" / "views").mkdir(parents=True, exist_ok=True)
        (proj / "src" / "views" / "MeetingRoom.vue").write_text(_PARTIAL_VUE)

        _seed_to_code_written(path)
        result = _run_apply("conference/login-auth", path, proj)
        assert result.returncode == 1

        ev_files = list((path.parent / ".trtc-apply-evidence").glob("*.json"))
        ev = json.loads(ev_files[0].read_text())
        assert ev["issues"], "regression: failure should produce at least one issue"
        for issue in ev["issues"]:
            assert "patterns" not in issue, (
                f"issue leaks 'patterns' field: {issue}. "
                "Patterns must stay out of evidence JSON so AI can't see "
                "a clean pattern list to comment-stuff."
            )
            # Also assert the issue has the keys we DO want.
            assert "rule_text" in issue
            assert "type" in issue


class TestApplyStaticOnly:
    def test_no_project_src_falls_back_to_static_only(
        self, session_factory, tmp_path
    ):
        path = session_factory()
        empty_proj = tmp_path / "user-project"
        empty_proj.mkdir(exist_ok=True)

        _seed_to_code_written(path)
        result = _run_apply("conference/login-auth", path, empty_proj)
        assert result.returncode == 1
        ev = json.loads(next((path.parent / ".trtc-apply-evidence").glob("*.json")).read_text())
        assert ev["mode"] == "static-only"


class TestApplyUsageErrors:
    def test_refuses_when_not_in_code_written(self, session_factory, project_factory):
        path = session_factory()
        proj = project_factory()
        state_machine.init_queue(path)

        result = _run_apply("conference/login-auth", path, proj)
        assert result.returncode == 2
        assert "code_written" in result.stderr or "state" in result.stderr.lower()

    def test_refuses_when_slice_does_not_match_cursor(
        self, session_factory, project_factory
    ):
        path = session_factory()
        proj = project_factory()
        _seed_to_code_written(path)
        result = _run_apply("conference/room-lifecycle", path, proj)
        assert result.returncode == 2
        assert "current slice" in result.stderr.lower() or "login-auth" in result.stderr

    def test_refuses_when_session_missing(self, tmp_path, project_factory):
        proj = project_factory()
        result = _run_apply("conference/login-auth", tmp_path / "missing.yaml", proj)
        assert result.returncode == 2


# ---------- A+B: auto-advance policy ----------
#
# session.auto_advance_policy (root-level) controls what apply.py does
# AFTER recording pass:
#
#     pause_each (or unset)  → state stays at apply_passed; AI must wait
#                              for the user before calling mark_user_confirmed.
#                              This is the original behaviour.
#     pause_on_failure       → apply pass auto-advances mark_user_confirmed,
#                              landing on the next slice's not_started. apply
#                              fail / partial(warning) still pauses.
#     pause_at_end           → same as pause_on_failure (reserved for future).
#
# The motivation: forcing the user to type "继续" between every slice was the
# loud half of the protection. The quiet half — apply.py itself running real
# grep + advancing state — survives. AI still cannot skip apply, fake
# evidence, or batch-write multiple slices.


def _set_policy(session_path: Path, policy: str) -> None:
    """Write auto_advance_policy at session root (matches the project's flat schema)."""
    data = yaml.safe_load(session_path.read_text())
    data["auto_advance_policy"] = policy
    session_path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True))


class TestAutoAdvanceOnPass:
    def test_pause_on_failure_pass_advances_to_next_slice(
        self, session_factory, project_factory
    ):
        path = session_factory()
        proj = project_factory()
        (proj / "src" / "views").mkdir(parents=True, exist_ok=True)
        (proj / "src" / "views" / "MeetingRoom.vue").write_text(_PASSING_VUE)

        _seed_to_code_written(path)
        _set_policy(path, "pause_on_failure")

        result = _run_apply("conference/login-auth", path, proj)
        assert result.returncode == 0, result.stderr

        idx, sid, state = state_machine.current_slice(path)
        assert idx == 1
        assert sid == "conference/room-lifecycle"
        assert state == "not_started"

    def test_pause_each_pass_stays_at_apply_passed(
        self, session_factory, project_factory
    ):
        """Original behaviour preserved when policy is pause_each."""
        path = session_factory()
        proj = project_factory()
        (proj / "src" / "views").mkdir(parents=True, exist_ok=True)
        (proj / "src" / "views" / "MeetingRoom.vue").write_text(_PASSING_VUE)

        _seed_to_code_written(path)
        _set_policy(path, "pause_each")

        result = _run_apply("conference/login-auth", path, proj)
        assert result.returncode == 0
        _, _, state = state_machine.current_slice(path)
        assert state == "apply_passed"

    def test_unset_policy_defaults_to_pause_each(
        self, session_factory, project_factory
    ):
        """Backward-compat: sessions without the field keep the old behaviour."""
        path = session_factory()
        proj = project_factory()
        (proj / "src" / "views").mkdir(parents=True, exist_ok=True)
        (proj / "src" / "views" / "MeetingRoom.vue").write_text(_PASSING_VUE)

        _seed_to_code_written(path)
        # No _set_policy call.

        result = _run_apply("conference/login-auth", path, proj)
        assert result.returncode == 0
        _, _, state = state_machine.current_slice(path)
        assert state == "apply_passed"

    def test_pause_at_end_behaves_like_pause_on_failure(
        self, session_factory, project_factory
    ):
        """Reserved value: same behaviour as pause_on_failure for now."""
        path = session_factory()
        proj = project_factory()
        (proj / "src" / "views").mkdir(parents=True, exist_ok=True)
        (proj / "src" / "views" / "MeetingRoom.vue").write_text(_PASSING_VUE)

        _seed_to_code_written(path)
        _set_policy(path, "pause_at_end")

        result = _run_apply("conference/login-auth", path, proj)
        assert result.returncode == 0
        _, _, state = state_machine.current_slice(path)
        assert state == "not_started"

    def test_unknown_policy_is_safe_pause_each(
        self, session_factory, project_factory
    ):
        """An unrecognised policy value must not auto-advance — fail closed."""
        path = session_factory()
        proj = project_factory()
        (proj / "src" / "views").mkdir(parents=True, exist_ok=True)
        (proj / "src" / "views" / "MeetingRoom.vue").write_text(_PASSING_VUE)

        _seed_to_code_written(path)
        _set_policy(path, "yolo_mode")

        result = _run_apply("conference/login-auth", path, proj)
        assert result.returncode == 0
        _, _, state = state_machine.current_slice(path)
        assert state == "apply_passed", "unknown policy must not auto-advance"


class TestAutoAdvanceOnFailure:
    def test_pause_on_failure_apply_fail_still_pauses(
        self, session_factory, project_factory
    ):
        path = session_factory()
        proj = project_factory()
        (proj / "src" / "views").mkdir(parents=True, exist_ok=True)
        (proj / "src" / "views" / "MeetingRoom.vue").write_text(_PARTIAL_VUE)

        _seed_to_code_written(path)
        _set_policy(path, "pause_on_failure")

        result = _run_apply("conference/login-auth", path, proj)
        assert result.returncode == 1

        idx, sid, state = state_machine.current_slice(path)
        # Cursor stays on this slice; state is apply_failed; AI must regenerate.
        assert idx == 0
        assert sid == "conference/login-auth"
        assert state == "apply_failed"


class TestAutoAdvanceLastSlice:
    def test_last_slice_auto_advance_lands_on_all_done(
        self, session_factory, project_factory
    ):
        path = session_factory(confirmed_plan=["conference/login-auth"])
        proj = project_factory()
        (proj / "src" / "views").mkdir(parents=True, exist_ok=True)
        (proj / "src" / "views" / "MeetingRoom.vue").write_text(_PASSING_VUE)

        _seed_to_code_written(path)
        _set_policy(path, "pause_on_failure")

        result = _run_apply("conference/login-auth", path, proj)
        assert result.returncode == 0
        idx, sid, state = state_machine.current_slice(path)
        assert state == "all_done"
