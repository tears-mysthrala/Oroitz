"""Session dashboard for monitoring analysis progress."""

from typing import Optional

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from oroitz.core.executor import Executor
from oroitz.core.session import Session
from oroitz.core.workflow import registry
from oroitz.ui.gui.notification_center import NotificationCenter
from oroitz.ui.gui.results_explorer import ResultsExplorer


class WorkflowWorker(QThread):
    """Worker thread for executing workflows asynchronously."""

    # Signals
    progress_updated = Signal(int, str)  # progress_percentage, status_message
    log_message = Signal(str)  # log message
    execution_finished = Signal(list)  # results list
    execution_error = Signal(str)  # error message

    def __init__(self, workflow_id: str, image_path: str, profile: str) -> None:
        """Initialize the workflow worker."""
        super().__init__()
        self.workflow_id = workflow_id
        self.image_path = image_path
        self.profile = profile
        self.executor = Executor()

    def run(self) -> None:
        """Execute the workflow in a separate thread."""
        try:
            # Get workflow
            workflow = registry.get(self.workflow_id)
            if not workflow:
                self.execution_error.emit(f"Workflow '{self.workflow_id}' not found")
                return

            # Check compatibility
            if not registry.validate_compatibility(self.workflow_id, self.profile):
                self.execution_error.emit(f"Workflow not compatible with profile {self.profile}")
                return

            self.log_message.emit(f"Starting workflow: {workflow.name}")
            self.progress_updated.emit(5, "Initializing...")

            # Execute workflow
            results = self.executor.execute_workflow(workflow, self.image_path, self.profile)

            # Update progress for each plugin
            total_plugins = len(workflow.plugins)
            for i, result in enumerate(results):
                progress = int(10 + (i / total_plugins) * 80)  # 10-90% range

                # Build message with attempt info and fallback marker
                if result.success:
                    msg = f"\u2713 {result.plugin_name}: {result.duration:.2f}s"
                else:
                    msg = f"\u2717 {result.plugin_name}: {result.error}"

                if getattr(result, "attempts", None):
                    msg += f" (Attempts: {result.attempts})"
                if getattr(result, "used_mock", False):
                    msg += " [FALLBACK: mock data used]"

                if result.success:
                    self.log_message.emit(msg)
                    self.progress_updated.emit(progress, f"Completed {result.plugin_name}")
                else:
                    self.log_message.emit(msg)
                    self.progress_updated.emit(progress, f"Failed {result.plugin_name}")

            self.progress_updated.emit(95, "Processing results...")
            self.log_message.emit("Workflow execution completed")

            self.progress_updated.emit(100, "Complete")
            self.execution_finished.emit(results)

        except Exception as e:
            self.execution_error.emit(f"Workflow execution failed: {str(e)}")
            self.log_message.emit(f"Error: {str(e)}")


