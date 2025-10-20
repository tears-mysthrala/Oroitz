"""Tests for the PySide6 GUI application."""

import pytest

from pathlib import Path
from unittest.mock import patch

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QComboBox, QLineEdit, QPushButton, QWizard

from oroitz.core.session import SessionManager
from oroitz.core.workflow import seed_workflows
from oroitz.ui.gui.landing_view import LandingView
from oroitz.ui.gui.main_window import MainWindow
from oroitz.ui.gui.about_dialog import AboutDialog
from oroitz.ui.gui.results_explorer import ResultsExplorer
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


@pytest.mark.gui
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

    def test_open_session_file_dialog(self, main_window, qtbot, tmp_path, monkeypatch):
        """Test opening a session file through file dialog."""
        from pathlib import Path
        from unittest.mock import patch
        
        # Create a test session file
        session_data = {
            "id": "test-session-id",
            "name": "Test Session",
            "image_path": "/test/image.dmp",
            "profile": "Win10x64_19041",
            "workflow_id": "quick_triage",
            "created_at": "2025-01-01T00:00:00",
            "updated_at": "2025-01-01T00:00:00"
        }
        session_file = tmp_path / "test_session.json"
        import json
        with open(session_file, 'w') as f:
            json.dump(session_data, f)
        
        # Mock QFileDialog.getOpenFileName to return our test file
        def mock_get_open_file_name(parent, title, directory, filter_str):
            return str(session_file), "Session Files (*.json)"
        
        monkeypatch.setattr("oroitz.ui.gui.main_window.QFileDialog.getOpenFileName", mock_get_open_file_name)
        
        # Mock the show_session_dashboard method to verify it's called
        with patch.object(main_window, 'show_session_dashboard') as mock_show_dashboard:
            main_window._open_session()
            
            # Verify show_session_dashboard was called with the loaded session
            assert mock_show_dashboard.called
            session = mock_show_dashboard.call_args[0][0]
            assert session.id == "test-session-id"
            assert session.name == "Test Session"

    def test_show_about_dialog(self, main_window, qtbot):
        """Test showing the about dialog."""
        # Mock the dialog exec method to avoid actually showing the dialog
        with patch('oroitz.ui.gui.about_dialog.AboutDialog.exec') as mock_exec:
            main_window._show_about()
            mock_exec.assert_called_once()

    def test_export_json_file_dialog(self, qapp, monkeypatch):
        """Test JSON export with file dialog."""
        from unittest.mock import patch, MagicMock
        from pathlib import Path
        
        explorer = ResultsExplorer()
        
        # Mock normalized data
        mock_data = MagicMock()
        explorer.normalized_data = mock_data
        
        # Mock QFileDialog.getSaveFileName
        def mock_get_save_file_name(parent, title, default_name, filter_str):
            return "/test/path/results.json", "JSON Files (*.json)"
        
        monkeypatch.setattr("oroitz.ui.gui.results_explorer.QFileDialog.getSaveFileName", mock_get_save_file_name)
        
        # Mock the exporter
        with patch('oroitz.ui.gui.results_explorer.OutputExporter') as mock_exporter_class:
            mock_exporter = MagicMock()
            mock_exporter_class.return_value = mock_exporter
            
            explorer._export_json()
            
            # Verify exporter was called with correct path
            mock_exporter.export_json.assert_called_once_with(mock_data, Path("/test/path/results.json"))

    def test_export_csv_directory_dialog(self, qapp, monkeypatch):
        """Test CSV export with directory dialog."""
        from unittest.mock import patch, MagicMock
        from pathlib import Path
        
        explorer = ResultsExplorer()
        
        # Mock normalized data
        mock_data = MagicMock()
        explorer.normalized_data = mock_data
        
        # Mock QFileDialog.getExistingDirectory
        def mock_get_existing_directory(parent, title, default_dir):
            return "/test/directory"
        
        monkeypatch.setattr("oroitz.ui.gui.results_explorer.QFileDialog.getExistingDirectory", mock_get_existing_directory)
        
        # Mock the exporter
        with patch('oroitz.ui.gui.results_explorer.OutputExporter') as mock_exporter_class:
            mock_exporter = MagicMock()
            mock_exporter_class.return_value = mock_exporter
            
            explorer._export_csv()
            
            # Verify exporter was called with correct path
            expected_path = Path("/test/directory") / "oroitz_results.csv"
            mock_exporter.export_csv.assert_called_once_with(mock_data, expected_path)


@pytest.mark.gui
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
            if btn.text() == "🔍 Start New Analysis":
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


@pytest.mark.gui
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


@pytest.mark.gui
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
