"""Help View for Oroitz TUI."""

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual.widgets import Button, Static

from ..widgets import Breadcrumb


class HelpView(Screen):
    """Screen showing help and keyboard shortcuts."""

    BINDINGS = [
        ("escape", "back", "Back"),
        ("ctrl+c", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        """Compose the help screen."""
        with Container(id="help-container"):
            with Vertical():
                yield Breadcrumb("Home > Help")
                yield Static("🆘 Oroitz Help & Shortcuts", id="help-title")
                yield Static(
                    "Welcome to Oroitz - Cross-platform Volatility 3 Wrapper",
                    classes="help-subtitle",
                )

                yield Static("📋 Available Workflows:", classes="section-title")
                yield Static(
                    "• Quick Triage: Fast overview of processes, network, and malware",
                    classes="help-text",
                )
                yield Static(
                    "• Process Deep Dive: Detailed process analysis with DLLs and handles",
                    classes="help-text",
                )
                yield Static(
                    "• Network Focus: Comprehensive network connection analysis",
                    classes="help-text",
                )
                yield Static(
                    "• Timeline Overview: Chronological event timeline",
                    classes="help-text",
                )

                yield Static("⌨️  Keyboard Shortcuts:", classes="section-title")
                yield Static("• Tab/Shift+Tab: Navigate between elements", classes="help-text")
                yield Static("• Enter: Select/Activate button or input", classes="help-text")
                yield Static("• Esc: Go back to previous screen", classes="help-text")
                yield Static("• Ctrl+K: Open command palette", classes="help-text")
                yield Static("• F1: Open this help screen", classes="help-text")
                yield Static("• Ctrl+C: Quit application", classes="help-text")

                yield Static("💡 Tips:", classes="section-title")
                yield Static(
                    "• Start with Quick Triage for fast results",
                    classes="help-text",
                )
                yield Static(
                    "• Use Process Deep Dive when investigating specific processes",
                    classes="help-text",
                )
                yield Static(
                    "• Results are automatically exported to JSON/CSV",
                    classes="help-text",
                )
                yield Static(
                    "• Check the logs during analysis for detailed progress",
                    classes="help-text",
                )

                yield Button("Back to Home", id="back-button", variant="primary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "back-button":
            self.app.pop_screen()
