"""TUI Screens for Oroitz."""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Static, DataTable, Input, Select, Label, ProgressBar
from textual import events
from typing import Optional, List, Dict, Any
import asyncio
from pathlib import Path

from oroitz.core.session import Session
from oroitz.core.workflow import registry, WorkflowSpec
from oroitz.core.executor import Executor, ExecutionResult
from oroitz.core.output import OutputNormalizer, OutputExporter


class HomeScreen(Screen):
    """Home screen with workflow selection."""

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("ctrl+c", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        """Compose the home screen."""
        with Container(id="home-container"):
            with Vertical():
                yield Static("🕵️ Oroitz - Cross-platform Volatility 3 Wrapper", id="title")
                yield Static("Select a workflow to begin analysis:", classes="subtitle")

                # Workflow buttons
                with Vertical(id="workflow-buttons"):
                    for workflow in registry.list():
                        yield Button(
                            f"{workflow.name}\n{workflow.description}",
                            id=f"workflow-{workflow.id}",
                            classes="workflow-button"
                        )

                yield Static("", id="spacer")
                yield Button("Exit", id="exit-button", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "exit-button":
            self.app.exit()
        elif button_id and button_id.startswith("workflow-"):
            workflow_id = button_id.replace("workflow-", "")
            workflow = registry.get(workflow_id)
            if workflow:
                self.app.push_screen(SessionWizardScreen(workflow))


class SessionWizardScreen(Screen):
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
                yield Static(f"Configure Session: {self.workflow.name}", id="wizard-title")
                yield Static(self.workflow.description, classes="description")

                with Vertical(id="form"):
                    yield Label("Memory Image Path:")
                    yield Input(placeholder="/path/to/memory/image.raw", id="image-path-input")

                    yield Label("Profile:")
                    yield Select(
                        [("windows", "Windows"), ("linux", "Linux"), ("mac", "macOS")],
                        id="profile-select"
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
        if not registry.validate_compatibility(self.workflow.id, self.profile):
            self.notify(f"Workflow not compatible with profile: {self.profile}", severity="error")
            return

        # Create session
        session = Session(image_path=str(self.image_path), profile=self.profile)
        self.app.set_current_session(session)

        # Start analysis
        self.app.push_screen(RunScreen(self.workflow, session))


class RunScreen(Screen):
    """Screen showing workflow execution progress."""

    BINDINGS = [
        ("escape", "back", "Back"),
        ("ctrl+c", "quit", "Quit"),
    ]

    def __init__(self, workflow: WorkflowSpec, session: Session):
        super().__init__()
        self.workflow = workflow
        self.session = session
        self.results: List[ExecutionResult] = []
        self.executor = Executor()

    def compose(self) -> ComposeResult:
        """Compose the run screen."""
        with Container(id="run-container"):
            with Vertical():
                yield Static(f"Running: {self.workflow.name}", id="run-title")
                yield Static(f"Image: {self.session.image_path}", classes="image-info")
                yield Static(f"Profile: {self.session.profile}", classes="profile-info")

                yield ProgressBar(id="progress-bar", total=len(self.workflow.plugins))

                with VerticalScroll(id="log-container"):
                    yield Static("Execution Log:", id="log-title")
                    yield Static("", id="log-content")

                with Horizontal(id="run-buttons"):
                    yield Button("Cancel", id="cancel-button", variant="error")
                    yield Button("View Results", id="results-button", variant="primary", disabled=True)

    async def on_mount(self) -> None:
        """Start execution when screen mounts."""
        await self._run_workflow()

    async def _run_workflow(self) -> None:
        """Execute the workflow asynchronously."""
        try:
            self.query_one("#log-content").update("Starting workflow execution...\n")

            results = []
            total_plugins = len(self.workflow.plugins)

            for i, plugin_spec in enumerate(self.workflow.plugins):
                plugin_name = plugin_spec.name
                self.query_one("#log-content").update(f"Running plugin {i+1}/{total_plugins}: {plugin_name}\n")

                # Execute plugin
                result = await asyncio.get_event_loop().run_in_executor(
                    None,
                    self.executor.execute_plugin,
                    plugin_name,
                    str(self.session.image_path),
                    self.session.profile
                )

                results.append(result)

                # Update progress
                self.query_one("#progress-bar").update(progress=i+1)

                # Update log
                status = "✓" if result.success else "✗"
                log_update = f"{status} {plugin_name}: {result.duration:.2f}s"
                if not result.success and result.error:
                    log_update += f" (Error: {result.error})"
                current_log = self.query_one("#log-content").renderable.plain
                self.query_one("#log-content").update(current_log + log_update + "\n")

            self.results = results

            # Final log update
            successful = sum(1 for r in results if r.success)
            final_msg = f"\nWorkflow completed! {successful}/{total_plugins} plugins successful.\n"
            current_log = self.query_one("#log-content").renderable.plain
            self.query_one("#log-content").update(current_log + final_msg)
            self.query_one("#results-button").disabled = False

        except Exception as e:
            error_msg = f"Workflow execution failed: {str(e)}"
            self.query_one("#log-content").update(error_msg)
            self.notify(error_msg, severity="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "cancel-button":
            self.app.pop_screen()
        elif button_id == "results-button":
            self.app.push_screen(ResultsScreen(self.workflow, self.session, self.results))


class ResultsScreen(Screen):
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
                yield Static(f"Results: {self.workflow.name}", id="results-title")
                yield Static(f"Session: {self.session.image_path} ({self.session.profile})", classes="session-info")

                # Results summary
                summary = self._get_summary()
                yield Static(f"Summary: {summary}", id="summary")

                # Data table for results
                yield DataTable(id="results-table")

                with Horizontal(id="export-buttons"):
                    yield Button("Export JSON", id="export-json", variant="secondary")
                    yield Button("Export CSV", id="export-csv", variant="secondary")
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

            table.add_row(
                result.plugin_name,
                status,
                ".2f",
                str(records),
                error
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "home-button":
            # Clear session and go back to home
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
            if format == "json":
                output_path = Path(f"oroitz_results_{self.session.id}.json")
                self.exporter.export_json(normalized_output, output_path)
            elif format == "csv":
                output_path = Path(f"oroitz_results_{self.session.id}.csv")
                self.exporter.export_csv(normalized_output, output_path)

            self.notify(f"Results exported to {output_path}", severity="success")

        except Exception as e:
            self.notify(f"Export failed: {str(e)}", severity="error")