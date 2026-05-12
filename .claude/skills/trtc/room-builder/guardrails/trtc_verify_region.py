#!/usr/bin/env python3
"""trtc_verify_region.py — Per-component region fidelity check.

PostToolUse:Write hook that ensures a generated .vue component preserves
the structural elements from its corresponding region HTML fragment.

When ui_mode=full-ui, components should be generated via paste-then-bind
from region HTML. This hook catches cases where the AI skips paste and
writes templates from memory, causing structural loss (buttons, popovers,
menu items disappear).

Exit codes:
  0 — pass (or not applicable: wrong file, gates closed, no region mapping)
  2 — fail (structural elements missing from the written .vue file)

Designed to run alongside trtc_verify_ui.py (V4/V5) in verify_ui_post_write.sh.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.session_state import (
    find_session_for_file,
    in_scope as _session_in_scope,
    scaffold_complete as _session_scaffold_complete,
    scaffold_in_progress as _session_scaffold_in_progress,
)
from lib.region_fingerprint import extract_fingerprints, check_fidelity

import yaml

REPO_ROOT = Path(__file__).resolve().parents[5]
REGIONS_BASE = Path(__file__).resolve().parent.parent / "references" / "regions"
MANIFEST_PATH = Path(__file__).resolve().parent.parent / "references" / "region-manifest.yaml"

# Component filename → region filename mapping (case-insensitive stem match)
COMPONENT_TO_REGION = {
    'topbar': 'topbar.html',
    'bottombar': 'bottombar.html',
    'stage': 'stage.html',
    'sidepanel': 'sidepanel.html',
    'modals': 'modals.html',
}


def _resolve_region_path(vue_path: Path, session: dict) -> Path | None:
    """Map a .vue file to its corresponding region HTML fragment.

    Returns the region file Path, or None if no mapping exists.
    """
    stem = vue_path.stem.lower()  # e.g. "TopBar" → "topbar"

    region_filename = COMPONENT_TO_REGION.get(stem)
    if not region_filename:
        return None

    # Determine theme from session scenario via manifest
    scenario = session.get("scenario")
    if not scenario:
        return None

    if not MANIFEST_PATH.exists():
        return None

    manifest = yaml.safe_load(MANIFEST_PATH.read_text())
    if not manifest:
        return None

    # Find the theme entry that covers this scenario
    for theme_key, theme_data in manifest.items():
        if not isinstance(theme_data, dict):
            continue
        scenarios = theme_data.get("scenarios", [])
        if scenario in scenarios:
            base_path = theme_data.get("base_path", "")
            region_path = REGIONS_BASE.parent / base_path / region_filename
            if region_path.exists():
                return region_path

    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True, help="Path to the .vue file being written")
    args = parser.parse_args()

    vue_path = Path(args.file)

    # Only .vue files
    if not vue_path.exists() or vue_path.suffix != ".vue":
        return 0

    # Find session for this file
    session, _ = find_session_for_file(args.file)
    if session is None:
        return 0  # No session — not our file

    # Gate: lifecycle complete → user owns code, don't check
    if _session_scaffold_complete(session):
        return 0

    # Gate: mid-integration → don't block step-by-step building
    if _session_scaffold_in_progress(session):
        return 0

    # Gate: scope check (ui_mode=full-ui, conference, integrate-scenario)
    if not _session_in_scope(session, REPO_ROOT):
        return 0

    # Resolve region file for this component
    region_path = _resolve_region_path(vue_path, session)
    if region_path is None:
        return 0  # No region mapping — not a region-backed component, skip

    # Extract fingerprints from region HTML
    fingerprints = extract_fingerprints(region_path)

    # Read the .vue file content
    try:
        vue_content = vue_path.read_text()
    except (UnicodeDecodeError, PermissionError):
        return 0

    # Check fidelity
    violations = check_fidelity(vue_content, fingerprints)

    if violations:
        component_name = vue_path.stem
        header = (
            f"V7: {component_name}.vue region fidelity check failed against "
            f"{region_path.name}. The following structural elements are missing:"
        )
        print(header, file=sys.stderr)
        for v in violations:
            print(f"  {v}", file=sys.stderr)
        print(
            f"\nFix: Read the region file at .claude/skills/trtc/room-builder/references/"
            f"regions/meeting-classic/{region_path.name} and paste its structure verbatim "
            f"before adding Vue bindings.",
            file=sys.stderr,
        )
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
