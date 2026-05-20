"""Slice-loop state machine for the topic skill.

The state machine is the *enforcement mechanism* that prevents the AI from
batch-reading slices, batch-generating code, or skipping `apply`. It lives
on disk in `.trtc-session.yaml` so PreToolUse / Stop hooks can read the same
state the topic skill is driving.

Public API:
    init_queue(session_path)
    current_slice(session_path) -> (index, slice_id, state)
    advance(session_path, transition) -> new_state
    status(session_path) -> dict           # convenience for CLIs

State diagram (one slice's lifecycle):

    not_started ──mark_slice_read──▶ slice_read
                                        │
                                        ▼
                                    code_written ──mark_apply_failed──▶ apply_failed
                                        │                                   │
                                        │                            mark_code_written
                                        ▼                                   │
                                    apply_passed ◀──────────────────────────┘
                                        │
                              mark_user_confirmed
                                        │
                                        ▼
                          (index += 1, state = not_started)
                                        │
                              (or all_done if last slice)

Any transition not covered by the diagram above raises RuntimeError.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple

import yaml

# --- transition table -------------------------------------------------------

# Each entry: (current_state, transition) -> next_state.
# The special value "ADVANCE_INDEX" means: bump current_slice_index, set the
# new state to "not_started" (or "all_done" if we walked off the end).
_TRANSITIONS = {
    ("not_started", "mark_slice_read"): "slice_read",
    ("slice_read", "mark_code_written"): "code_written",
    ("code_written", "mark_apply_passed"): "apply_passed",
    ("code_written", "mark_apply_failed"): "apply_failed",
    ("apply_failed", "mark_code_written"): "code_written",
    ("apply_passed", "mark_user_confirmed"): "ADVANCE_INDEX",
}

_KNOWN_TRANSITIONS = {t for (_state, t) in _TRANSITIONS.keys()}


# --- yaml IO ----------------------------------------------------------------

def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text()) or {}


def _save(path: Path, data: dict) -> None:
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True))


# --- init_queue -------------------------------------------------------------

def init_queue(session_path) -> None:
    """Materialise `confirmed_plan` into a `slice_queue` cursor on disk.

    Idempotent when the plan matches what's already installed; refuses to
    re-init if the user (or another tool) has changed `confirmed_plan` —
    the queue is frozen once topic owns the loop.
    """
    path = Path(session_path)
    data = _load(path)
    plan = data.get("confirmed_plan")
    if not plan:
        raise RuntimeError(
            "confirmed_plan is missing or empty in session — onboarding A2 "
            "should have populated it before topic ran init_queue."
        )

    expected_ids = list(plan)

    existing_queue = data.get("slice_queue")
    if existing_queue is not None:
        existing_ids = [entry.get("id") for entry in existing_queue]
        if existing_ids != expected_ids:
            raise RuntimeError(
                "slice_queue is frozen and differs from confirmed_plan — "
                "the queue cannot be re-initialised mid-flight. To reset, "
                "remove slice_queue / current_slice_index / current_slice_state "
                "from the session file and run init again."
            )
        # Same plan — leave the cursor where it is. Idempotent.
        return

    data["slice_queue"] = [{"id": sid, "status": "pending"} for sid in expected_ids]
    data["current_slice_index"] = 0
    data["current_slice_state"] = "not_started"
    _save(path, data)


# --- current_slice ----------------------------------------------------------

def current_slice(session_path) -> Tuple[Optional[int], Optional[str], Optional[str]]:
    """Return ``(index, slice_id, state)`` for the cursor.

    ``(None, None, None)`` when:
      - the session file does not exist
      - the session file exists but has no slice_queue (topic flow not active)

    Hooks rely on the all-None return to detect "not in topic flow" and
    fall through silently.
    """
    path = Path(session_path)
    if not path.exists():
        return (None, None, None)

    data = _load(path)
    queue = data.get("slice_queue")
    if not queue:
        return (None, None, None)

    state = data.get("current_slice_state")
    idx = data.get("current_slice_index")

    if state == "all_done":
        # Cursor walked past the end. Report no current slice but a state
        # callers can recognise.
        return (idx, None, "all_done")

    if idx is None or idx >= len(queue):
        return (None, None, None)

    return (idx, queue[idx]["id"], state)


# --- advance ----------------------------------------------------------------

def advance(session_path, transition: str) -> str:
    """Apply a transition; return the new state.

    Raises ``RuntimeError`` for any illegal (state, transition) pair, for
    unknown transition names, and for transitions when the queue is not
    initialised or already exhausted.
    """
    if transition not in _KNOWN_TRANSITIONS:
        raise RuntimeError(
            f"unknown transition '{transition}'. Known transitions: "
            f"{sorted(_KNOWN_TRANSITIONS)}"
        )

    path = Path(session_path)
    data = _load(path)
    queue = data.get("slice_queue")
    if not queue:
        raise RuntimeError(
            "slice_queue not initialised — call init_queue() before advance()."
        )

    state = data.get("current_slice_state")
    idx = data.get("current_slice_index", 0)

    if state == "all_done":
        raise RuntimeError(
            "all_done — the slice queue is finished; no further transitions "
            "are allowed. Start a new scenario or reset the session."
        )

    next_state = _TRANSITIONS.get((state, transition))
    if next_state is None:
        raise RuntimeError(
            f"illegal transition '{transition}' from state '{state}'. "
            f"Allowed from '{state}': "
            f"{sorted(t for (s, t) in _TRANSITIONS.keys() if s == state)}"
        )

    if next_state == "ADVANCE_INDEX":
        # Mark the just-confirmed slice as done. Drop its apply-evidence
        # JSON: a clean integration leaves the evidence directory empty.
        # Failed evidence stays (we never reach this branch on apply_failed).
        confirmed_id = queue[idx]["id"]
        queue[idx]["status"] = "done"
        ev_path = (
            path.parent / ".trtc-apply-evidence"
            / (confirmed_id.replace("/", "__") + ".json")
        )
        try:
            ev_path.unlink()
        except FileNotFoundError:
            pass

        new_idx = idx + 1
        if new_idx >= len(queue):
            data["current_slice_index"] = new_idx
            data["current_slice_state"] = "all_done"
            _save(path, data)
            return "all_done"
        data["current_slice_index"] = new_idx
        data["current_slice_state"] = "not_started"
        _save(path, data)
        return "not_started"

    data["current_slice_state"] = next_state
    _save(path, data)
    return next_state


# --- status (convenience for CLI display) -----------------------------------

def status(session_path) -> dict:
    """Return a small dict the CLI can pretty-print."""
    path = Path(session_path)
    if not path.exists():
        return {"initialised": False, "reason": "session file missing"}
    data = _load(path)
    queue = data.get("slice_queue")
    if not queue:
        return {"initialised": False, "reason": "slice_queue not set"}
    idx = data.get("current_slice_index", 0)
    state = data.get("current_slice_state")
    return {
        "initialised": True,
        "index": idx,
        "state": state,
        "total": len(queue),
        "current_slice_id": queue[idx]["id"] if idx < len(queue) else None,
        "queue": queue,
    }
