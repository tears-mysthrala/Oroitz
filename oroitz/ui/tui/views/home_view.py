"""Home View for Oroitz TUI."""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Static

from oroitz.core.workflow import registry

from ..widgets import Breadcrumb


class HomeView(Screen):
    """Home screen with workflow selection."""

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("ctrl+c", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        """Compose the home screen."""
        with Container(id="home-container"):
            with Vertical():
                yield Breadcrumb("Home")
                yield Static("🕵️ Oroitz - Cross-platform Volatility 3 Wrapper", id="title")
                yield Static("Select a workflow to begin analysis:", classes="subtitle")

                # Workflow buttons
                with VerticalScroll(id="workflow-scroll"):
                    with Vertical(id="workflow-buttons"):
                        for workflow in registry.list():
                            yield Button(
                                f"{workflow.name}\n{workflow.description}",
                                id=f"workflow-{workflow.id}",
                                classes="workflow-button",
                            )

                yield Static("", id="spacer")
                yield Static(
                    "💡 Tip: Use Tab/Shift+Tab to navigate, Enter to select, Esc to go back",
                    classes="help-text",
                )
                with Horizontal(id="bottom-buttons"):
                    yield Button("Help", id="help-button", variant="default")
                    yield Button("Settings", id="settings-button", variant="default")
                    yield Button("Provide Feedback", id="feedback-button", variant="default")
                yield Button("Exit", id="exit-button", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "exit-button":
            self.app.exit()
        elif button_id == "feedback-button":
            from .feedback_view import FeedbackView

            self.app.push_screen(FeedbackView())
        elif button_id == "help-button":
            from .help_view import HelpView

            self.app.push_screen(HelpView())
        elif button_id == "settings-button":
            from .settings_view import SettingsView

            self.app.push_screen(SettingsView())
        elif button_id and button_id.startswith("workflow-"):
            workflow_id = button_id.replace("workflow-", "")
            workflow = registry.get(workflow_id)
            if workflow:
                from .session_wizard_view import SessionWizardView

                self.app.push_screen(SessionWizardView(workflow))
