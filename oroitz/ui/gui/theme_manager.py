"""Theme management for the GUI application."""

from enum import Enum

from PySide6.QtWidgets import QApplication


class Theme(Enum):
    """Available application themes."""

    SYSTEM = "system"
    LIGHT = "light"
    DARK = "dark"


class ThemeManager:
    """Manages application theming."""

    # Light theme stylesheet
    LIGHT_THEME = """
    QWidget {
        background-color: #f5f5f5;
        color: #333333;
        font-family: "Segoe UI", sans-serif;
        font-size: 10pt;
    }

    QMainWindow {
        background-color: #f5f5f5;
    }

    QMenuBar {
        background-color: #ffffff;
        border-bottom: 1px solid #e0e0e0;
    }

    QMenuBar::item {
        background-color: transparent;
        padding: 4px 8px;
    }

    QMenuBar::item:selected {
        background-color: #e6f3ff;
    }

    QMenu {
        background-color: #ffffff;
        border: 1px solid #cccccc;
    }

    QMenu::item {
        padding: 4px 20px;
    }

    QMenu::item:selected {
        background-color: #e6f3ff;
    }

    QPushButton {
        background-color: #ffffff;
        border: 1px solid #cccccc;
        border-radius: 4px;
        padding: 6px 12px;
        color: #333333;
    }

    QPushButton:hover {
        background-color: #f0f0f0;
        border-color: #999999;
    }

    QPushButton:pressed {
        background-color: #e6e6e6;
    }

    QPushButton:disabled {
        background-color: #f9f9f9;
        color: #999999;
        border-color: #e0e0e0;
    }

    QLineEdit, QComboBox, QSpinBox {
        background-color: #ffffff;
        border: 1px solid #cccccc;
        border-radius: 4px;
        padding: 4px 8px;
        color: #333333;
    }

    QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
        border-color: #0078d4;
    }

    QListWidget {
        background-color: #ffffff;
        border: 1px solid #cccccc;
        border-radius: 4px;
        alternate-background-color: #f9f9f9;
    }

    QListWidget::item {
        padding: 4px;
        border-bottom: 1px solid #f0f0f0;
    }

    QListWidget::item:selected {
        background-color: #e6f3ff;
        color: #333333;
    }

    QTableWidget {
        background-color: #ffffff;
        border: 1px solid #cccccc;
        gridline-color: #e0e0e0;
    }

    QTableWidget::item {
        padding: 4px;
        border-bottom: 1px solid #f0f0f0;
    }

    QTableWidget::item:selected {
        background-color: #e6f3ff;
    }

    QHeaderView::section {
        background-color: #f8f8f8;
        border: 1px solid #cccccc;
        padding: 6px;
        font-weight: bold;
    }

    QTabWidget::pane {
        border: 1px solid #cccccc;
        background-color: #ffffff;
    }

    QTabBar::tab {
        background-color: #f8f8f8;
        border: 1px solid #cccccc;
        padding: 8px 12px;
        margin-right: 2px;
    }

    QTabBar::tab:selected {
        background-color: #ffffff;
        border-bottom: none;
    }

    QTabBar::tab:hover {
        background-color: #f0f0f0;
    }

    QGroupBox {
        font-weight: bold;
        border: 1px solid #cccccc;
        border-radius: 4px;
        margin-top: 1ex;
    }

    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px 0 5px;
    }

    QWizard {
        background-color: #f5f5f5;
    }

    QWizardPage {
        background-color: #ffffff;
        border: 1px solid #cccccc;
        border-radius: 4px;
    }
    """

    # Dark theme stylesheet
    DARK_THEME = """
    QWidget {
        background-color: #2d2d30;
        color: #f1f1f1;
        font-family: "Segoe UI", sans-serif;
        font-size: 10pt;
    }

    QMainWindow {
        background-color: #2d2d30;
    }

    QMenuBar {
        background-color: #3c3c3c;
        border-bottom: 1px solid #555555;
    }

    QMenuBar::item {
        background-color: transparent;
        padding: 4px 8px;
    }

    QMenuBar::item:selected {
        background-color: #9d4edd;
    }

    QMenu {
        background-color: #3c3c3c;
        border: 1px solid #555555;
    }

    QMenu::item {
        padding: 4px 20px;
    }

    QMenu::item:selected {
        background-color: #9d4edd;
    }

    QPushButton {
        background-color: #3c3c3c;
        border: 1px solid #555555;
        border-radius: 4px;
        padding: 6px 12px;
        color: #f1f1f1;
    }

    QPushButton:hover {
        background-color: #505050;
        border-color: #777777;
    }

    QPushButton:pressed {
        background-color: #1e1e1e;
    }

    QPushButton:disabled {
        background-color: #2d2d30;
        color: #888888;
        border-color: #444444;
    }

    QLineEdit, QComboBox, QSpinBox {
        background-color: #3c3c3c;
        border: 1px solid #555555;
        border-radius: 4px;
        padding: 4px 8px;
        color: #f1f1f1;
    }

    QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
        border-color: #9d4edd;
    }

    QListWidget {
        background-color: #3c3c3c;
        border: 1px solid #555555;
        border-radius: 4px;
        alternate-background-color: #333333;
    }

    QListWidget::item {
        padding: 4px;
        border-bottom: 1px solid #444444;
    }

    QListWidget::item:selected {
        background-color: #9d4edd;
        color: #f1f1f1;
    }

    QTableWidget {
        background-color: #3c3c3c;
        border: 1px solid #555555;
        gridline-color: #555555;
    }

    QTableWidget::item {
        padding: 4px;
        border-bottom: 1px solid #444444;
    }

    QTableWidget::item:selected {
        background-color: #9d4edd;
    }

    QHeaderView::section {
        background-color: #404040;
        border: 1px solid #555555;
        padding: 6px;
        font-weight: bold;
        color: #f1f1f1;
    }

    QTabWidget::pane {
        border: 1px solid #555555;
        background-color: #3c3c3c;
    }

    QTabBar::tab {
        background-color: #404040;
        border: 1px solid #555555;
        padding: 8px 12px;
        margin-right: 2px;
        color: #f1f1f1;
    }

    QTabBar::tab:selected {
        background-color: #2d2d30;
        border-bottom: none;
    }

    QTabBar::tab:hover {
        background-color: #505050;
    }

    QGroupBox {
        font-weight: bold;
        border: 1px solid #555555;
        border-radius: 4px;
        margin-top: 1ex;
        color: #f1f1f1;
    }

    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px 0 5px;
    }

    QWizard {
        background-color: #2d2d30;
    }

    QWizardPage {
        background-color: #3c3c3c;
        border: 1px solid #555555;
        border-radius: 4px;
    }
    """

    _current_theme: Theme = Theme.SYSTEM

    @classmethod
    def set_theme(cls, theme: Theme) -> None:
        """Set the application theme."""
        cls._current_theme = theme

        app = QApplication.instance()
        if not app:
            return

        # QApplication.instance() may be typed as QCoreApplication by some
        # stubs; only call setStyleSheet when we actually have a QApplication
        # instance to satisfy static type checkers.
        if isinstance(app, QApplication):
            if theme == Theme.LIGHT:
                app.setStyleSheet(cls.LIGHT_THEME)
            elif theme == Theme.DARK:
                app.setStyleSheet(cls.DARK_THEME)
            else:  # SYSTEM
                app.setStyleSheet("")  # Reset to system default

    @classmethod
    def get_current_theme(cls) -> Theme:
        """Get the current theme."""
        return cls._current_theme
