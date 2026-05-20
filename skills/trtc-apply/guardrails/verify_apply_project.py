#!/usr/bin/env python3
"""verify_apply_project.py — Stop hook for project-wide apply checks.

Runs P4 (MUST rules) and P5 (async patterns) across ALL .vue/.ts files
in the project src/ directory. This catches issues that PostToolUse misses
when files are written by Agent subprocesses (which bypass PostToolUse hooks).

Exit codes:
  0 = pass (or not in scope)
  1 = fail — critical MUST rules missing across project

Unlike the per-file preflight hook, this script:
- Scans ALL source files (not just the one being written)
- Aggregates MUST rule coverage project-wide (a rule satisfied in ANY file counts)
- Only reports rules that are missing from the ENTIRE project
"""
import json
import os
import re
import sys
from pathlib import Path

GUARDRAILS_DIR = Path(__file__).resolve().parent
PLUGIN_ROOT = Path(os.environ.get("CLAUDE_PLUGIN_ROOT", Path(__file__).resolve().parents[3]))
ROOM_BUILDER_GUARDRAILS = PLUGIN_ROOT / 'skills' / 'trtc-room-builder' / 'guardrails'

sys.path.insert(0, str(ROOM_BUILDER_GUARDRAILS))
from lib.session_state import (
    load_session,
    project_root as _session_project_root,
    in_scope as _session_in_scope,
    scaffold_complete as _session_scaffold_complete,
)
sys.path.pop(0)

sys.path.insert(0, str(GUARDRAILS_DIR))
from apply_lib.rule_parser import load_rules_for_product_platform, rules_for_file
sys.path.pop(0)

REPO_ROOT = Path(os.environ.get("CLAUDE_PLUGIN_ROOT", Path(__file__).resolve().parents[3]))
SESSION_PATH = Path(os.environ.get("CLAUDE_PROJECT_DIR", ".")) / '.trtc-session.yaml'


def main():
    # Gate checks
    session = load_session(SESSION_PATH)
    if session is None:
        return 0
    if _session_scaffold_complete(session):
        return 0
    if not _session_in_scope(session, REPO_ROOT):
        return 0

    project_root = _session_project_root(session)
    if project_root is None or not project_root.exists():
        return 0

    src_dir = project_root / 'src'
    if not src_dir.exists():
        return 0

    # Collect all source files
    source_files = list(src_dir.rglob('*.vue')) + list(src_dir.rglob('*.ts'))
    source_files = [f for f in source_files if 'node_modules' not in str(f)]

    if not source_files:
        return 0

    # Concatenate all file contents for project-wide rule checking
    combined_content = ''
    for f in source_files:
        try:
            combined_content += f.read_text(encoding='utf-8') + '\n'
        except (UnicodeDecodeError, PermissionError):
            continue

    if not combined_content:
        return 0

    # Skip if no SDK usage at all in project
    if 'tuikit-atomicx-vue3' not in combined_content:
        return 0

    product = session.get('product', 'conference')
    platform = session.get('platform', 'web')

    # Load ALL rules for this product/platform
    all_rules = load_rules_for_product_platform(REPO_ROOT, product, platform)
    if not all_rules:
        return 0

    # Check MUST rules project-wide: a rule is satisfied if ANY file contains the pattern
    missing_rules = []
    for rule in all_rules:
        if rule['type'] != 'MUST':
            continue
        if not rule['patterns']:
            continue

        meaningful = [p for p in rule['patterns'] if len(p) >= 8]
        if not meaningful:
            continue

        # Rule is satisfied if at least one meaningful pattern exists in combined content
        present = [p for p in meaningful if p in combined_content]
        if not present:
            missing_rules.append(rule)

    # Check async patterns across all .vue files
    async_issues = []
    async_funcs = [
        'login(', 'setSelfInfo(', 'createAndJoinRoom(', 'joinRoom(',
        'leaveRoom(', 'endRoom(', 'openLocalCamera(', 'closeLocalCamera(',
        'openLocalMicrophone(', 'muteMicrophone(', 'unmuteMicrophone(',
        'startScreenShare(', 'stopScreenShare(', 'sendMessage(',
        'getParticipantList(',
    ]
    for f in source_files:
        if f.suffix != '.vue':
            continue
        try:
            content = f.read_text(encoding='utf-8')
        except (UnicodeDecodeError, PermissionError):
            continue
        # Only check <script> section
        script_match = re.search(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
        if not script_match:
            continue
        script = script_match.group(1)
        lines = script.split('\n')
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('//') or stripped.startswith('*'):
                continue
            for func in async_funcs:
                if func in line and 'await' not in line and 'return' not in line:
                    if 'function' not in line and 'type' not in line and '=>' not in line:
                        rel_path = f.relative_to(project_root)
                        async_issues.append(f"  [{rel_path}:{i}] `{func.rstrip('(')}` called without await")
                        break

    # Report
    if not missing_rules and not async_issues:
        return 0

    print("", file=sys.stderr)
    print("=" * 70, file=sys.stderr)
    print("APPLY PROJECT CHECK FAILED (Stop)", file=sys.stderr)
    print("=" * 70, file=sys.stderr)
    print(f"  Project: {project_root}", file=sys.stderr)
    print("", file=sys.stderr)

    if missing_rules:
        print(f"MUST RULES MISSING ({len(missing_rules)}):", file=sys.stderr)
        print("  (These patterns are absent from ALL project source files)", file=sys.stderr)
        print("", file=sys.stderr)
        for rule in missing_rules[:10]:  # Cap output
            patterns_str = ', '.join(f'`{p}`' for p in rule['patterns'][:3] if len(p) >= 8)
            print(f"  ✗ [{rule['slice_id']}] {rule['text'][:70]}", file=sys.stderr)
            print(f"    Need one of: {patterns_str}", file=sys.stderr)
        if len(missing_rules) > 10:
            print(f"  ... and {len(missing_rules) - 10} more", file=sys.stderr)
        print("", file=sys.stderr)

    if async_issues:
        print(f"ASYNC ISSUES ({len(async_issues)}):", file=sys.stderr)
        for issue in async_issues[:5]:
            print(issue, file=sys.stderr)
        if len(async_issues) > 5:
            print(f"  ... and {len(async_issues) - 5} more", file=sys.stderr)
        print("", file=sys.stderr)

    print("─" * 70, file=sys.stderr)
    print("FIX: Check knowledge-base/slices/conference/web/ for required APIs.", file=sys.stderr)
    print("=" * 70, file=sys.stderr)

    return 1


if __name__ == '__main__':
    sys.exit(main())
