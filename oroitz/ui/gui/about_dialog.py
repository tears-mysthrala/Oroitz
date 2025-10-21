"""About dialog for the Oroitz application."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    # QWidget not used directly here
)


class AboutDialog(QDialog):
    """Dialog showing information about the Oroitz application."""

    def __init__(self, parent=None) -> None:
        """Initialize the about dialog."""
        super().__init__(parent)

        self.setWindowTitle("About Oroitz")
        self.setModal(True)
        self.resize(500, 400)

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the UI components."""
        layout = QVBoxLayout(self)

        # Title
        title_label = QLabel("Oroitz")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #0078d4;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Subtitle
        subtitle_label = QLabel("Cross-platform Volatility 3 Wrapper")
        subtitle_label.setStyleSheet("font-size: 14px; color: #666666;")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle_label)

        # Version info
        version_label = QLabel("Version 0.0.1 (Beta)")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)

        # Description
        description_text = QTextEdit()
        description_text.setPlainText(
            "Oroitz is a cross-platform wrapper around Volatility 3 that delivers "
            "a shared Python core, a Textual-powered TUI, a PySide6 desktop GUI,"
            " and a CLI so analysts can run guided memory forensics workflows "
            "with minimal setup.\n\n"
            "Key Features:\n"
            "• Streamlines common Volatility investigations through a unified API\n"
            "• Normalizes plugin outputs into structured formats\n"
            "• Shares workflow logic across CLI, GUI, and TUI interfaces\n"
            "• Prioritizes extensibility for custom workflows and output targets\n\n"
            "Built with Python 3.11, PySide6, and Textual."
        )
        description_text.setReadOnly(True)
        description_text.setStyleSheet("border: none; background-color: transparent;")
        layout.addWidget(description_text)

        # Links
        links_layout = QVBoxLayout()
        github_label = QLabel(
            '<a href="https://github.com/tears-mysthrala/Oroitz">' "GitHub Repository</a>"
        )
        github_label.setOpenExternalLinks(True)
        links_layout.addWidget(github_label)
        docs_label = QLabel(
            '<a href="https://github.com/tears-mysthrala/Oroitz/blob/main/docs/">'
            "Documentation</a>"
        )
        docs_label.setOpenExternalLinks(True)
        links_layout.addWidget(docs_label)
        layout.addLayout(links_layout)

        # Button
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        ok_button.setDefault(True)
        button_layout.addWidget(ok_button)

        button_layout.addStretch()
        layout.addLayout(button_layout)
