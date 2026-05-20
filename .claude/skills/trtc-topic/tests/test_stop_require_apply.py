"""Tests for stop_require_apply_evidence.py — Stop hook.

Stop hook runs when the AI's turn ends. We use it to refuse to end on
states that mean "code was written but not validated":

    code_written  → exit 2 (block) — apply.py never ran
    apply_failed  → exit 2 (block) — apply rejected the code, AI must regenerate

Other states pass:
    not_started, slice_read, apply_passed, all_done, queue-not-initialised,
    session-missing.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

GUARDRAILS_DIR = Path(__file__).resolve().parents[1] / "guardrails"
STOP_SCRIPT = GUARDRAILS_DIR / "stop_require_apply_evidence.py"

STATE_MACHINE_DIR = Path(__file__).resolve().parents[1] / "scripts" / "lib"
sys.path.insert(0, str(STATE_MACHINE_DIR))
import state_machine  # noqa: E402
sys.path.pop(0)


def _run(session_path: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(STOP_SCRIPT)],
        text=True,
        capture_output=True,
        env={"TRTC_SESSION_PATH": str(session_path), "PATH": "/usr/bin:/bin"},
    )


class TestStopHook:
    def test_allows_when_session_missing(self, tmp_path):
        result = _run(tmp_path / "missing.yaml")
        assert result.returncode == 0

    def test_allows_when_queue_not_initialised(self, session_factory):
        path = session_factory()
        result = _run(path)
        assert result.returncode == 0

    def test_allows_in_not_started(self, session_factory):
        path = session_factory()
        state_machine.init_queue(path)
        result = _run(path)
        assert result.returncode == 0

    def test_allows_in_slice_read(self, session_factory):
        path = session_factory()
        state_machine.init_queue(path)
        state_machine.advance(path, "mark_slice_read")
        result = _run(path)
        assert result.returncode == 0

    def test_blocks_in_code_written(self, session_factory):
        path = session_factory()
        state_machine.init_queue(path)
        state_machine.advance(path, "mark_slice_read")
        state_machine.advance(path, "mark_code_written")
        result = _run(path)
        assert result.returncode == 2
        # Helpful error mentions apply.py and slice id
        assert "apply" in result.stderr.lower()
        assert "login-auth" in result.stderr

    def test_blocks_in_apply_failed(self, session_factory):
        path = session_factory()
        state_machine.init_queue(path)
        state_machine.advance(path, "mark_slice_read")
        state_machine.advance(path, "mark_code_written")
        state_machine.advance(path, "mark_apply_failed")
        result = _run(path)
        assert result.returncode == 2
        assert "apply_failed" in result.stderr or "regenerate" in result.stderr.lower()

    def test_allows_in_apply_passed(self, session_factory):
        path = session_factory()
        state_machine.init_queue(path)
        state_machine.advance(path, "mark_slice_read")
        state_machine.advance(path, "mark_code_written")
        state_machine.advance(path, "mark_apply_passed")
        result = _run(path)
        assert result.returncode == 0

    def test_allows_in_all_done(self, session_factory):
        path = session_factory(confirmed_plan=["conference/login-auth"])
        state_machine.init_queue(path)
        state_machine.advance(path, "mark_slice_read")
        state_machine.advance(path, "mark_code_written")
        state_machine.advance(path, "mark_apply_passed")
        state_machine.advance(path, "mark_user_confirmed")
        # Now in all_done
        result = _run(path)
        assert result.returncode == 0
