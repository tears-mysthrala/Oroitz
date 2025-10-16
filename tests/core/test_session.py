"""Tests for session module."""

import tempfile
from pathlib import Path

from oroitz.core.session import Session


def test_session_creation():
    """Test session creation with defaults."""
    session = Session()
    assert session.id
    assert session.name == "Untitled Session"
    assert session.image_path is None
    assert session.profile is None
    assert session.created_at
    assert session.updated_at


def test_session_save_load():
    """Test saving and loading session."""
    session = Session(name="Test Session", profile="Win10x64")
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "session.json"
        session.save(path)
        loaded = Session.load(path)
        assert loaded.id == session.id
        assert loaded.name == session.name
        assert loaded.profile == session.profile


def test_session_context_manager():
    """Test session as context manager."""
    session = Session()
    with session as s:
        assert s is session