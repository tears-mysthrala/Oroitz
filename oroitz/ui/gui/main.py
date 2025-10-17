"""PySide6 GUI application entry point."""

import sys

from PySide6.QtWidgets import QApplication

from oroitz.core.telemetry import setup_logging
from oroitz.ui.gui.main_window import MainWindow
from oroitz.ui.gui.theme_manager import ThemeManager


def main() -> None:
    """Launch the PySide6 GUI application."""
    setup_logging()

    app = QApplication(sys.argv)
    app.setApplicationName("Oroitz")
    app.setApplicationVersion("0.0.1")
    app.setOrganizationName("Tears Workshop")

    # Initialize theme
    ThemeManager.set_theme(ThemeManager.get_current_theme())

    # Set application icon if available
    # app.setWindowIcon(QIcon("resources/icons/app.png"))

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
