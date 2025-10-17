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

        # Title
        title = QLabel("Oroitz - Cross-platform Volatility 3 Wrapper")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title)

        # Quick actions
        actions_layout = QHBoxLayout()

        new_analysis_btn = QPushButton("New Analysis")
        new_analysis_btn.setStyleSheet("font-size: 14px; padding: 10px;")
        new_analysis_btn.clicked.connect(self._on_new_analysis)
        actions_layout.addWidget(new_analysis_btn)

        actions_layout.addStretch()
        layout.addLayout(actions_layout)

        # Recent sessions
        sessions_label = QLabel("Recent Sessions")
        sessions_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 20px;")
        layout.addWidget(sessions_label)

        self.sessions_list = QListWidget()
        self.sessions_list.itemDoubleClicked.connect(self._on_session_double_clicked)
        layout.addWidget(self.sessions_list)

        # Refresh sessions
        self.refresh_sessions()

    def refresh_sessions(self) -> None:
        """Refresh the sessions list."""
        self.sessions_list.clear()

        sessions = self.session_manager.list_sessions()
        if not sessions:
            item = QListWidgetItem("No recent sessions")
            item.setFlags(item.flags() & ~Qt.ItemIsSelectable)  # Make it non-selectable
            self.sessions_list.addItem(item)
            return

        for session in sessions[:10]:  # Show last 10 sessions
            display_text = f"{session.name} - {session.created_at.strftime('%Y-%m-%d %H:%M')}"
            if session.image_path:
                display_text += f" - {session.image_path.name}"

            item = QListWidgetItem(display_text)
            item.setData(Qt.UserRole, session)  # Store session object
            self.sessions_list.addItem(item)

    def _on_new_analysis(self) -> None:
        """Handle new analysis button click."""
        self.new_analysis_requested.emit()

    def _on_session_double_clicked(self, item: QListWidgetItem) -> None:
        """Handle session double-click."""
        session = item.data(Qt.UserRole)
        if session:
            self.session_selected.emit(session)
