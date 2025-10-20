"""Notification center for displaying user notifications."""

from enum import Enum

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QMessageBox, QWidget


class NotificationType(Enum):
    """Types of notifications."""

    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


class NotificationCenter:
    """Centralized notification system for the GUI."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._queue = []

    def show_notification(self, message: str, notification_type: NotificationType = NotificationType.INFO,
                         parent: QWidget = None, auto_close: bool = True, duration: int = 3000) -> None:
        """Show a notification to the user."""
        if notification_type == NotificationType.ERROR:
            self._show_error_dialog(message, parent)
        elif notification_type == NotificationType.WARNING:
            self._show_warning_dialog(message, parent)
        else:
            # For info and success, use a simple message box that auto-closes
            self._show_info_dialog(message, notification_type, parent, auto_close, duration)

    def _show_info_dialog(self, message: str, notification_type: NotificationType,
                         parent: QWidget, auto_close: bool, duration: int) -> None:
        """Show an info/success dialog."""
        icon = QMessageBox.Icon.Information
        title = "Information"
        if notification_type == NotificationType.SUCCESS:
            title = "Success"
            icon = QMessageBox.Icon.Information  # Could use a custom icon

        msg_box = QMessageBox(parent)
        msg_box.setIcon(icon)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.setDefaultButton(QMessageBox.StandardButton.Ok)

        if auto_close:
            QTimer.singleShot(duration, msg_box.accept)

        msg_box.exec()

    def _show_warning_dialog(self, message: str, parent: QWidget) -> None:
        """Show a warning dialog."""
        QMessageBox.warning(parent, "Warning", message)

    def _show_error_dialog(self, message: str, parent: QWidget) -> None:
        """Show an error dialog."""
        QMessageBox.critical(parent, "Error", message)

    # Convenience methods
    def show_info(self, message: str, parent: QWidget = None) -> None:
        """Show an info notification."""
        self.show_notification(message, NotificationType.INFO, parent)

    def show_success(self, message: str, parent: QWidget = None) -> None:
        """Show a success notification."""
        self.show_notification(message, NotificationType.SUCCESS, parent)

    def show_warning(self, message: str, parent: QWidget = None) -> None:
        """Show a warning notification."""
        self.show_notification(message, NotificationType.WARNING, parent)

    def show_error(self, message: str, parent: QWidget = None) -> None:
        """Show an error notification."""
        self.show_notification(message, NotificationType.ERROR, parent)