"""Landing view for the GUI application."""

from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from oroitz.core.session import Session, SessionManager


class LandingView(QWidget):
    """Landing view showing recent sessions and quick actions."""

    # Signals
    new_analysis_requested = Signal()
    session_selected = Signal(Session)

    def __init__(self, session_manager: Optional[SessionManager] = None) -> None:
        """Initialize the landing view."""
        super().__init__()

        self.session_manager = session_manager or SessionManager()
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the UI components."""
        layout = QVBoxLayout(self)

        # Welcome header with branding
        header_layout = QVBoxLayout()

        title = QLabel("🕵️ Oroitz")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 5px;
        """)
        header_layout.addWidget(title)

        subtitle = QLabel("Cross-platform Volatility 3 Memory Analysis")
        subtitle.setStyleSheet("""
            font-size: 14px;
            color: #7f8c8d;
            margin-bottom: 20px;
        """)
        header_layout.addWidget(subtitle)

        layout.addLayout(header_layout)

        # Quick actions section
        actions_group = QWidget()
        actions_group.setStyleSheet("""
            background-color: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        """)
        actions_layout = QVBoxLayout(actions_group)

        actions_title = QLabel("Get Started")
        actions_title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 15px;")
        actions_layout.addWidget(actions_title)

        new_analysis_btn = QPushButton("🔍 Start New Analysis")
        new_analysis_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                padding: 12px;
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        new_analysis_btn.clicked.connect(self._on_new_analysis)
        actions_layout.addWidget(new_analysis_btn)

        help_btn = QPushButton("📚 Help & Documentation")
        help_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                padding: 8px;
                background-color: transparent;
                color: #3498db;
                border: 1px solid #3498db;
                border-radius: 6px;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #ebf5fb;
            }
        """)
        help_btn.clicked.connect(self._on_help_clicked)
        actions_layout.addWidget(help_btn)

        layout.addWidget(actions_group)

        # Recent sessions section
        sessions_label = QLabel("Recent Analysis Sessions")
        sessions_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            margin-top: 20px;
            margin-bottom: 10px;
        """)
        layout.addWidget(sessions_label)

        self.sessions_list = QListWidget()
        self.sessions_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 6px;
                padding: 5px;
                background-color: white;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:hover {
                background-color: #f8f9fa;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
        """)
        self.sessions_list.itemDoubleClicked.connect(self._on_session_double_clicked)
        layout.addWidget(self.sessions_list)

        # Status bar
        self.status_label = QLabel("Ready to analyze memory images with Volatility 3")
        self.status_label.setStyleSheet("""
            font-size: 12px;
            color: #7f8c8d;
            margin-top: 15px;
            padding: 8px;
            background-color: #f8f9fa;
            border-radius: 4px;
        """)
        layout.addWidget(self.status_label)

        self.refresh_sessions()

    def refresh_sessions(self) -> None:
        """Refresh the sessions list."""
        self.sessions_list.clear()

        sessions = self.session_manager.list_sessions()
        if not sessions:
            item = QListWidgetItem("No recent sessions")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)  # Make it non-selectable
            self.sessions_list.addItem(item)
            return

        for session in sessions[:10]:  # Show last 10 sessions
            display_text = f"{session.name} - {session.created_at.strftime('%Y-%m-%d %H:%M')}"
            if session.image_path:
                display_text += f" - {session.image_path.name}"

            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, session)  # Store session object
            self.sessions_list.addItem(item)

    def _on_new_analysis(self) -> None:
        """Handle new analysis button click."""
        self.new_analysis_requested.emit()

    def _on_help_clicked(self) -> None:
        """Handle help button click."""
        # TODO: Open help/documentation dialog
        pass

    def _on_session_double_clicked(self, item: QListWidgetItem) -> None:
        """Handle session double-click."""
        session = item.data(Qt.ItemDataRole.UserRole)
        if session:
            self.session_selected.emit(session)
