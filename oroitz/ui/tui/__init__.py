"""Textual TUI application for Oroitz."""

import sys
from typing import Optional

from textual.app import App

from oroitz.core.executor import Executor
from oroitz.core.output import OutputExporter, OutputNormalizer
from oroitz.core.session import Session
from oroitz.core.telemetry import logger, setup_logging
from oroitz.core.workflow import seed_workflows

from .views import HomeView
from .widgets import Breadcrumb

__all__ = ["OroitzTUI", "HomeView", "Breadcrumb"]


class OroitzTUI(App):
    """Main Textual application for Oroitz."""

    CSS_PATH = None if getattr(sys, "_MEIPASS", None) else "styles/base.css"

    BINDINGS = [
        ("f1", "help", "Help"),
    ]

    def __init__(self):
        super().__init__()
        seed_workflows()
        self.session: Optional[Session] = None
        self.executor = Executor()
        self.normalizer = OutputNormalizer()
        self.exporter = OutputExporter()
        setup_logging("INFO")

    def on_mount(self) -> None:
        """Mount the initial screen."""
        self.push_screen(HomeView())
        logger.info("TUI on_mount called")

    # def compose(self) -> ComposeResult:
    #     """Compose the main application layout."""
    #     # yield Header()
    #     # yield Footer()
    #     pass

    def get_current_session(self) -> Optional[Session]:
        """Get the current active session."""
        return self.session

    def set_current_session(self, session: Optional[Session]) -> None:
        """Set the current active session."""
        self.session = session

    def action_help(self) -> None:
        """Show help."""
        from .views.help_view import HelpView

        self.push_screen(HelpView())

    def action_new(self) -> None:
        """Create a new session."""
        # Go to home and trigger new session
        self.push_screen(HomeView())

    def action_settings(self) -> None:
        """Open settings."""
        from .views.settings_view import SettingsView

        self.push_screen(SettingsView())

    def action_pause(self) -> None:
        """Pause current operation."""
        # TODO: Implement pause
        self.notify("Pause not implemented yet", severity="information")

    def action_resume(self) -> None:
        """Resume current operation."""
        # TODO: Implement resume
        self.notify("Resume not implemented yet", severity="information")

    def action_feedback(self) -> None:
        """Open feedback collection form."""
        from .views.feedback_view import FeedbackView

        self.push_screen(FeedbackView())
