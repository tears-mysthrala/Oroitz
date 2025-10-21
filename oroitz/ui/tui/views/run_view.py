"""Run View for Oroitz TUI."""

import asyncio
from typing import List, cast

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, ProgressBar, Static

from oroitz.core.executor import ExecutionResult, Executor
from oroitz.core.session import Session
from oroitz.core.workflow import WorkflowSpec

from ..widgets import Breadcrumb


class RunView(Screen):
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
                yield Breadcrumb(f"Home > {self.workflow.name} > Running")
                yield Static(f"Running: {self.workflow.name}", id="run-title")
                yield Static(f"Image: {self.session.image_path}", classes="image-info")
                yield Static(f"Profile: {self.session.profile}", classes="profile-info")

                yield ProgressBar(id="progress-bar", total=len(self.workflow.plugins))

                with VerticalScroll(id="log-container"):
                    yield Static("Execution Log:", id="log-title")
                    yield Static("", id="log-content")

                with Horizontal(id="run-buttons"):
                    yield Button("Cancel", id="cancel-button", variant="error")
                    yield Button(
                        "View Results", id="results-button", variant="primary", disabled=True
                    )

    async def on_mount(self) -> None:
        """Start execution when screen mounts."""
        await self._run_workflow()

    async def _run_workflow(self) -> None:
        """Execute the workflow asynchronously."""
        try:
            cast(Static, self.query_one("#log-content")).update("Starting workflow execution...\n")

            results = []
            total_plugins = len(self.workflow.plugins)

            for i, plugin_spec in enumerate(self.workflow.plugins):
                plugin_name = plugin_spec.name
                cast(Static, self.query_one("#log-content")).update(
                    f"Running plugin {i+1}/{total_plugins}: {plugin_name}\n"
                )

                # Execute plugin
                result = await asyncio.get_event_loop().run_in_executor(
                    None,
                    self.executor.execute_plugin,
                    plugin_name,
                    str(self.session.image_path),
                    self.session.profile or "windows",
                )

                results.append(result)

                # Update progress
                cast(ProgressBar, self.query_one("#progress-bar")).update(progress=i + 1)

                # Update log
                status = "✓" if result.success else "✗"
                log_update = f"{status} {plugin_name}: {result.duration:.2f}s"
                # Include retry/attempt info if available
                if getattr(result, "attempts", None):
                    log_update += f" (Attempts: {result.attempts})"
                if getattr(result, "used_mock", False):
                    log_update += " [FALLBACK: mock data used]"
                if not result.success and result.error:
                    log_update += f" (Error: {result.error})"
                current_log = str(cast(Static, self.query_one("#log-content")).renderable)
                cast(Static, self.query_one("#log-content")).update(current_log + log_update + "\n")

            self.results = results

            # Final log update
            successful = sum(1 for r in results if r.success)
            final_msg = f"\nWorkflow completed! {successful}/{total_plugins} plugins successful.\n"
            current_log = str(cast(Static, self.query_one("#log-content")).renderable)
            cast(Static, self.query_one("#log-content")).update(current_log + final_msg)
            cast(Button, self.query_one("#results-button")).disabled = False

        except Exception as e:
            error_msg = f"Workflow execution failed: {str(e)}"
            cast(Static, self.query_one("#log-content")).update(error_msg)
            self.notify(error_msg, severity="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "cancel-button":
            self.app.pop_screen()
        elif button_id == "results-button":
            from .results_view import ResultsView

            self.app.push_screen(ResultsView(self.workflow, self.session, self.results))
