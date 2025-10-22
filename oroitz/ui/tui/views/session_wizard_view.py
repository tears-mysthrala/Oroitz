"""Session Wizard View for Oroitz TUI."""

from pathlib import Path
from typing import Optional

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Input, Label, Static

from oroitz.core.session import Session
from oroitz.core.workflow import WorkflowSpec, registry

from ..widgets import Breadcrumb


class SessionWizardView(Screen):
    """Screen for creating a new analysis session."""

    BINDINGS = [
        ("escape", "back", "Back"),
        ("ctrl+c", "quit", "Quit"),
    ]

    def __init__(self, workflow: WorkflowSpec):
        super().__init__()
        self.workflow = workflow
        self.image_path: Optional[Path] = None

    def compose(self) -> ComposeResult:
        """Compose the session wizard."""
        with Container(id="wizard-container"):
            with Vertical():
                yield Breadcrumb(f"Home > {self.workflow.name}")
                yield Static(f"Configure Session: {self.workflow.name}", id="wizard-title")
                yield Static(self.workflow.description, classes="description")

                with Vertical(id="form"):
                    yield Label("Memory Image Path:")
                    yield Input(placeholder="/path/to/memory/image.raw", id="image-path-input")

                with Horizontal(id="buttons"):
                    yield Button("Back", id="back-button", variant="default")
                    yield Button("Start Analysis", id="start-button", variant="primary")

                yield Static(
                    "💡 Use Tab to navigate fields, Enter to select, Esc to go back",
                    classes="help-text",
                )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "back-button":
            self.app.pop_screen()
        elif button_id == "start-button":
            self._start_analysis()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission."""
        if event.input.id == "image-path-input":
            path_str = event.value.strip()
            if path_str:
                self.image_path = Path(path_str)

    def _start_analysis(self) -> None:
        """Start the analysis with current configuration."""
        if not self.image_path:
            self.notify("Please enter a memory image path", severity="error")
            return

        if not self.image_path.exists():
            self.notify(f"Memory image file does not exist: {self.image_path}", severity="error")
            return

        # Check workflow compatibility - Volatility 3 auto-detects OS
        if not registry.validate_compatibility(self.workflow.id):
            self.notify("Workflow validation failed", severity="error")
            return

        # Create session
        session = Session(image_path=self.image_path)
        # Cast app to access custom methods
        from .. import OroitzTUI

        if isinstance(self.app, OroitzTUI):
            self.app.set_current_session(session)

        # Start analysis
        from .run_view import RunView

        self.app.push_screen(RunView(self.workflow, session))
