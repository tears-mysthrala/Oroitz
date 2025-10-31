"""Results explorer for displaying and exporting analysis results."""

from pathlib import Path
from typing import List, cast

from PySide6.QtWidgets import (
    QAbstractItemView,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
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
        self.users_tab = self._create_table_tab("Users")
        self.hashes_tab = self._create_table_tab("Hashes")

        self.tab_widget.addTab(self.processes_tab, "Processes")
        self.tab_widget.addTab(self.network_tab, "Network")
        self.tab_widget.addTab(self.malfind_tab, "Malfind")
        self.tab_widget.addTab(self.users_tab, "Users")
        self.tab_widget.addTab(self.hashes_tab, "Hashes")

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
        # Use the SelectionBehavior enum for clearer type resolution
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.horizontalHeader().setStretchLastSection(True)
        # Use the ResizeMode enum member for explicitness
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)

        scroll_area = QScrollArea()
        scroll_area.setWidget(table)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        # Keep a direct reference to the table on the tab widget so callers
        # can retrieve it without navigating the layout (avoids Optional[...])
        # type issues when static analysis checks layout.itemAt(...)).
        setattr(widget, "_table", table)

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
        self._update_users_tab()
        self._update_hashes_tab()

    def _update_processes_tab(self) -> None:
        """Update the processes table."""
        if not self.normalized_data or not self.normalized_data.processes:
            self._clear_table(self.processes_tab)
            return

        # Retrieve the table we attached to the tab widget in
        # _create_table_tab(). This avoids optional layout lookups that
        # confuse static analysis.
        table = cast(QTableWidget, getattr(self.processes_tab, "_table"))
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

        table = cast(QTableWidget, getattr(self.network_tab, "_table"))
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

        table = cast(QTableWidget, getattr(self.malfind_tab, "_table"))
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

    def _update_users_tab(self) -> None:
        """Update the users table (from windows.getsids normalized data)."""
        if not self.normalized_data or not self.normalized_data.users:
            self._clear_table(self.users_tab)
            return

        table = cast(QTableWidget, getattr(self.users_tab, "_table"))
        users = self.normalized_data.users

        # Set up table
        table.setRowCount(len(users))
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Name", "SID", "PID", "Process"])

        # Populate table
        for row, user in enumerate(users):
            table.setItem(row, 0, QTableWidgetItem(user.name or ""))
            table.setItem(row, 1, QTableWidgetItem(user.sid or ""))
            table.setItem(row, 2, QTableWidgetItem(str(user.pid or "")))
            table.setItem(row, 3, QTableWidgetItem(user.process or ""))

        # Resize columns to content
        table.resizeColumnsToContents()

    def _update_hashes_tab(self) -> None:
        """Update the hashes table (if present)."""
        if not self.normalized_data or not self.normalized_data.hashes:
            self._clear_table(self.hashes_tab)
            return

        table = cast(QTableWidget, getattr(self.hashes_tab, "_table"))
        hashes = self.normalized_data.hashes

        # Set up table
        table.setRowCount(len(hashes))
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Username", "Hash Type", "Hash Value", "Note"])

        # Populate table
        for row, hash_info in enumerate(hashes):
            table.setItem(row, 0, QTableWidgetItem(hash_info.username or ""))
            table.setItem(row, 1, QTableWidgetItem(hash_info.hash_type or ""))
            table.setItem(row, 2, QTableWidgetItem(hash_info.hash_value or ""))
            table.setItem(row, 3, QTableWidgetItem(hash_info.note or ""))

        # Resize columns to content
        table.resizeColumnsToContents()

    def _clear_table(self, tab_widget: QWidget) -> None:
        """Clear a table widget."""
        table = cast(QTableWidget, getattr(tab_widget, "_table"))
        table.setRowCount(0)
        table.setColumnCount(0)

    def _filter_table(self, tab_title: str, filter_text: str) -> None:
        """Filter the table based on search text."""
        if tab_title == "Processes":
            table = cast(QTableWidget, getattr(self.processes_tab, "_table"))
        elif tab_title == "Network Connections":
            table = cast(QTableWidget, getattr(self.network_tab, "_table"))
        elif tab_title == "Malfind Results":
            table = cast(QTableWidget, getattr(self.malfind_tab, "_table"))
        elif tab_title == "Users":
            table = cast(QTableWidget, getattr(self.users_tab, "_table"))
        elif tab_title == "Hashes":
            table = cast(QTableWidget, getattr(self.hashes_tab, "_table"))
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
