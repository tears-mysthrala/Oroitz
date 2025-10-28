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
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                          stop:0 #0f0f23, stop:1 #1a1a2e);
        color: #f1f1f1;
        font-family: "Segoe UI", sans-serif;
        font-size: 10pt;
        border-radius: 4px;
    }

    QMainWindow {
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                          stop:0 #0f0f23, stop:1 #1a1a2e);
    }

    QMenuBar {
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #2d1b69, stop:1 #1a1a2e);
        border-bottom: 1px solid rgba(157, 78, 221, 0.5);
        border-radius: 0px;
    }

    QMenuBar::item {
        background-color: transparent;
        padding: 6px 12px;
        border-radius: 4px;
        margin: 2px;
    }

    QMenuBar::item:selected {
        background-color: rgba(157, 78, 221, 0.3);
        border: 1px solid rgba(157, 78, 221, 0.6);
    }

    QMenuBar::item:pressed {
        background-color: rgba(157, 78, 221, 0.5);
    }

    QMenu {
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #2d1b69, stop:1 #1a1a2e);
        border: 1px solid rgba(157, 78, 221, 0.5);
        border-radius: 6px;
        padding: 4px;
    }

    QMenu::item {
        padding: 6px 20px;
        border-radius: 4px;
        margin: 2px 4px;
    }

    QMenu::item:selected {
        background-color: rgba(157, 78, 221, 0.4);
        border: 1px solid rgba(157, 78, 221, 0.7);
    }

    QPushButton {
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #2d1b69, stop:1 #4c1d95);
        border: 1px solid rgba(157, 78, 221, 0.8);
        border-radius: 6px;
        padding: 8px 16px;
        color: #f1f1f1;
        font-weight: bold;
    }

    QPushButton:hover {
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #4c1d95, stop:1 #7c3aed);
        border-color: rgba(157, 78, 221, 1.0);
    }

    QPushButton:pressed {
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #1a1a2e, stop:1 #2d1b69);
        border-color: rgba(157, 78, 221, 0.6);
    }

    QPushButton:disabled {
        background-color: rgba(45, 45, 48, 0.8);
        color: rgba(241, 241, 241, 0.5);
        border-color: rgba(85, 85, 85, 0.5);
    }

    QLineEdit, QComboBox, QSpinBox {
        background-color: rgba(45, 45, 48, 0.9);
        border: 1px solid rgba(157, 78, 221, 0.5);
        border-radius: 6px;
        padding: 6px 10px;
        color: #f1f1f1;
        selection-background-color: rgba(157, 78, 221, 0.6);
    }

    QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
        border-color: rgba(157, 78, 221, 1.0);
        box-shadow: 0 0 0 2px rgba(157, 78, 221, 0.3);
    }

    QComboBox::drop-down {
        border: none;
        background-color: rgba(157, 78, 221, 0.2);
        border-radius: 3px;
    }

    QComboBox::down-arrow {
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 4px solid #f1f1f1;
        margin-right: 6px;
    }

    QListWidget {
        background-color: rgba(45, 45, 48, 0.9);
        border: 1px solid rgba(157, 78, 221, 0.5);
        border-radius: 6px;
        alternate-background-color: rgba(26, 26, 46, 0.8);
        selection-background-color: rgba(157, 78, 221, 0.4);
    }

    QListWidget::item {
        padding: 6px;
        border-bottom: 1px solid rgba(85, 85, 85, 0.3);
        border-radius: 3px;
    }

    QListWidget::item:selected {
        background-color: rgba(157, 78, 221, 0.6);
        color: #ffffff;
        border: 1px solid rgba(157, 78, 221, 0.8);
    }

    QListWidget::item:hover {
        background-color: rgba(157, 78, 221, 0.2);
    }

    QTableWidget {
        background-color: rgba(45, 45, 48, 0.9);
        border: 1px solid rgba(157, 78, 221, 0.5);
        border-radius: 6px;
        gridline-color: rgba(157, 78, 221, 0.3);
        selection-background-color: rgba(157, 78, 221, 0.4);
    }

    QTableWidget::item {
        padding: 6px;
        border-bottom: 1px solid rgba(85, 85, 85, 0.2);
        border-radius: 2px;
    }

    QTableWidget::item:selected {
        background-color: rgba(157, 78, 221, 0.6);
        color: #ffffff;
    }

    QTableWidget::item:hover {
        background-color: rgba(157, 78, 221, 0.2);
    }

    QHeaderView::section {
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #2d1b69, stop:1 #4c1d95);
        border: 1px solid rgba(157, 78, 221, 0.6);
        padding: 8px;
        font-weight: bold;
        color: #f1f1f1;
        border-radius: 4px;
        margin: 1px;
    }

    QHeaderView::section:hover {
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #4c1d95, stop:1 #7c3aed);
    }

    QTabWidget::pane {
        border: 1px solid rgba(157, 78, 221, 0.5);
        background-color: rgba(26, 26, 46, 0.9);
        border-radius: 6px;
    }

    QTabBar::tab {
        background-color: rgba(45, 27, 105, 0.8);
        border: 1px solid rgba(157, 78, 221, 0.4);
        padding: 10px 16px;
        margin-right: 2px;
        color: #f1f1f1;
        border-radius: 6px 6px 0 0;
        font-weight: bold;
    }

    QTabBar::tab:selected {
        background-color: rgba(26, 26, 46, 0.9);
        border-bottom: none;
        border-color: rgba(157, 78, 221, 0.8);
    }

    QTabBar::tab:hover {
        background-color: rgba(76, 29, 149, 0.8);
        border-color: rgba(157, 78, 221, 0.6);
    }

    QGroupBox {
        font-weight: bold;
        border: 1px solid rgba(157, 78, 221, 0.5);
        border-radius: 8px;
        margin-top: 1ex;
        background-color: rgba(45, 45, 48, 0.7);
        color: #f1f1f1;
    }

    QGroupBox::title {
        subcontrol-origin: margin;
        left: 12px;
        padding: 0 8px 0 8px;
        color: #9d4edd;
        font-weight: bold;
    }

    QWizard {
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                          stop:0 #0f0f23, stop:1 #1a1a2e);
    }

    QWizardPage {
        background-color: rgba(45, 45, 48, 0.9);
        border: 1px solid rgba(157, 78, 221, 0.5);
        border-radius: 8px;
    }

    QProgressBar {
        border: 1px solid rgba(157, 78, 221, 0.5);
        border-radius: 4px;
        text-align: center;
        background-color: rgba(45, 45, 48, 0.8);
    }

    QProgressBar::chunk {
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #9d4edd, stop:1 #7c3aed);
        border-radius: 3px;
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
