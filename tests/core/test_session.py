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
    assert session.created_at
    assert session.updated_at


def test_session_save_load():
    """Test saving and loading session."""
    session = Session(name="Test Session")
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "session.json"
        session.save(path)
        loaded = Session.load(path)
        assert loaded.id == session.id
        assert loaded.name == session.name


def test_session_context_manager():
    """Test session as context manager."""
    session = Session()
    with session as s:
        assert s is session


def test_session_run_quick_triage():
    """Test running quick_triage workflow through session."""
    from pathlib import Path

    from oroitz.core.workflow import seed_workflows

    # Seed workflows
    seed_workflows()

    # Create session with image and profile
    session = Session(name="Test Session", image_path=Path("/fake/image.dmp"))

    # Run quick_triage
    result = session.run("quick_triage")

    # Verify result
    assert result is not None
    assert len(result.processes) == 2  # Mock data
    assert len(result.network_connections) == 1
    assert len(result.malfind_hits) == 1

    # Check specific data
    assert result.processes[0].pid == 4
    assert result.processes[0].name == "System"
    assert result.network_connections[0].state == "ESTABLISHED"
    assert result.malfind_hits[0].process_name == "suspicious.exe"


def test_session_run_with_caching():
    """Test session run with caching integration."""
    from pathlib import Path

    from oroitz.core.workflow import seed_workflows

    # Seed workflows
    seed_workflows()

    # Create session with image and profile
    session = Session(name="Test Session", image_path=Path("/fake/image.dmp"))

    # Run quick_triage twice
    result1 = session.run("quick_triage")
    result2 = session.run("quick_triage")

    # Both should succeed and be identical
    assert result1 is not None
    assert result2 is not None
    assert result1.processes == result2.processes
    assert result1.network_connections == result2.network_connections
    assert result1.malfind_hits == result2.malfind_hits
