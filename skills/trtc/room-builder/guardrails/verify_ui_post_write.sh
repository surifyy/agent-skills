#!/usr/bin/env bash
# verify_ui_post_write.sh — PostToolUse(Write|Edit) hook glue.
#
# Reads Claude Code's hook stdin JSON, extracts tool_input.file_path,
# and runs two verifiers:
#   1. trtc_verify_ui.py --file (V4/V5: class counts, structure abuse)
#   2. trtc_verify_region.py --file (V7: region fidelity check)
#
# If either fails (exit 2), the overall hook fails.
# Exit code is 0 (pass) or 2 (fail with stderr messages).
set -euo pipefail

GUARDRAILS_DIR="$(cd "$(dirname "$0")" && pwd)"

# Resolve session path: CLAUDE_PROJECT_DIR is set by Claude Code hooks runtime.
# Fall back to the guardrails dir's ancestor (4 levels up = repo root).
if [[ -n "${CLAUDE_PROJECT_DIR:-}" ]]; then
    SESSION_PATH="${CLAUDE_PROJECT_DIR}/.trtc-session.yaml"
else
    SESSION_PATH="$(cd "$GUARDRAILS_DIR/../../../../.." && pwd)/.trtc-session.yaml"
fi

# Hook stdin is JSON: { tool_input: { file_path: "..." }, ... }
# Use Python to parse — avoids hard dependency on jq.
FILE_PATH=$(python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('tool_input', {}).get('file_path', ''))
except:
    print('')
" 2>/dev/null || echo "")

if [[ -z "$FILE_PATH" ]]; then
    # No file_path → not an Edit/Write we can verify. Don't block.
    exit 0
fi

# Only .vue files are subject to per-file enforcement.
case "$FILE_PATH" in
    *.vue) ;;
    *) exit 0 ;;
esac

# Run V4/V5 check first (pass session path explicitly)
python3 "$GUARDRAILS_DIR/trtc_verify_ui.py" --file "$FILE_PATH" --session-path "$SESSION_PATH"
UI_EXIT=$?

if [[ $UI_EXIT -ne 0 ]]; then
    exit $UI_EXIT
fi

# Run V7 region fidelity check (pass session path as fallback)
exec python3 "$GUARDRAILS_DIR/trtc_verify_region.py" --file "$FILE_PATH" --session-path "$SESSION_PATH"
