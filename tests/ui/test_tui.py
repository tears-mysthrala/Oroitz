"""Tests for TUI components."""

import pytest

from oroitz.ui.tui import OroitzTUI
from oroitz.core.workflow import seed_workflows


def test_tui_creation():
    """Test TUI can be created."""
    seed_workflows()
    app = OroitzTUI()
    assert app is not None
    assert app.session is None


def test_tui_session_management():
    """Test session management."""
    seed_workflows()
    app = OroitzTUI()

    # Test setting session
    from oroitz.core.session import Session
    session = Session(image_path="/test.img", profile="windows")
    app.set_current_session(session)
    assert app.get_current_session() == session

    # Test clearing session
    app.set_current_session(None)
    assert app.get_current_session() is None