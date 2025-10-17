"""Results View for Oroitz TUI."""

from pathlib import Path
from typing import List

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, DataTable, Static

from oroitz.core.executor import ExecutionResult
from oroitz.core.output import OutputExporter, OutputNormalizer
from oroitz.core.session import Session
from oroitz.core.workflow import WorkflowSpec

from ..widgets import Breadcrumb


class ResultsView(Screen):
    """Screen for displaying and exporting analysis results."""

    BINDINGS = [
        ("h", "home", "Home"),
        ("escape", "back", "Back"),
        ("ctrl+c", "quit", "Quit"),
    ]

    def __init__(self, workflow: WorkflowSpec, session: Session, results: List[ExecutionResult]):
        super().__init__()
        self.workflow = workflow
        self.session = session
        self.results = results
        self.normalizer = OutputNormalizer()
        self.exporter = OutputExporter()

    def compose(self) -> ComposeResult:
        """Compose the results screen."""
        with Container(id="results-container"):
            with Vertical():
                yield Breadcrumb(f"Home > {self.workflow.name} > Results")
                yield Static(f"Results: {self.workflow.name}", id="results-title")
                yield Static(
                    f"Session: {self.session.image_path} ({self.session.profile})",
                    classes="session-info",
                )

                # Results summary
                summary = self._get_summary()
                yield Static(f"Summary: {summary}", id="summary")

                # Data table for results
                yield DataTable(id="results-table")

                with Horizontal(id="export-buttons"):
                    yield Button("Export JSON", id="export-json", variant="default")
                    yield Button("Export CSV", id="export-csv", variant="default")
                    yield Button("Back to Home", id="home-button", variant="primary")

    def on_mount(self) -> None:
        """Populate the results table when screen mounts."""
        self._populate_table()

    def _get_summary(self) -> str:
        """Get a summary of the results."""
        total = len(self.results)
        successful = sum(1 for r in self.results if r.success)
        return f"{successful}/{total} plugins completed successfully"

    def _populate_table(self) -> None:
        """Populate the results data table."""
        table = self.query_one("#results-table", DataTable)

        # Add columns
        table.add_columns("Plugin", "Status", "Duration", "Records", "Error")

        # Add rows
        for result in self.results:
            status = "Success" if result.success else "Failed"
            records = len(result.output) if result.output else 0
            error = result.error or ""

            table.add_row(result.plugin_name, status, ".2f", str(records), error)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "home-button":
            # Clear session and go back to home
            from .. import OroitzTUI
            if isinstance(self.app, OroitzTUI):
                self.app.set_current_session(None)
            self.app.pop_screen()
            self.app.pop_screen()
            self.app.pop_screen()  # Back to home
        elif button_id == "export-json":
            self._export_results("json")
        elif button_id == "export-csv":
            self._export_results("csv")

    def _export_results(self, format: str) -> None:
        """Export results in the specified format."""
        try:
            # Normalize outputs using the normalizer
            normalized_output = self.normalizer.normalize_quick_triage(self.results)

            # Export
            output_path = Path()
            if format == "json":
                output_path = Path(f"oroitz_results_{self.session.id}.json")
                self.exporter.export_json(normalized_output, output_path)
            elif format == "csv":
                output_path = Path(f"oroitz_results_{self.session.id}.csv")
                self.exporter.export_csv(normalized_output, output_path)

            self.notify(f"Results exported to {output_path}", severity="information")

        except Exception as e:
            self.notify(f"Export failed: {str(e)}", severity="error")