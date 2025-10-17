"""Tests for the PySide6 GUI application."""

from pathlib import Path
from unittest.mock import patch

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QComboBox, QLineEdit, QPushButton, QWizard

from oroitz.core.session import SessionManager
from oroitz.core.workflow import seed_workflows
from oroitz.ui.gui.landing_view import LandingView
from oroitz.ui.gui.main_window import MainWindow
from oroitz.ui.gui.session_dashboard import SessionDashboard
from oroitz.ui.gui.session_wizard import SessionWizard


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def main_window(qapp):
    """Create MainWindow instance for testing."""
    seed_workflows()
    window = MainWindow()
    yield window
    window.close()


@pytest.fixture
def session_manager():
    """Create SessionManager instance."""
    return SessionManager()


class TestMainWindow:
    """Test MainWindow functionality."""

    def test_initial_state(self, main_window):
        """Test initial state of main window."""
        assert main_window.windowTitle() == "Oroitz - Cross-platform Volatility 3 Wrapper"
        assert main_window.stacked_widget.currentWidget() == main_window.landing_view

    def test_show_landing_view(self, main_window):
        """Test showing landing view."""
        main_window.show_landing_view()
        assert main_window.stacked_widget.currentWidget() == main_window.landing_view

    def test_show_session_wizard(self, main_window):
        """Test showing session wizard."""
        main_window.show_session_wizard()
        assert main_window.stacked_widget.currentWidget() == main_window.session_wizard

    def test_show_session_dashboard(self, main_window):
        """Test showing session dashboard."""
        from oroitz.core.session import Session

        session = Session(name="Test Session")
        main_window.show_session_dashboard(session)
        assert main_window.stacked_widget.currentWidget() == main_window.session_dashboard

    def test_session_created_signal(self, main_window, qtbot):
        """Test session created signal handling."""
        from oroitz.core.session import Session

        # Create a session
        session = Session(image_path=Path("/test.img"), profile="windows")

        # Test that _on_session_created emits the signal and shows dashboard
        with qtbot.waitSignal(main_window.session_created, timeout=1000) as blocker:
            main_window._on_session_created(session)

        assert blocker.signal_triggered
        assert main_window.stacked_widget.currentWidget() == main_window.session_dashboard


class TestLandingView:
    """Test LandingView functionality."""

    def test_initial_state(self, qapp):
        """Test initial state of landing view."""
        # Create a fresh session manager for this test
        import tempfile
        from pathlib import Path

        from oroitz.core.session import SessionManager

        with tempfile.TemporaryDirectory() as temp_dir:
            session_manager = SessionManager(Path(temp_dir) / "sessions")
            view = LandingView(session_manager)
            # Should have 1 item saying "No recent sessions"
            assert view.sessions_list.count() == 1
            assert view.sessions_list.item(0).text() == "No recent sessions"

    def test_new_session_button(self, session_manager, qapp, qtbot):
        """Test new session button click."""
        view = LandingView(session_manager)

        # Find the new analysis button by searching all buttons
        buttons = view.findChildren(QPushButton)
        new_analysis_btn = None
        for btn in buttons:
            if btn.text() == "New Analysis":
                new_analysis_btn = btn
                break
        assert new_analysis_btn is not None

        with qtbot.waitSignal(view.new_analysis_requested, timeout=1000) as blocker:
            qtbot.mouseClick(new_analysis_btn, Qt.LeftButton)

        assert blocker.signal_triggered

    def test_session_selection(self, qapp, qtbot):
        """Test session selection from list."""
        # Create a fresh session manager for this test
        import tempfile
        from pathlib import Path

        from oroitz.core.session import Session, SessionManager

        with tempfile.TemporaryDirectory() as temp_dir:
            session_manager = SessionManager(Path(temp_dir) / "sessions")

            # Add a mock session
            session = Session(name="Test Session", image_path=Path("/test.img"), profile="windows")
            session_manager._sessions[session.id] = session
            session_manager.save_sessions()

            view = LandingView(session_manager)

            # Refresh the view
            view.refresh_sessions()

            assert view.sessions_list.count() == 1
            assert "Test Session" in view.sessions_list.item(0).text()

            # Double-click the session item in the list
            with qtbot.waitSignal(view.session_selected, timeout=1000) as blocker:
                # Trigger the double-click by calling the slot directly
                item = view.sessions_list.item(0)
                view._on_session_double_clicked(item)

            assert blocker.signal_triggered


