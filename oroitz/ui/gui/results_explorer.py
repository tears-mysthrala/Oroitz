"""Results explorer for displaying and exporting analysis results."""

from pathlib import Path
from typing import List

from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from oroitz.core.executor import ExecutionResult
from oroitz.core.output import OutputExporter, OutputNormalizer
from oroitz.ui.gui.notification_center import NotificationCenter


class ResultsExplorer(QWidget):
    """Widget for exploring and exporting analysis results."""

    def __init__(self) -> None:
        """Initialize the results explorer."""
        super().__init__()

        self.results: List[ExecutionResult] = []
        self.normalized_data = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the UI components."""
        layout = QVBoxLayout(self)

        # Export buttons
        export_layout = QHBoxLayout()

        self.export_json_btn = QPushButton("Export JSON")
        self.export_json_btn.clicked.connect(self._export_json)
        export_layout.addWidget(self.export_json_btn)

        self.export_csv_btn = QPushButton("Export CSV")
        self.export_csv_btn.clicked.connect(self._export_csv)
        export_layout.addWidget(self.export_csv_btn)

        export_layout.addStretch()
        layout.addLayout(export_layout)

        # Tab widget for different result types
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # Create tabs
        self.processes_tab = self._create_table_tab("Processes")
        self.network_tab = self._create_table_tab("Network Connections")
        self.malfind_tab = self._create_table_tab("Malfind Results")

        self.tab_widget.addTab(self.processes_tab, "Processes")
        self.tab_widget.addTab(self.network_tab, "Network")
        self.tab_widget.addTab(self.malfind_tab, "Malfind")

    def _create_table_tab(self, title: str) -> QWidget:
        """Create a tab with a table widget."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Search box
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        search_edit = QLineEdit()
        search_edit.setPlaceholderText("Filter results...")
        search_edit.textChanged.connect(lambda text, t=title: self._filter_table(t, text))
        search_layout.addWidget(search_edit)
        layout.addLayout(search_layout)

        table = QTableWidget()
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)

        layout.addWidget(table)
        return widget

    def set_results(self, results: List[ExecutionResult]) -> None:
        """Set the execution results to display."""
        self.results = results

        # Normalize the results
        normalizer = OutputNormalizer()
        self.normalized_data = normalizer.normalize_quick_triage(results)

        # Update all tabs
        self._update_processes_tab()
        self._update_network_tab()
        self._update_malfind_tab()

    def _update_processes_tab(self) -> None:
        """Update the processes table."""
        if not self.normalized_data or not self.normalized_data.processes:
            self._clear_table(self.processes_tab)
            return

        table = self.processes_tab.layout().itemAt(1).widget()
        processes = self.normalized_data.processes

        # Set up table
        table.setRowCount(len(processes))
        table.setColumnCount(8)
        table.setHorizontalHeaderLabels(
            ["PID", "Name", "PPID", "Threads", "Handles", "Session", "Wow64", "Anomalies"]
        )

        # Populate table
        for row, process in enumerate(processes):
            table.setItem(row, 0, QTableWidgetItem(str(process.pid)))
            table.setItem(row, 1, QTableWidgetItem(process.name))
            table.setItem(row, 2, QTableWidgetItem(str(process.ppid or "")))
            table.setItem(row, 3, QTableWidgetItem(str(process.threads or "")))
            table.setItem(row, 4, QTableWidgetItem(str(process.handles or "")))
            table.setItem(row, 5, QTableWidgetItem(str(process.session or "")))
            table.setItem(row, 6, QTableWidgetItem(str(process.wow64 or "")))
            table.setItem(
                row, 7, QTableWidgetItem(", ".join(process.anomalies) if process.anomalies else "")
            )

        # Resize columns to content
        table.resizeColumnsToContents()

    def _update_network_tab(self) -> None:
        """Update the network connections table."""
        if not self.normalized_data or not self.normalized_data.network_connections:
            self._clear_table(self.network_tab)
            return

        table = self.network_tab.layout().itemAt(1).widget()
        connections = self.normalized_data.network_connections

        # Set up table
        table.setRowCount(len(connections))
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels(
            ["PID", "Owner", "Local Address", "Remote Address", "State", "Created"]
        )

        # Populate table
        for row, conn in enumerate(connections):
            table.setItem(row, 0, QTableWidgetItem(str(conn.pid or "")))
            table.setItem(row, 1, QTableWidgetItem(conn.owner or ""))
            table.setItem(row, 2, QTableWidgetItem(conn.local_addr or ""))
            table.setItem(row, 3, QTableWidgetItem(conn.remote_addr or ""))
            table.setItem(row, 4, QTableWidgetItem(conn.state or ""))
            table.setItem(row, 5, QTableWidgetItem(conn.created or ""))

        # Resize columns to content
        table.resizeColumnsToContents()

    def _update_malfind_tab(self) -> None:
        """Update the malfind results table."""
        if not self.normalized_data or not self.normalized_data.malfind_hits:
            self._clear_table(self.malfind_tab)
            return

        table = self.malfind_tab.layout().itemAt(1).widget()
        hits = self.normalized_data.malfind_hits

        # Set up table
        table.setRowCount(len(hits))
        table.setColumnCount(8)
        table.setHorizontalHeaderLabels(
            ["PID", "Process Name", "Start", "End", "Tag", "Protection", "Commit", "Private"]
        )

        # Populate table
        for row, hit in enumerate(hits):
            table.setItem(row, 0, QTableWidgetItem(str(hit.pid)))
            table.setItem(row, 1, QTableWidgetItem(hit.process_name or ""))
            table.setItem(row, 2, QTableWidgetItem(hit.start or ""))
            table.setItem(row, 3, QTableWidgetItem(hit.end or ""))
            table.setItem(row, 4, QTableWidgetItem(hit.tag or ""))
            table.setItem(row, 5, QTableWidgetItem(hit.protection or ""))
            table.setItem(row, 6, QTableWidgetItem(str(hit.commit_charge or "")))
            table.setItem(row, 7, QTableWidgetItem(str(hit.private_memory or "")))

        # Resize columns to content
        table.resizeColumnsToContents()

    def _clear_table(self, tab_widget: QWidget) -> None:
        """Clear a table widget."""
        table = tab_widget.layout().itemAt(1).widget()
        table.setRowCount(0)
        table.setColumnCount(0)

    def _filter_table(self, tab_title: str, filter_text: str) -> None:
        """Filter the table based on search text."""
        if tab_title == "Processes":
            table = self.processes_tab.layout().itemAt(1).widget()
            data = self.normalized_data.processes if self.normalized_data else []
        elif tab_title == "Network Connections":
            table = self.network_tab.layout().itemAt(1).widget()
            data = self.normalized_data.network_connections if self.normalized_data else []
        elif tab_title == "Malfind Results":
            table = self.malfind_tab.layout().itemAt(1).widget()
            data = self.normalized_data.malfind_hits if self.normalized_data else []
        else:
            return

        if not filter_text:
            # Show all rows
            for row in range(table.rowCount()):
                table.setRowHidden(row, False)
            return

        # Filter rows
        filter_lower = filter_text.lower()
        for row in range(table.rowCount()):
            visible = False
            for col in range(table.columnCount()):
                item = table.item(row, col)
                if item and filter_lower in item.text().lower():
                    visible = True
                    break
            table.setRowHidden(row, not visible)

    def _export_json(self) -> None:
        """Export results to JSON."""
        if not self.normalized_data:
            return

        # Show file dialog for export location
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Results to JSON",
            "oroitz_results.json",
            "JSON Files (*.json);;All Files (*)",
        )

        if not file_path:
            return

        export_path = Path(file_path)
        exporter = OutputExporter()
        exporter.export_json(self.normalized_data, export_path)

        NotificationCenter().show_success(f"Results exported to {export_path}", self)

    def _export_csv(self) -> None:
        """Export results to CSV."""
        if not self.normalized_data:
            return

        # Show directory dialog for export location (CSV creates multiple files)
        directory = QFileDialog.getExistingDirectory(self, "Select Directory for CSV Export", "")

        if not directory:
            return

        export_path = Path(directory) / "oroitz_results.csv"
        exporter = OutputExporter()
        exporter.export_csv(self.normalized_data, export_path)

        NotificationCenter().show_success(f"Results exported to CSV files in {directory}", self)
