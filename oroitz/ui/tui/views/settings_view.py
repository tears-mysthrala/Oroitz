"""Settings View for Oroitz TUI."""

from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Container, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Checkbox, Input, Label, Select, Static

from oroitz.core.cache import cache
from oroitz.core.config import config
from oroitz.core.telemetry import logger


class SettingsView(Screen):
    """Screen for application settings and configuration."""

    BINDINGS = [
        ("escape", "back", "Back"),
        ("ctrl+c", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        """Compose the settings screen."""
        with Container(id="settings-container"):
            with VerticalScroll():
                with Vertical():
                    yield Static("Settings", id="settings-title")

                    # General settings
                    yield Static("General", classes="section-header")
                    yield Label("Log Level:")
                    yield Select(
                        [
                            ("DEBUG", "Debug"),
                            ("INFO", "Info"),
                            ("WARNING", "Warning"),
                            ("ERROR", "Error"),
                        ],
                        id="log-level-select",
                        value=config.log_level,
                    )

                    yield Checkbox(
                        "Enable telemetry",
                        id="telemetry-checkbox",
                        value=config.telemetry_enabled,
                    )

                    # Cache settings
                    yield Static("Cache", classes="section-header")
                    yield Checkbox(
                        "Force re-execute on fail",
                        id="force-reexecute-checkbox",
                        value=config.force_reexecute_on_fail,
                    )
                    yield Button("Clear Cache", id="clear-cache-button", variant="default")

                    # Advanced settings
                    yield Static("Advanced", classes="section-header")
                    yield Label("Volatility Path:")
                    yield Input(
                        placeholder="/path/to/volatility",
                        id="volatility-path-input",
                        value=str(config.volatility_path) if config.volatility_path else "",
                    )

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
        config.log_level = self.query_one("#log-level-select").value
        config.telemetry_enabled = self.query_one("#telemetry-checkbox").value
        config.force_reexecute_on_fail = self.query_one("#force-reexecute-checkbox").value

        vol_path_input = self.query_one("#volatility-path-input").value
        config.volatility_path = Path(vol_path_input) if vol_path_input else None

        # In a real application, you'd persist config to a file here.
        # For pydantic-settings, changes to the in-memory object are used immediately.
        logger.info("Settings saved: %s", config.model_dump_json())
        self.notify("Settings saved", severity="information")

    def _clear_cache(self) -> None:
        """Clear the application cache."""
        cache.clear()
        self.notify("Cache cleared", severity="information")
