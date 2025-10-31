"""Results View for Oroitz TUI."""

from pathlib import Path
from typing import List

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, DataTable, Static, TabbedContent, TabPane

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
                    f"Session: {self.session.image_path}",
                    classes="session-info",
                )

                # Results summary
                summary = self._get_summary()
                yield Static(f"Summary: {summary}", id="summary")

                # Tabbed results interface
                with TabbedContent():
                    with TabPane("Overview", id="overview-tab"):
                        yield DataTable(id="overview-table")

                    with TabPane("Processes", id="processes-tab"):
                        yield DataTable(id="processes-table")

                    with TabPane("Network", id="network-tab"):
                        yield DataTable(id="network-table")

                    with TabPane("Users", id="users-tab"):
                        yield DataTable(id="users-table")

                    with TabPane("DLLs", id="dlls-tab"):
                        yield DataTable(id="dlls-table")

                    with TabPane("Timeline", id="timeline-tab"):
                        yield DataTable(id="timeline-table")

                with Horizontal(id="export-buttons"):
                    yield Button("Export JSON", id="export-json", variant="default")
                    yield Button("Export CSV", id="export-csv", variant="default")
                    yield Button("Back to Home", id="home-button", variant="primary")

    def on_mount(self) -> None:
        """Populate the results tables when screen mounts."""
        # Defer population until after initial layout to ensure widgets exist
        self.call_after_refresh(self._populate_tables)

    def _get_summary(self) -> str:
        """Get a summary of the results."""
        total = len(self.results)
        successful = sum(1 for r in self.results if r.success)
        total_time = sum(r.duration for r in self.results)
        return f"{successful}/{total} plugins completed successfully in {total_time:.2f}s"

    def _populate_tables(self) -> None:
        """Populate all results tables."""
        # Overview tab - plugin execution results
        overview_table = self.query_one("#overview-table", DataTable)
        overview_table.add_columns("Plugin", "Status", "Duration", "Records", "Error")
        for result in self.results:
            status = "Success" if result.success else "Failed"
            records = len(result.output) if result.output else 0
            error = result.error or ""
            overview_table.add_row(
                result.plugin_name, status, f"{result.duration:.2f}", str(records), error
            )

        # For now, populate other tabs with mock data based on plugin types
        # In a real implementation, this would parse the actual output data
        self._populate_processes_tab()
        self._populate_network_tab()
        self._populate_users_tab()
        self._populate_dlls_tab()
        self._populate_timeline_tab()

    def _populate_processes_tab(self) -> None:
        """Populate processes tab with process-related data."""
        table = self.query_one("#processes-table", DataTable)
        table.add_columns("PID", "Name", "PPID", "Threads", "Handles", "Create Time")

        # Get data from pslist or psscan plugin results
        # (check both since different workflows use different plugins)
        process_results = {}

        # Try pslist first (used in quick triage)
        pslist_result = next(
            (r for r in self.results if r.plugin_name == "windows.pslist" and r.output), None
        )
        if pslist_result and pslist_result.output:
            for process in pslist_result.output:
                pid = process.get("PID")
                if pid is not None:
                    process_results[pid] = process

        # Try psscan (used in deep dive)
        psscan_result = next(
            (r for r in self.results if r.plugin_name == "windows.psscan" and r.output), None
        )
        if psscan_result and psscan_result.output:
            for process in psscan_result.output:
                pid = process.get("PID")
                if pid is not None:
                    process_results[pid] = process  # Overwrite if duplicate, prefer psscan if both

        if process_results:
            for process in process_results.values():  # Show all unique processes
                table.add_row(
                    str(process.get("PID", "")),
                    process.get("ImageFileName", ""),
                    str(process.get("PPID", "")),
                    str(process.get("Threads", "")),
                    str(process.get("Handles", "")),
                    process.get("CreateTime", ""),
                )
        else:
            # Fallback to mock data if no real data
            mock_processes = [
                ("4", "System", "0", "100", "500", "2023-01-01T00:00:00Z"),
                ("1234", "notepad.exe", "876", "8", "150", "2023-01-01T12:00:00Z"),
            ]
            for pid, name, ppid, threads, handles, create_time in mock_processes:
                table.add_row(pid, name, ppid, threads, handles, create_time)

    def _populate_network_tab(self) -> None:
        """Populate network tab with network-related data."""
        table = self.query_one("#network-table", DataTable)
        table.add_columns("Local Address", "Remote Address", "State", "PID", "Process")

        # Get data from netscan plugin results
        netscan_result = next(
            (r for r in self.results if r.plugin_name == "windows.netscan" and r.output), None
        )
        if netscan_result and netscan_result.output:
            for conn in netscan_result.output:  # Show all connections
                local = f"{conn.get('LocalAddr', '')}:{conn.get('LocalPort', '')}"
                remote = f"{conn.get('ForeignAddr', '')}:{conn.get('ForeignPort', '')}"
                table.add_row(
                    local,
                    remote,
                    conn.get("State", ""),
                    str(conn.get("PID", "")),
                    conn.get("Owner", ""),
                )
        else:
            # Fallback to mock data
            mock_connections = [
                ("192.168.1.100:12345", "8.8.8.8:53", "ESTABLISHED", "1234", "notepad.exe"),
            ]
            for local, remote, state, pid, process in mock_connections:
                table.add_row(local, remote, state, pid, process)

    def _populate_users_tab(self) -> None:
        """Populate users tab with data from windows.getsids."""
        table = self.query_one("#users-table", DataTable)
        table.add_columns("Name", "SID", "PID", "Process")

        users_result = next(
            (r for r in self.results if r.plugin_name == "windows.getsids" and r.output), None
        )

        if users_result and users_result.output:
            for user in users_result.output:
                table.add_row(
                    str(user.get("Name", "")),
                    str(user.get("SID", "")),
                    str(user.get("PID", "")),
                    str(user.get("Process", "")),
                )

    def _populate_dlls_tab(self) -> None:
        """Populate DLLs tab with DLL-related data."""
        table = self.query_one("#dlls-table", DataTable)
        table.add_columns("Process", "DLL Name", "Base Address", "Size")

        # Get data from dlllist plugin results
        dlllist_result = next(
            (r for r in self.results if r.plugin_name == "windows.dlllist" and r.output), None
        )
        if dlllist_result and dlllist_result.output:
            for dll in dlllist_result.output:  # Show all DLLs
                table.add_row(
                    dll.get("Process", ""),
                    dll.get("Name", ""),
                    dll.get("Base", ""),
                    str(dll.get("Size", "")),
                )
        else:
            # Fallback to mock data
            mock_dlls = [
                ("notepad.exe", "kernel32.dll", "0x77400000", "0x1000"),
                ("notepad.exe", "user32.dll", "0x75e00000", "0x800"),
            ]
            for process, dll, base, size in mock_dlls:
                table.add_row(process, dll, base, size)

    def _populate_timeline_tab(self) -> None:
        """Populate timeline tab with temporal data."""
        table = self.query_one("#timeline-table", DataTable)
        table.add_columns("Timestamp", "Event", "Process", "Details")

        # Get data from timeliner plugin results
        timeliner_result = next(
            (r for r in self.results if r.plugin_name == "windows.timeliner" and r.output), None
        )
        if timeliner_result and timeliner_result.output:
            for event in timeliner_result.output:  # Show all events
                table.add_row(
                    event.get("CreatedDate", ""),
                    event.get("Plugin", ""),
                    "",  # Process not directly available
                    event.get("Description", ""),
                )
        else:
            # Fallback to mock data
            mock_events = [
                ("2023-01-01T12:00:00Z", "Process Create", "notepad.exe", "PID 1234 created"),
                (
                    "2023-01-01T12:00:05Z",
                    "Network Connect",
                    "notepad.exe",
                    "Connected to 8.8.8.8:53",
                ),
            ]
            for timestamp, event, process, details in mock_events:
                table.add_row(timestamp, event, process, details)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "home-button":
            # Clear session and go back to home - better navigation
            from .. import OroitzTUI

            if isinstance(self.app, OroitzTUI):
                self.app.set_current_session(None)
            # Pop back to home screen (should be 3 screens back: results -> run -> wizard -> home)
            for _ in range(3):
                if self.app.screen_stack:
                    self.app.pop_screen()
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
                self.notify(f"✅ Results exported to {output_path}", severity="information")
            elif format == "csv":
                output_path = Path(f"oroitz_results_{self.session.id}.csv")
                self.exporter.export_csv(normalized_output, output_path)
                self.notify(f"✅ Results exported to {output_path}", severity="information")

        except Exception as e:
            self.notify(f"❌ Export failed: {str(e)}", severity="error")
