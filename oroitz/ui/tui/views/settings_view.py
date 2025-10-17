"""Settings View for Oroitz TUI."""

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual.widgets import Button, Checkbox, Input, Label, Select, Static


class SettingsView(Screen):
    """Screen for application settings and configuration."""

    BINDINGS = [
        ("escape", "back", "Back"),
        ("ctrl+c", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        """Compose the settings screen."""
        with Container(id="settings-container"):
            with Vertical():
                yield Static("Settings", id="settings-title")

                # General settings
                yield Static("General", classes="section-header")
                yield Label("Log Level:")
                yield Select(
                    [("DEBUG", "Debug"), ("INFO", "Info"), ("WARNING", "Warning"), ("ERROR", "Error")],
                    id="log-level-select",
                )

                yield Checkbox("Enable telemetry", id="telemetry-checkbox")

                # Cache settings
                yield Static("Cache", classes="section-header")
                yield Button("Clear Cache", id="clear-cache-button", variant="default")

                # Advanced settings
                yield Static("Advanced", classes="section-header")
                yield Label("Volatility Path:")
                yield Input(placeholder="/path/to/volatility", id="volatility-path-input")

                yield Button("Save Settings", id="save-button", variant="primary")
                yield Button("Back", id="back-button", variant="default")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "back-button":
            self.app.pop_screen()
        elif button_id == "save-button":
            self._save_settings()
        elif button_id == "clear-cache-button":
            self._clear_cache()

    def _save_settings(self) -> None:
        """Save the current settings."""
        # TODO: Implement settings persistence
        self.notify("Settings saved", severity="information")

    def _clear_cache(self) -> None:
        """Clear the application cache."""
        # TODO: Implement cache clearing
        self.notify("Cache cleared", severity="information")