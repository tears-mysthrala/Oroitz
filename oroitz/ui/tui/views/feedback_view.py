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
                    # Note: some Textual versions/type stubs do not accept a
                    # `placeholder` keyword in the constructor. To remain
                    # compatible with the type checker we set placeholders in
                    # `on_mount` using setattr rather than passing them here.
                    yield Input(id="tester-name")

                    yield Label("Testing Environment:")
                    yield Input(id="environment")

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
                    yield TextArea(id="issues-description")

                    # Suggestions
                    yield Static("Suggestions for Improvement", classes="section-header")
                    yield Label("What features would you like to see added?")
                    yield TextArea(id="feature-suggestions")

                    yield Label("Any other comments or feedback:")
                    yield TextArea(id="general-comments")

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

    def on_mount(self) -> None:
        """Set up widget placeholders after the screen is mounted.

        Some Textual versions do not accept a `placeholder` constructor
        keyword; setting the attribute after construction using setattr is a
        safe, type-checker-friendly approach that avoids call-time
        diagnostics from Pylance.
        """
        placeholders = {
            "#tester-name": (Input, "Enter your name"),
            "#environment": (Input, "OS, Terminal, Python version, etc."),
            "#issues-description": (
                TextArea,
                "Describe bugs, crashes, confusing UI elements, etc.",
            ),
            "#feature-suggestions": (TextArea, "New features, improvements, etc."),
            "#general-comments": (TextArea, "General comments, praise, concerns, etc."),
        }

        for selector, (widget_type, text) in placeholders.items():
            try:
                widget = self.query_one(selector, widget_type)
                # Use setattr to avoid static attribute checks on some stubs.
                setattr(widget, "placeholder", text)
            except Exception:
                # If placeholder isn't supported by the widget implementation
                # or the widget isn't present yet, fail silently.
                pass

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
            # Some RadioSet implementations expose read-only properties for
            # selection state (e.g. pressed_index). Avoid assigning to those
            # properties; instead try to clear the selection by un-pressing
            # any pressed child buttons in a defensive way.
            try:
                pressed_btn = getattr(radio_set, "pressed_button", None)
                if pressed_btn is not None:
                    # Try common attribute names that indicate a pressed/toggled
                    # state and clear them dynamically.
                    for attr in ("pressed", "value", "active", "toggled"):
                        if hasattr(pressed_btn, attr):
                            try:
                                setattr(pressed_btn, attr, False)
                            except Exception:
                                pass

                # Also iterate over child buttons and clear them explicitly.
                for btn in radio_set.query(Button):
                    for attr in ("pressed", "value", "active", "toggled"):
                        if hasattr(btn, attr):
                            try:
                                setattr(btn, attr, False)
                            except Exception:
                                pass
            except Exception:
                # Defensive: if the RadioSet API differs, don't let clearing
                # the form crash the app.
                pass

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
        tester_value = self.query_one("#tester-name", Input).value
        env_value = self.query_one("#environment", Input).value
        self.feedback_data["Tester Name"] = str(tester_value) if tester_value is not None else ""
        self.feedback_data["Environment"] = str(env_value) if env_value is not None else ""

        # Ratings
        overall_rating = self.query_one("#overall-rating", RadioSet)
        overall_label = overall_rating.pressed_button.label if overall_rating.pressed_button else ""
        self.feedback_data["Overall Rating"] = str(overall_label)

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
            rating_label = rating_set.pressed_button.label if rating_set.pressed_button else ""
            self.feedback_data[f"{feature.title()} Rating"] = str(rating_label)

        # Issues
        issues_found = self.query_one("#issues-found", RadioSet)
        issues_label = issues_found.pressed_button.label if issues_found.pressed_button else ""
        self.feedback_data["Issues Found"] = str(issues_label)
        issues_desc = self.query_one("#issues-description", TextArea).text
        self.feedback_data["Issues Description"] = (
            str(issues_desc) if issues_desc is not None else ""
        )

        # Suggestions
        feature_suggestions = self.query_one("#feature-suggestions", TextArea).text
        general_comments = self.query_one("#general-comments", TextArea).text
        self.feedback_data["Feature Suggestions"] = (
            str(feature_suggestions) if feature_suggestions is not None else ""
        )
        self.feedback_data["General Comments"] = (
            str(general_comments) if general_comments is not None else ""
        )

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