class SessionDashboard(QWidget):
    """Dashboard for monitoring session analysis progress."""

    # Signals
    back_to_landing = Signal()

    def __init__(self) -> None:
        """Initialize the session dashboard."""
        super().__init__()

        self.current_session: Optional[Session] = None
        self.worker: Optional[WorkflowWorker] = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the UI components."""
        layout = QVBoxLayout(self)

        # Header with session info and back button
        header_layout = QHBoxLayout()

        self.back_btn = QPushButton("← Back to Landing")
        self.back_btn.clicked.connect(self._on_back_clicked)
        header_layout.addWidget(self.back_btn)

        header_layout.addStretch()

        self.session_title = QLabel("No Session Loaded")
        self.session_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        header_layout.addWidget(self.session_title)

        layout.addLayout(header_layout)

        # Main content splitter
        splitter = QSplitter()
        layout.addWidget(splitter)

        # Left panel - Progress and controls
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # Progress section
        progress_label = QLabel("Analysis Progress")
        progress_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        left_layout.addWidget(progress_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        left_layout.addWidget(self.progress_bar)

        self.status_label = QLabel("Ready to start analysis")
        left_layout.addWidget(self.status_label)

        # Control buttons
        controls_layout = QHBoxLayout()

        self.start_btn = QPushButton("Start Analysis")
        self.start_btn.clicked.connect(self._on_start_clicked)
        controls_layout.addWidget(self.start_btn)

        self.pause_btn = QPushButton("Pause")
        self.pause_btn.clicked.connect(self._on_pause_clicked)
        self.pause_btn.setEnabled(False)
        controls_layout.addWidget(self.pause_btn)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(self._on_stop_clicked)
        self.stop_btn.setEnabled(False)
        controls_layout.addWidget(self.stop_btn)

        left_layout.addLayout(controls_layout)

        # Workflow info
        workflow_label = QLabel("Workflow Information")
        workflow_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 20px;")
        left_layout.addWidget(workflow_label)

        self.workflow_info = QLabel("No workflow selected")
        self.workflow_info.setWordWrap(True)
        left_layout.addWidget(self.workflow_info)

        left_layout.addStretch()

        # Right panel - Logs and results
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        logs_label = QLabel("Analysis Logs")
        logs_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        right_layout.addWidget(logs_label)

        self.logs_text = QTextEdit()
        self.logs_text.setReadOnly(True)
        self.logs_text.setPlainText("Analysis logs will appear here...")
        right_layout.addWidget(self.logs_text)

        # Results section (placeholder for now)
        results_label = QLabel("Results")
        results_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 20px;")
        right_layout.addWidget(results_label)

        self.results_explorer = ResultsExplorer()
        right_layout.addWidget(self.results_explorer)

        # Set splitter proportions
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 600])

    def set_session(self, session: Session) -> None:
        """Set the current session to display."""
        self.current_session = session

        # Update UI with session info
        self.session_title.setText(f"Session: {session.name}")

        # Update workflow info
        workflow_info = f"Name: {session.name}\n"
        if session.image_path:
            workflow_info += f"Image: {session.image_path.name}\n"
        if session.profile:
            workflow_info += f"Profile: {session.profile}\n"
        workflow_info += f"Created: {session.created_at.strftime('%Y-%m-%d %H:%M')}"

        self.workflow_info.setText(workflow_info)

        # Reset progress
        self.progress_bar.setValue(0)
        self.status_label.setText("Ready to start analysis")
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)

    def _on_back_clicked(self) -> None:
        """Handle back button click."""
        self.back_to_landing.emit()

    def _on_start_clicked(self) -> None:
        """Handle start analysis button click."""
        if not self.current_session or not self.current_session.workflow_id:
            return

        # Check if we have required session data
        if not self.current_session.image_path:
            self.status_label.setText("Error: No memory image specified")
            return

        if not self.current_session.profile:
            self.status_label.setText("Error: No profile specified")
            return

        # Start workflow execution
        self.status_label.setText("Starting analysis...")
        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)

        # Clear previous logs and results
        self.logs_text.clear()
        self.results_explorer.set_results([])

        # Create and start worker thread
        self.worker = WorkflowWorker(
            self.current_session.workflow_id,
            str(self.current_session.image_path),
            self.current_session.profile,
        )

        # Connect signals
        self.worker.progress_updated.connect(self._on_progress_updated)
        self.worker.log_message.connect(self._on_log_message)
        self.worker.execution_finished.connect(self._on_execution_finished)
        self.worker.execution_error.connect(self._on_execution_error)

        # Start execution
        self.worker.start()

    def _on_progress_updated(self, progress: int, status: str) -> None:
        """Handle progress updates from worker thread."""
        self.progress_bar.setValue(progress)
        self.status_label.setText(status)

    def _on_log_message(self, message: str) -> None:
        """Handle log messages from worker thread."""
        self.logs_text.append(message)

    def _on_execution_finished(self, results) -> None:
        """Handle successful workflow execution."""
        self.status_label.setText("Analysis complete")
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)

        # Display results in explorer
        self.results_explorer.set_results(results)

        NotificationCenter().show_success("Analysis completed successfully", self)

        # Clean up worker
        if self.worker:
            self.worker = None

    def _on_execution_error(self, error_message: str) -> None:
        """Handle workflow execution errors."""
        self.status_label.setText(f"Error: {error_message}")
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)

        NotificationCenter().show_error(f"Analysis failed: {error_message}", self)

        # Clean up worker
        if self.worker:
            self.worker = None

    def _on_pause_clicked(self) -> None:
        """Handle pause button click."""
        # TODO: Implement pause functionality
        self.status_label.setText("Analysis paused")
        self.pause_btn.setText("Resume")
        self.start_btn.setEnabled(False)

    def _on_stop_clicked(self) -> None:
        """Handle stop button click."""
        # Stop the worker thread if running
        if self.worker and self.worker.isRunning():
            self.worker.terminate()  # Force termination
            self.worker.wait()
            self.worker = None

        self.status_label.setText("Analysis stopped")
        self.progress_bar.setValue(0)
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.pause_btn.setText("Pause")
        self.stop_btn.setEnabled(False)
