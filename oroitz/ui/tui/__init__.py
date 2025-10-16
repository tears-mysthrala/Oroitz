"""Textual TUI application for Oroitz."""

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Button, Static, DataTable, Input, Select
from textual.screen import Screen
from textual import events
from typing import Optional
import asyncio

from oroitz.core.session import Session
from oroitz.core.workflow import registry
from oroitz.core.executor import Executor
from oroitz.core.output import OutputNormalizer, OutputExporter
from oroitz.core.telemetry import setup_logging


class OroitzTUI(App):
    """Main Textual application for Oroitz."""

    CSS = """
    Screen {
        background: $surface;
        color: $text;
    }

    Container {
        height: 100%;
        width: 100%;
    }

    #main-container {
        layout: vertical;
    }

    #title {
        text-align: center;
        margin: 2;
        color: $primary;
        text-style: bold;
    }

    .subtitle {
        text-align: center;
        margin: 1;
        color: $text-muted;
    }

    .workflow-button {
        width: 100%;
        margin: 1;
        padding: 1;
        background: $primary-darken-1;
        border: solid $primary;
    }

    .workflow-button:hover {
        background: $primary;
    }

    #wizard-title {
        text-align: center;
        margin: 2;
        color: $primary;
        text-style: bold;
    }

    .description {
        text-align: center;
        margin: 1;
        color: $text-muted;
    }

    #form {
        margin: 2;
    }

    #buttons {
        margin: 2;
        align: center middle;
    }

    #run-title {
        text-align: center;
        margin: 2;
        color: $primary;
        text-style: bold;
    }

    .image-info, .profile-info {
        text-align: center;
        margin: 1;
        color: $text-muted;
    }

    #progress-bar {
        margin: 2;
    }

    #log-container {
        height: 60%;
        margin: 2;
        border: solid $primary-darken-2;
        padding: 1;
    }

    #log-title {
        color: $primary;
        text-style: bold;
    }

    #log-content {
        color: $text;
        background: $surface-darken-1;
        padding: 1;
    }

    #run-buttons {
        margin: 2;
        align: center middle;
    }

    #results-title {
        text-align: center;
        margin: 2;
        color: $primary;
        text-style: bold;
    }

    .session-info {
        text-align: center;
        margin: 1;
        color: $text-muted;
    }

    #summary {
        text-align: center;
        margin: 2;
        color: $success;
        text-style: bold;
    }

    #results-table {
        height: 50%;
        margin: 2;
    }

    #export-buttons {
        margin: 2;
        align: center middle;
    }

    Button {
        margin: 1;
    }

    .error {
        background: $error;
        color: $text;
    }

    .success {
        background: $success;
        color: $text;
    }
    """

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

    async def on_mount(self) -> None:
        """Handle application mount."""
        await self.push_screen(HomeScreen())

    def get_current_session(self) -> Optional[Session]:
        """Get the current active session."""
        return self.session

    def set_current_session(self, session: Optional[Session]) -> None:
        """Set the current active session."""
        self.session = session

    async def action_quit(self) -> None:
        """Quit the application."""
        await self.exit()

    async def action_back(self) -> None:
        """Go back to previous screen."""
        await self.pop_screen()

    async def action_home(self) -> None:
        """Go back to home screen."""
        # Clear session and go to home
        self.set_current_session(None)
        await self.pop_screen()
        await self.pop_screen()
        await self.pop_screen()  # Should get us back to home


# Import screens here to avoid circular imports
from .screens import HomeScreen
