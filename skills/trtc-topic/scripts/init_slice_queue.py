#!/usr/bin/env python3
"""init_slice_queue.py — Topic-skill CLI: materialise slice_queue from session.

Usage:
    python3 init_slice_queue.py                 # auto-resolves session path
    python3 init_slice_queue.py --session PATH  # explicit override

Session path resolution (in order):
    1. --session flag, if given
    2. $TRTC_SESSION_PATH env var
    3. $CLAUDE_PROJECT_DIR/.trtc-session.yaml (Claude Code sets this to the
       user project root)
    4. ./.trtc-session.yaml (cwd fallback — useful when AI runs Bash from
       the user project root)

Reads ``confirmed_plan`` from the session and writes:
    slice_queue, current_slice_index=0, current_slice_state=not_started

Idempotent. Refuses to re-init if the plan has changed (queue is frozen).

Exit codes:
    0 — success (queue written or already up to date)
    1 — confirmed_plan missing/empty, or plan diverged from existing queue
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "lib"))
import state_machine  # noqa: E402


def _resolve_session_path() -> Path:
    """Match the resolver used by guardrails/gate_*.py:
    env var → $CLAUDE_PROJECT_DIR → cwd. The session file lives in the
    user project, never in the skill repo, so we never look at HERE.parents.
    """
    explicit = os.environ.get("TRTC_SESSION_PATH")
    if explicit:
        return Path(explicit)
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR")
    if project_dir:
        return Path(project_dir) / ".trtc-session.yaml"
    return Path.cwd() / ".trtc-session.yaml"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--session",
        type=Path,
        default=None,
        help="explicit path to .trtc-session.yaml (overrides env-based resolver)",
    )
    args = parser.parse_args(argv)

    session_path = args.session if args.session is not None else _resolve_session_path()

    if not session_path.exists():
        print(
            f"error: session file not found at {session_path}\n"
            f"  hint: cd to the user project root, or set $CLAUDE_PROJECT_DIR / "
            f"$TRTC_SESSION_PATH before running this script.",
            file=sys.stderr,
        )
        return 1

    try:
        state_machine.init_queue(session_path)
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    st = state_machine.status(session_path)
    print(
        f"queue initialised — {st['total']} slices, "
        f"cursor at [{st['index']}] {st['current_slice_id']} ({st['state']})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
