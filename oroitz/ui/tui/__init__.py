"""Textual TUI application for Oroitz."""

from typing import Optional

from textual.app import App, ComposeResult
from textual.command import CommandPalette, Hit, Hits, Provider
from textual.widgets import Footer, Header

from oroitz.core.executor import Executor
from oroitz.core.output import OutputExporter, OutputNormalizer
from oroitz.core.session import Session
from oroitz.core.telemetry import setup_logging

from .views import HomeView
from .widgets import Breadcrumb


class OroitzTUI(App):
    """Main Textual application for Oroitz."""

    CSS_PATH = "styles/base.css"

    BINDINGS = [
        ("ctrl+k", "command_palette", "Command Palette"),
        ("f1", "help", "Help"),
    ]

    def __init__(self):
        super().__init__()
        self.session: Optional[Session] = None
        self.executor = Executor()
        self.normalizer = OutputNormalizer()
        self.exporter = OutputExporter()
        setup_logging("INFO")

    def compose(self) -> ComposeResult:
        """Compose the main application layout."""
        yield Header()
        yield Footer()
        yield CommandPalette()

    async def on_mount(self) -> None:
        """Handle application mount."""
        await self.push_screen(HomeView())

    def get_current_session(self) -> Optional[Session]:
        """Get the current active session."""
        return self.session

    def set_current_session(self, session: Optional[Session]) -> None:
        """Set the current active session."""
        self.session = session

    def action_command_palette(self) -> None:
        """Show the command palette."""
        self.push_screen("command-palette")

    def action_help(self) -> None:
        """Show help."""
        # TODO: Implement help screen
        self.notify("Help not implemented yet", severity="information")

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
