"""Main window for the PySide6 GUI application."""


from PySide6.QtCore import Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from oroitz.core.session import SessionManager
from oroitz.core.workflow import seed_workflows
from oroitz.ui.gui.landing_view import LandingView
from oroitz.ui.gui.session_dashboard import SessionDashboard
from oroitz.ui.gui.session_wizard import SessionWizard
from oroitz.ui.gui.settings_dialog import SettingsDialog


class MainWindow(QMainWindow):
    """Main application window with navigation between views."""

    # Signals
    session_created = Signal(object)  # Session object
    session_selected = Signal(object)  # Session object

    def __init__(self) -> None:
        """Initialize the main window."""
        super().__init__()

        # Initialize core components
        seed_workflows()
        self.session_manager = SessionManager()

        # Setup UI
        self._setup_ui()
        self._setup_menu()
        self._setup_connections()

        # Show landing view initially
        self.show_landing_view()

    def _setup_ui(self) -> None:
        """Setup the main UI components."""
        self.setWindowTitle("Oroitz - Cross-platform Volatility 3 Wrapper")
        self.setMinimumSize(1200, 800)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # Create stacked widget for different views
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)

        # Create views
        self.landing_view = LandingView()
        self.session_wizard = SessionWizard()
        self.session_dashboard = SessionDashboard()

        # Add views to stack
        self.stacked_widget.addWidget(self.landing_view)
        self.stacked_widget.addWidget(self.session_wizard)
        self.stacked_widget.addWidget(self.session_dashboard)

    def _setup_menu(self) -> None:
        """Setup the application menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        new_action = QAction("&New Analysis", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.show_session_wizard)
        file_menu.addAction(new_action)

        open_action = QAction("&Open Session", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._open_session)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View menu
        view_menu = menubar.addMenu("&View")

        landing_action = QAction("&Landing", self)
        landing_action.triggered.connect(self.show_landing_view)
        view_menu.addAction(landing_action)

        view_menu.addSeparator()

        settings_action = QAction("&Settings", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(self._show_settings)
        view_menu.addAction(settings_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _setup_connections(self) -> None:
        """Setup signal connections between components."""
        # Landing view connections
        self.landing_view.new_analysis_requested.connect(self.show_session_wizard)
        self.landing_view.session_selected.connect(self._on_session_selected)

        # Session wizard connections
        self.session_wizard.session_created.connect(self._on_session_created)
        self.session_wizard.cancelled.connect(self.show_landing_view)

        # Session dashboard connections
        self.session_dashboard.back_to_landing.connect(self.show_landing_view)

    def show_landing_view(self) -> None:
        """Show the landing view."""
        self.stacked_widget.setCurrentWidget(self.landing_view)
        self.landing_view.refresh_sessions()

    def show_session_wizard(self) -> None:
        """Show the session wizard."""
        self.stacked_widget.setCurrentWidget(self.session_wizard)
        self.session_wizard.restart()

    def show_session_dashboard(self, session) -> None:
        """Show the session dashboard for the given session."""
        self.session_dashboard.set_session(session)
        self.stacked_widget.setCurrentWidget(self.session_dashboard)

    def _on_session_created(self, session) -> None:
        """Handle session creation from wizard."""
        self.session_created.emit(session)
        self.show_session_dashboard(session)

    def _on_session_selected(self, session) -> None:
        """Handle session selection from landing view."""
        self.session_selected.emit(session)
        self.show_session_dashboard(session)

    def _open_session(self) -> None:
        """Open an existing session file."""
        # TODO: Implement file dialog for opening session files
        pass

    def _show_about(self) -> None:
        """Show about dialog."""
        # TODO: Implement about dialog
        pass

    def _show_settings(self) -> None:
        """Show settings dialog."""
        dialog = SettingsDialog(self)
        dialog.exec()

    def closeEvent(self, event) -> None:
        """Handle application close event."""
        # Save any unsaved state
        self.session_manager.save_sessions()
        super().closeEvent(event)
