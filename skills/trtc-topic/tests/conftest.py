"""pytest fixtures for the topic state-machine and gate hooks.

These fixtures only know about session files and a simulated project root.
They never touch the real repo session.
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml


# Default confirmed_plan used by most tests — mirrors the general-conference
# minimal scope (P0).
DEFAULT_CONFIRMED_PLAN = [
    "conference/login-auth",
    "conference/room-lifecycle",
    "conference/participant-list",
    "conference/video-layout",
    "conference/device-control",
    "conference/network-quality",
]


@pytest.fixture
def session_factory(tmp_path: Path):
    """Factory that writes a `.trtc-session.yaml` into tmp_path.

    Returns a callable: ``make_session(**overrides) -> Path``.
    Defaults are picked to match a typical mid-integration general-conference/web
    session so individual tests only override what they care about.
    """

    def _make(**overrides) -> Path:
        base = {
            "schema_version": 1,
            "status": "active",
            "product": "conference",
            "platform": "web",
            "intent": "integrate-scenario",
            "scenario": "general-conference",
            "ui_mode": None,
            "current_step": "topic-handoff",
            "confirmed_plan": list(DEFAULT_CONFIRMED_PLAN),
            "completed_steps": [],
            "project_state": {
                "project_root": str(tmp_path / "user-project"),
            },
        }
        base.update(overrides)
        path = tmp_path / ".trtc-session.yaml"
        path.write_text(yaml.safe_dump(base, sort_keys=False, allow_unicode=True))
        return path

    return _make


@pytest.fixture
def project_factory(tmp_path: Path):
    """Factory that creates an empty user project skeleton at tmp_path/user-project.

    Returns the project root Path. Tests can write whatever Vue/TS files they
    need into it.
    """

    def _make() -> Path:
        root = tmp_path / "user-project"
        (root / "src").mkdir(parents=True, exist_ok=True)
        return root

    return _make
