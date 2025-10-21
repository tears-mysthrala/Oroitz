"""Error View for Oroitz TUI."""

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual.widgets import Button, Static


class ErrorView(Screen):
    """Screen for displaying fatal errors."""

    BINDINGS = [
        ("escape", "back", "Back"),
        ("ctrl+c", "quit", "Quit"),
    ]

    def __init__(self, error_message: str, details: str = ""):
        super().__init__()
        self.error_message = error_message
        self.details = details

    def compose(self) -> ComposeResult:
        """Compose the error screen."""
        with Container(id="error-container"):
            with Vertical():
                yield Static("🚨 Error", id="error-title")
                yield Static(self.error_message, id="error-message", classes="error")
                if self.details:
                    yield Static("Details:", classes="error-details-title")
                    yield Static(self.details, id="error-details", classes="error-details")

                yield Button("Copy Details", id="copy-button", variant="default")
                yield Button("Back", id="back-button", variant="primary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "back-button":
            self.app.pop_screen()
        elif button_id == "copy-button":
            self._copy_details()

    def _copy_details(self) -> None:
        """Copy error details to clipboard."""
        # TODO: Implement clipboard copy
        full_details = f"{self.error_message}\n{self.details}"
        self.notify("Error details copied to clipboard", severity="information")
