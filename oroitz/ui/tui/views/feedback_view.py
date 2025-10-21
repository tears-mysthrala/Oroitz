"""Feedback Collection View for Oroitz TUI."""

from pathlib import Path
from typing import Dict

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Checkbox, Input, Label, RadioSet, Static, TextArea

from ..widgets import Breadcrumb


class FeedbackView(Screen):
    """Screen for collecting manual testing feedback."""

    BINDINGS = [
        ("escape", "back", "Back"),
        ("ctrl+c", "quit", "Quit"),
    ]

    def __init__(self):
        super().__init__()
        self.feedback_data: Dict[str, str] = {}

    def compose(self) -> ComposeResult:
        """Compose the feedback collection screen."""
        with Container(id="feedback-container"):
            with Vertical():
                yield Breadcrumb("Home > Feedback")
                yield Static("Manual Testing Feedback", id="feedback-title")
                yield Static(
                    "Please provide feedback on your testing experience. "
                    "This helps us improve Oroitz!",
                    classes="feedback-subtitle",
                )

                with VerticalScroll(id="feedback-form"):
                    # Tester Information
                    yield Static("Tester Information", classes="section-header")
                    yield Label("Your Name:")
                    yield Input(placeholder="Enter your name", id="tester-name")

                    yield Label("Testing Environment:")
                    yield Input(placeholder="OS, Terminal, Python version, etc.", id="environment")

                    # Overall Experience
                    yield Static("Overall Experience", classes="section-header")
                    yield Label("How would you rate the overall experience?")
                    yield RadioSet(
                        "Excellent",
                        "Good",
                        "Average",
                        "Poor",
                        "Very Poor",
                        id="overall-rating",
                    )

                    # Feature Ratings
                    yield Static("Feature Ratings", classes="section-header")

                    features = [
                        ("navigation", "Navigation and workflow"),
                        ("performance", "Performance and responsiveness"),
                        ("usability", "Ease of use"),
                        ("visual", "Visual design and themes"),
                        ("functionality", "Core functionality"),
                        ("error_handling", "Error handling and messages"),
                    ]

                    for feature_id, feature_name in features:
                        yield Label(f"{feature_name}:")
                        yield RadioSet(
                            "Excellent",
                            "Good",
                            "Average",
                            "Poor",
                            "Not Tested",
                            id=f"rating-{feature_id}",
                        )

                    # Issues Found
                    yield Static("Issues Found", classes="section-header")
                    yield Label("Did you encounter any issues?")
                    yield RadioSet("Yes", "No", id="issues-found")

                    yield Label("Please describe any issues:")
                    yield TextArea(
                        placeholder="Describe bugs, crashes, confusing UI elements, etc.",
                        id="issues-description",
                    )

                    # Suggestions
                    yield Static("Suggestions for Improvement", classes="section-header")
                    yield Label("What features would you like to see added?")
                    yield TextArea(
                        placeholder="New features, improvements, etc.",
                        id="feature-suggestions",
                    )

                    yield Label("Any other comments or feedback:")
                    yield TextArea(
                        placeholder="General comments, praise, concerns, etc.",
                        id="general-comments",
                    )

                    # Testing Scenarios
                    yield Static("Testing Scenarios Completed", classes="section-header")
                    yield Checkbox("Created a new session", id="scenario-new-session")
                    yield Checkbox("Ran quick_triage workflow", id="scenario-quick-triage")
                    yield Checkbox("Viewed results and exported data", id="scenario-view-results")
                    yield Checkbox("Used command palette", id="scenario-command-palette")
                    yield Checkbox("Accessed settings", id="scenario-settings")
                    yield Checkbox("Tested error scenarios", id="scenario-error-handling")

                with Horizontal(id="feedback-buttons"):
                    yield Button("Save Feedback", id="save-feedback", variant="primary")
                    yield Button("Clear Form", id="clear-form", variant="default")
                    yield Button("Back", id="back-button", variant="default")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "back-button":
            self.app.pop_screen()
        elif button_id == "save-feedback":
            self._save_feedback()
        elif button_id == "clear-form":
            self._clear_form()

    def _save_feedback(self) -> None:
        """Save the feedback to a file."""
        try:
            # Collect all form data
            self._collect_form_data()

            # Save to file
            feedback_file = Path("manual_testing_feedback.txt")
            with open(feedback_file, "a", encoding="utf-8") as f:
                f.write("=== Manual Testing Feedback ===\n")
                f.write(f"Timestamp: {self._get_timestamp()}\n")
                for key, value in self.feedback_data.items():
                    if value.strip():  # Only write non-empty values
                        f.write(f"{key}: {value}\n")
                f.write("\n" + "=" * 50 + "\n\n")

            self.notify(f"Feedback saved to {feedback_file}", severity="information")

        except Exception as e:
            self.notify(f"Failed to save feedback: {str(e)}", severity="error")

    def _clear_form(self) -> None:
        """Clear all form fields."""
        # Reset inputs
        for input_widget in self.query(Input):
            input_widget.value = ""

        # Reset radio sets
        for radio_set in self.query(RadioSet):
            radio_set.pressed_index = None

        # Reset checkboxes
        for checkbox in self.query(Checkbox):
            checkbox.value = False

        # Reset text areas
        for text_area in self.query(TextArea):
            text_area.text = ""

        self.notify("Form cleared", severity="information")

    def _collect_form_data(self) -> None:
        """Collect data from all form fields."""
        self.feedback_data = {}

        # Basic info
        self.feedback_data["Tester Name"] = self.query_one("#tester-name", Input).value
        self.feedback_data["Environment"] = self.query_one("#environment", Input).value

        # Ratings
        overall_rating = self.query_one("#overall-rating", RadioSet)
        self.feedback_data["Overall Rating"] = (
            overall_rating.pressed_button.label if overall_rating.pressed_button else ""
        )

        # Feature ratings
        features = [
            "navigation",
            "performance",
            "usability",
            "visual",
            "functionality",
            "error_handling",
        ]
        for feature in features:
            rating_set = self.query_one(f"#rating-{feature}", RadioSet)
            self.feedback_data[f"{feature.title()} Rating"] = (
                rating_set.pressed_button.label if rating_set.pressed_button else ""
            )

        # Issues
        issues_found = self.query_one("#issues-found", RadioSet)
        self.feedback_data["Issues Found"] = (
            issues_found.pressed_button.label if issues_found.pressed_button else ""
        )
        self.feedback_data["Issues Description"] = self.query_one(
            "#issues-description", TextArea
        ).text

        # Suggestions
        self.feedback_data["Feature Suggestions"] = self.query_one(
            "#feature-suggestions", TextArea
        ).text
        self.feedback_data["General Comments"] = self.query_one("#general-comments", TextArea).text

        # Testing scenarios
        scenarios = []
        scenario_ids = [
            "scenario-new-session",
            "scenario-quick-triage",
            "scenario-view-results",
            "scenario-command-palette",
            "scenario-settings",
            "scenario-error-handling",
        ]
        for scenario_id in scenario_ids:
            checkbox = self.query_one(f"#{scenario_id}", Checkbox)
            if checkbox.value:
                scenarios.append(scenario_id.replace("scenario-", "").replace("-", " ").title())

        self.feedback_data["Testing Scenarios"] = ", ".join(scenarios)

    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime

        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