class TestSessionWizard:
    """Test SessionWizard functionality."""

    def test_wizard_pages(self, qapp):
        """Test wizard has required pages."""
        wizard = SessionWizard()
        assert wizard.page(0) is not None  # Session info page
        assert wizard.page(1) is not None  # Image selection page
        assert wizard.page(2) is not None  # Workflow selection page
        assert wizard.page(3) is not None  # Summary page

    def test_image_path_input(self, qapp, qtbot):
        """Test image path input."""
        wizard = SessionWizard()

        # Navigate to image selection page (page 1) - SessionInfoPage is 0, ImageSelectionPage is 1
        wizard.setStartId(1)
        wizard.restart()
        qtbot.wait(100)  # Allow UI to update

        # Find the image path input in the current page
        current_page = wizard.currentPage()
        assert current_page is not None
        image_edit = current_page.findChild(QLineEdit)
        assert image_edit is not None

        # Type a path
        test_path = "/test/memory.img"
        image_edit.setText(test_path)
        assert image_edit.text() == test_path

    def test_profile_selection(self, qapp, qtbot):
        """Test profile selection."""
        wizard = SessionWizard()

        # Navigate to image selection page (page 1)
        wizard.setStartId(1)
        wizard.restart()
        qtbot.wait(100)  # Allow UI to update

        # Find profile combo box in the current page
        current_page = wizard.currentPage()
        assert current_page is not None
        profile_combo = current_page.findChild(QComboBox)
        assert profile_combo is not None
        profile_combo.setCurrentText("Win10x64_19041")
        assert profile_combo.currentText() == "Win10x64_19041"

    def test_wizard_completion(self, qapp, qtbot):
        """Test wizard completion creates session."""
        wizard = SessionWizard()

        # Fill in required fields
        wizard.setField("sessionName", "Test Session")
        wizard.setField("imagePath", "/test/memory.img")
        wizard.setField("profile", "Win10x64_19041")

        # Mock the finish signal
        with qtbot.waitSignal(wizard.session_created, timeout=1000) as blocker:
            # Simulate completing the wizard
            wizard.done(QWizard.Accepted)

        assert blocker.signal_triggered


class TestSessionDashboard:
    """Test SessionDashboard functionality."""

    def test_initial_state(self, qapp):
        """Test initial state of dashboard."""
        dashboard = SessionDashboard()
        assert dashboard.progress_bar.value() == 0
        assert dashboard.logs_text.toPlainText() == "Analysis logs will appear here..."

    def test_set_session(self, qapp):
        """Test setting session in dashboard."""
        dashboard = SessionDashboard()
        from pathlib import Path

        from oroitz.core.session import Session

        session = Session(
            name="Test Session",
            image_path=Path("/test.img"),
            profile="Win10x64_19041",
            workflow_id="quick_triage",
        )

        dashboard.set_session(session)
        assert dashboard.current_session == session
        assert "Test Session" in dashboard.session_title.text()

    def test_workflow_execution(self, qapp, qtbot):
        """Test workflow execution in dashboard."""
        dashboard = SessionDashboard()
        from pathlib import Path

        from oroitz.core.session import Session

        # Set up a session
        session = Session(
            name="Test Session",
            image_path=Path("/test.img"),
            profile="Win10x64_19041",
            workflow_id="quick_triage",
        )
        dashboard.set_session(session)

        # Mock the start button click
        with patch.object(dashboard, "_on_start_clicked") as mock_start:
            qtbot.mouseClick(dashboard.start_btn, Qt.LeftButton)
            mock_start.assert_called_once()

    def test_progress_updates(self, qapp, qtbot):
        """Test progress bar updates."""
        dashboard = SessionDashboard()

        # Simulate progress updates via signals
        dashboard._on_progress_updated(50, "Halfway done")
        assert dashboard.progress_bar.value() == 50
        assert dashboard.status_label.text() == "Halfway done"

        dashboard._on_progress_updated(100, "Complete")
        assert dashboard.progress_bar.value() == 100

    def test_log_updates(self, qapp):
        """Test log text updates."""
        dashboard = SessionDashboard()

        test_message = "Test log message"
        dashboard._on_log_message(test_message)

        assert test_message in dashboard.logs_text.toPlainText()
