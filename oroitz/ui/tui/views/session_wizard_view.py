"""Session Wizard View for Oroitz TUI."""

from pathlib import Path
from typing import Optional

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Input, Label, Select, Static

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
        self.profile = "windows"

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

                    yield Label("Profile:")
                    yield Select(
                        [("windows", "Windows"), ("linux", "Linux"), ("mac", "macOS")],
                        id="profile-select",
                    )

                with Horizontal(id="buttons"):
                    yield Button("Back", id="back-button", variant="default")
                    yield Button("Start Analysis", id="start-button", variant="primary")

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

    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle select changes."""
        if event.select.id == "profile-select":
            self.profile = event.value

    def _start_analysis(self) -> None:
        """Start the analysis with current configuration."""
        if not self.image_path:
            self.notify("Please enter a memory image path", severity="error")
            return

        if not self.image_path.exists():
            self.notify(f"Memory image file does not exist: {self.image_path}", severity="error")
            return

        # Check workflow compatibility
        if not registry.validate_compatibility(self.workflow.id, str(self.profile)):
            self.notify(f"Workflow not compatible with profile: {self.profile}", severity="error")
            return

        # Create session
        session = Session(image_path=self.image_path, profile=str(self.profile))
        # Cast app to access custom methods
        from .. import OroitzTUI
        if isinstance(self.app, OroitzTUI):
            self.app.set_current_session(session)

        # Start analysis
        from .run_view import RunView
        self.app.push_screen(RunView(self.workflow, session))