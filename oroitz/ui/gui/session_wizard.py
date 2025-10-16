"""Session wizard for creating new analysis sessions."""

from pathlib import Path
from typing import Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
    QWizard,
    QWizardPage,
)

from oroitz.core.session import Session, SessionManager
from oroitz.core.workflow import registry


class SessionWizard(QWizard):
    """Wizard for creating new analysis sessions."""

    # Signals
    session_created = Signal(Session)
    cancelled = Signal()

    def __init__(self, session_manager: Optional[SessionManager] = None) -> None:
        """Initialize the session wizard."""
        super().__init__()

        self.session_manager = session_manager or SessionManager()
        self.selected_workflow_id = None

        self.setWindowTitle("New Analysis Session")
        self.setWizardStyle(QWizard.ModernStyle)

        # Add pages
        self.workflow_page = WorkflowSelectionPage()
        self.addPage(SessionInfoPage())
        self.addPage(ImageSelectionPage())
        self.addPage(self.workflow_page)
        self.addPage(SummaryPage())

        # Connect signals
        self.finished.connect(self._on_finished)
        self.rejected.connect(self._on_cancelled)

    def _on_finished(self, result: int) -> None:
        """Handle wizard completion."""
        if result == QWizard.Accepted:
            # Create session from wizard data
            session_name = self.field("sessionName")
            image_path = self.field("imagePath")
            profile = self.field("profile")
            workflow_id = self.selected_workflow_id

            session = self.session_manager.create_session(
                name=session_name,
                image_path=Path(image_path) if image_path else None,
                profile=profile,
                workflow_id=workflow_id
            )

            # Store workflow selection in session (extend Session model later)
            # session.workflow_id = workflow_id  # type: ignore

            self.session_created.emit(session)

    def _on_cancelled(self) -> None:
        """Handle wizard cancellation."""
        self.cancelled.emit()


class SessionInfoPage(QWizardPage):
    """Page for basic session information."""

    def __init__(self) -> None:
        """Initialize the session info page."""
        super().__init__()
        self.setTitle("Session Information")
        self.setSubTitle("Enter basic information for your analysis session.")

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the UI."""
        layout = QFormLayout(self)

        name_edit = QLineEdit("New Analysis Session")
        self.registerField("sessionName*", name_edit)
        layout.addRow("Session Name:", name_edit)


class ImageSelectionPage(QWizardPage):
    """Page for selecting memory image and profile."""

    def __init__(self) -> None:
        """Initialize the image selection page."""
        super().__init__()
        self.setTitle("Memory Image")
        self.setSubTitle("Select the memory image file and analysis profile.")

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the UI."""
        layout = QFormLayout(self)

        # Image path selection
        image_layout = QHBoxLayout()
        self.image_edit = QLineEdit()
        self.image_edit.setPlaceholderText("Select memory image file...")
        self.registerField("imagePath*", self.image_edit)

        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_image)
        image_layout.addWidget(self.image_edit)
        image_layout.addWidget(browse_btn)

        layout.addRow("Memory Image:", image_layout)

        # Profile selection
        profile_combo = QComboBox()
        profile_combo.addItems(["Win10x64_19041", "Win10x64_2004", "Win7SP1x64", "Linux"])
        self.registerField("profile", profile_combo, "currentText")
        layout.addRow("Profile:", profile_combo)

    def _browse_image(self) -> None:
        """Open file dialog to select memory image."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Memory Image",
            "",
            "Memory Images (*.raw *.mem *.dmp);;All Files (*)"
        )
        if file_path:
            self.image_edit.setText(file_path)


class WorkflowSelectionPage(QWizardPage):
    """Page for selecting analysis workflow."""

    def __init__(self) -> None:
        """Initialize the workflow selection page."""
        super().__init__()
        self.setTitle("Analysis Workflow")
        self.setSubTitle("Choose the type of analysis to perform.")

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the UI."""
        layout = QVBoxLayout(self)

        # Get available workflows
        workflows = registry.list()

        if not workflows:
            layout.addWidget(QLabel("No workflows available."))
            return

        # Create radio buttons for workflows
        self.workflow_group = QButtonGroup(self)
        first_radio = None

        for workflow in workflows:
            radio = QRadioButton(f"{workflow.name}\n{workflow.description}")
            radio.setProperty("workflow_id", workflow.id)
            self.workflow_group.addButton(radio)

            if first_radio is None:
                first_radio = radio
                self.registerField("workflowId", first_radio)

            layout.addWidget(radio)

            # Select first workflow by default
            if len(self.workflow_group.buttons()) == 1:
                radio.setChecked(True)

        # Connect to button group to update wizard's selected workflow
        self.workflow_group.buttonClicked.connect(self._on_workflow_selected)

        layout.addStretch()

    def _on_workflow_selected(self, button) -> None:
        """Handle workflow selection."""
        workflow_id = button.property("workflow_id")
        self.wizard().selected_workflow_id = workflow_id


class SummaryPage(QWizardPage):
    """Page showing session summary before creation."""

    def __init__(self) -> None:
        """Initialize the summary page."""
        super().__init__()
        self.setTitle("Summary")
        self.setSubTitle("Review your session settings before starting analysis.")

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the UI."""
        layout = QVBoxLayout(self)

        self.summary_label = QLabel()
        layout.addWidget(self.summary_label)

    def initializePage(self) -> None:
        """Initialize the page with current field values."""
        session_name = self.field("sessionName")
        image_path = self.field("imagePath")
        profile = self.field("profile")
        workflow_id = self.wizard().selected_workflow_id

        # Get workflow name
        workflow_name = "Unknown"
        if workflow_id:
            try:
                workflow = registry.get(workflow_id)
                if workflow:
                    workflow_name = workflow.name
            except:
                pass

        summary = f"""
        <b>Session Name:</b> {session_name}<br>
        <b>Memory Image:</b> {image_path or 'Not selected'}<br>
        <b>Profile:</b> {profile}<br>
        <b>Workflow:</b> {workflow_name}
        """

        self.summary_label.setText(summary)