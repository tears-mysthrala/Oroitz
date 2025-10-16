"""Tests for the PySide6 GUI application."""

import pytest
from unittest.mock import MagicMock

from oroitz.core.session import SessionManager
from oroitz.ui.gui.landing_view import LandingView
from oroitz.ui.gui.main_window import MainWindow
from oroitz.ui.gui.session_dashboard import SessionDashboard
from oroitz.ui.gui.session_wizard import SessionWizard


def test_main_window_creation():
    """Test that MainWindow can be created."""
    # Mock QApplication to avoid GUI initialization in tests
    with pytest.MonkeyPatch().context() as m:
        mock_app = MagicMock()
        m.setattr("oroitz.ui.gui.main_window.QApplication", lambda: mock_app)

        window = MainWindow()
        assert window is not None
        assert hasattr(window, 'landing_view')
        assert hasattr(window, 'session_wizard')
        assert hasattr(window, 'session_dashboard')


def test_landing_view_creation():
    """Test that LandingView can be created."""
    session_manager = SessionManager()
    view = LandingView(session_manager)
    assert view is not None
    assert hasattr(view, 'sessions_list')


def test_session_wizard_creation():
    """Test that SessionWizard can be created."""
    wizard = SessionWizard()
    assert wizard is not None
    assert wizard.page(0) is not None  # Should have at least one page


def test_session_dashboard_creation():
    """Test that SessionDashboard can be created."""
    dashboard = SessionDashboard()
    assert dashboard is not None
    assert hasattr(dashboard, 'progress_bar')
    assert hasattr(dashboard, 'logs_text')