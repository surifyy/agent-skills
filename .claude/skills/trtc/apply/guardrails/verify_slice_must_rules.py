#!/usr/bin/env python3
"""verify_slice_must_rules.py — PostToolUse hook for MUST-rule enforcement.

When a .vue or .ts file is written inside a project with an active
trtc-session, this script greps for MUST-rule markers from the relevant
slices. It does NOT replace apply — it's a lightweight first-pass that
catches the most egregious omissions (e.g. writing a meeting room without
useLoginState).

Exit codes:
  0 = pass (or not in scope)
  1 = fail — missing critical APIs

stderr on failure contains actionable messages naming the missing APIs
and which slice's MUST rules require them.
"""
import json
import re
import sys
from pathlib import Path

GUARDRAILS_DIR = Path(__file__).resolve().parent
ROOM_BUILDER_GUARDRAILS = GUARDRAILS_DIR.parents[1] / 'room-builder' / 'guardrails'

sys.path.insert(0, str(ROOM_BUILDER_GUARDRAILS))
from lib.session_state import load_session, find_session_for_file, project_root as _project_root, in_scope, scaffold_complete
sys.path.pop(0)

REPO_ROOT = Path(__file__).resolve().parents[5]
FALLBACK_SESSION_PATH = REPO_ROOT / ".trtc-session.yaml"

# Map: scenario → list of (slice_id, [required_patterns])
# These are the non-negotiable MUST rules from each slice's web platform file.
# Only include patterns that are ALWAYS required (not conditional).
GENERAL_MEETING_MUST_RULES = {
    "conference/login-auth": [
        r"login\(\s*\{",       # The actual login() call with config object
        r"setSelfInfo\(",
    ],
    "conference/room-lifecycle": [
        r"useRoomState",
        r"(createAndJoinRoom|joinRoom)\(",
        r"(leaveRoom|endRoom)\(",
    ],
    "conference/device-control": [
        r"useDeviceState",
        r"(openLocalCamera|closeLocalCamera)\(",
        r"(muteMicrophone|unmuteMicrophone)\(",
    ],
    "conference/participant-list": [
        r"useRoomParticipantState",
        r"participantList",
    ],
    "conference/video-layout": [
        r"RoomView",
        r"RoomLayoutTemplate",
    ],
    "conference/network-quality": [
        r"networkInfo",
        r"NetworkQuality",
    ],
    "conference/room-chat": [
        r"setActiveConversation\(",
        r"GROUP",
        r"useMessageListState",
        r"updateRawValue\(",
    ],
    "conference/screen-share": [
        r"startScreenShare\(",
        r"stopScreenShare\(",
    ],
}

SCENARIO_RULES = {
    "general-meeting": GENERAL_MEETING_MUST_RULES,
}


def check_must_rules(file_content: str, rules: dict) -> list:
    """Check file content against MUST rules. Return list of violations."""
    violations = []
    for slice_id, patterns in rules.items():
        for pattern in patterns:
            if not re.search(pattern, file_content):
                violations.append((slice_id, pattern))
    return violations


def main():
    # Read hook stdin
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        return 0

    file_path = data.get("tool_input", {}).get("file_path", "")
    if not file_path:
        return 0

    # Only check .vue files that look like meeting room components
    path = Path(file_path)
    if path.suffix not in (".vue", ".ts"):
        return 0

    # Skip small utility files (< 50 lines likely aren't the main room component)
    if not path.exists():
        return 0
    content = path.read_text()
    if content.count("\n") < 50:
        return 0

    # Load session — walk up from the written file to find the owning session
    session, _ = find_session_for_file(file_path, fallback_path=FALLBACK_SESSION_PATH)
    if session is None:
        return 0
    if scaffold_complete(session):
        return 0
    if not in_scope(session, REPO_ROOT):
        return 0

    scenario_id = session.get("scenario")
    if scenario_id not in SCENARIO_RULES:
        return 0

    # Only run full MUST-rule check on the "main" room component
    # Heuristic: file has > 100 lines and imports from tuikit-atomicx-vue3
    if "tuikit-atomicx-vue3" not in content:
        return 0
    if content.count("\n") < 100:
        return 0

    rules = SCENARIO_RULES[scenario_id]

    # Only check rules for slices whose composables are actually imported in this file.
    # This avoids false positives when responsibilities are split across files
    # (e.g. login in LoginView.vue, room logic in MeetingRoom.vue).
    relevant_rules = {}
    for slice_id, patterns in rules.items():
        # Check if the file imports/uses the primary composable of this slice
        primary_marker = patterns[0]  # First pattern is always the main import
        if re.search(primary_marker, content):
            relevant_rules[slice_id] = patterns

    if not relevant_rules:
        # File doesn't import any TRTC composables we track → skip
        return 0

    violations = check_must_rules(content, relevant_rules)

    if not violations:
        return 0

    # Report violations
    print(
        f"MUST-rule check failed for {file_path}:",
        file=sys.stderr,
    )
    for slice_id, pattern in violations:
        print(
            f"  - [{slice_id}] missing pattern: {pattern}",
            file=sys.stderr,
        )
    print(
        f"\nCheck the slice files at knowledge-base/slices/conference/web/ "
        f"for the correct API usage.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
