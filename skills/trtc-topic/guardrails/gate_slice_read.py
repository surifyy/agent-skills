#!/usr/bin/env python3
"""gate_slice_read.py — PreToolUse hook: block out-of-bounds slice reads.

Wired into ``.claude/settings.json`` under ``PreToolUse`` with matcher
``Read``. The contract:

* stdin is a JSON object: ``{"tool_name": "Read", "tool_input": {"file_path": "..."}}``
* exit 0 — allow the call (out of scope, or in bounds)
* exit 2 — block; stderr explains what the AI must do instead

Out-of-scope cases (silent allow):
    * tool_name != "Read"
    * file_path doesn't look like a slice file
      (under ``knowledge-base/slices/.../*.md``)
    * session file is missing
    * slice_queue not initialised (topic flow not active)

In-scope: file_path matches ``knowledge-base/slices/{product}/[{platform}/]{slice}.md``.
We block unless ``{product}/{slice}`` matches the cursor's current slice id.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STATE_MACHINE_DIR = HERE.parent / "scripts" / "lib"
sys.path.insert(0, str(STATE_MACHINE_DIR))
import state_machine  # noqa: E402
sys.path.pop(0)


# Match "knowledge-base/slices/{product}/{ability}.md" or
# "knowledge-base/slices/{product}/{platform}/{ability}.md".
# We accept it appearing anywhere in the path (relative or absolute).
_SLICE_PATH_RE = re.compile(
    r"knowledge-base/slices/(?P<product>[^/]+)"
    r"(?:/(?P<platform>web|android|ios|flutter|electron|unity))?"
    r"/(?P<ability>[^/]+)\.md$"
)


def _resolve_session_path() -> Path:
    """Pick the session file: env var first, then $CLAUDE_PROJECT_DIR/.trtc-session.yaml."""
    explicit = os.environ.get("TRTC_SESSION_PATH")
    if explicit:
        return Path(explicit)
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR")
    if project_dir:
        return Path(project_dir) / ".trtc-session.yaml"
    return Path.cwd() / ".trtc-session.yaml"


def _parse_payload() -> dict:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def _slice_id_from_path(file_path: str) -> str | None:
    """Extract '{product}/{ability}' from a slice file path; None if not a slice."""
    m = _SLICE_PATH_RE.search(file_path.replace("\\", "/"))
    if not m:
        return None
    return f"{m.group('product')}/{m.group('ability')}"


def main() -> int:
    payload = _parse_payload()
    if payload.get("tool_name") != "Read":
        return 0

    file_path = (payload.get("tool_input") or {}).get("file_path") or ""
    requested_slice = _slice_id_from_path(file_path)
    if requested_slice is None:
        # Not a slice file — out of this gate's domain.
        return 0

    session_path = _resolve_session_path()
    if not session_path.exists():
        return 0

    idx, current_id, state = state_machine.current_slice(session_path)
    if current_id is None and state != "all_done":
        # Topic flow not active.
        return 0

    if state == "all_done":
        # Topic finished; user owns the code now. Don't gate further reads.
        return 0

    if requested_slice == current_id:
        return 0

    sys.stderr.write(
        f"[topic gate] Read blocked: '{requested_slice}' is not the current slice.\n"
        f"Current slice is [{idx}] '{current_id}' (state: {state}).\n"
        f"Finish it first — generate code, run apply, and get user confirmation —\n"
        f"before reading any other slice from the queue.\n"
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
