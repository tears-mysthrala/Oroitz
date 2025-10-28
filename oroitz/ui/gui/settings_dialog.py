"""Settings dialog for application configuration."""

from pathlib import Path

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from oroitz.core.config import config
from oroitz.ui.gui.theme_manager import Theme, ThemeManager


class SettingsDialog(QDialog):
    """Dialog for configuring application settings."""

    def __init__(self, parent=None) -> None:
        """Initialize the settings dialog."""
        super().__init__(parent)

        self.setWindowTitle("Settings")
        self.setModal(True)
        self.resize(600, 400)

        self._setup_ui()
        self._load_settings()

    def _setup_ui(self) -> None:
        """Setup the UI components."""
        layout = QVBoxLayout(self)

        # Tab widget for different settings categories
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # General tab
        self.tab_widget.addTab(self._create_general_tab(), "General")

        # Paths tab
        self.tab_widget.addTab(self._create_paths_tab(), "Paths")

        # Analysis tab
        self.tab_widget.addTab(self._create_analysis_tab(), "Analysis")

        # Appearance tab
        self.tab_widget.addTab(self._create_appearance_tab(), "Appearance")

        # Button box
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
            | QDialogButtonBox.StandardButton.Apply
        )
        button_box.accepted.connect(self._accept)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self._apply)
        layout.addWidget(button_box)

    def _create_general_tab(self) -> QWidget:
        """Create the general settings tab."""
        widget = QWidget()
        layout = QFormLayout(widget)

        # Logging level
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        layout.addRow("Log Level:", self.log_level_combo)

        # Max concurrency
        self.max_concurrency_spin = QSpinBox()
        self.max_concurrency_spin.setRange(1, 16)
        layout.addRow("Max Concurrency:", self.max_concurrency_spin)

        # Telemetry
        self.telemetry_check = QCheckBox("Enable telemetry")
        layout.addRow(self.telemetry_check)

        return widget

    def _create_paths_tab(self) -> QWidget:
        """Create the paths settings tab."""
        widget = QWidget()
        layout = QFormLayout(widget)

        # Volatility path
        volatility_layout = QHBoxLayout()
        self.volatility_path_edit = QLineEdit()
        self.volatility_path_edit.setPlaceholderText("Auto-detect")
        browse_volatility_btn = QPushButton("Browse...")
        browse_volatility_btn.clicked.connect(self._browse_volatility_path)
        volatility_layout.addWidget(self.volatility_path_edit)
        volatility_layout.addWidget(browse_volatility_btn)
        layout.addRow("Volatility Path:", volatility_layout)

        # Sessions directory
        sessions_layout = QHBoxLayout()
        self.sessions_dir_edit = QLineEdit()
        browse_sessions_btn = QPushButton("Browse...")
        browse_sessions_btn.clicked.connect(self._browse_sessions_dir)
        sessions_layout.addWidget(self.sessions_dir_edit)
        sessions_layout.addWidget(browse_sessions_btn)
        layout.addRow("Sessions Directory:", sessions_layout)

        return widget

    def _create_analysis_tab(self) -> QWidget:
        """Create the analysis settings tab."""
        widget = QWidget()
        layout = QFormLayout(widget)

        # Cache results
        self.cache_results_check = QCheckBox("Cache plugin results")
        layout.addRow(self.cache_results_check)

        # Force re-execute on fail
        self.force_reexecute_check = QCheckBox("Force re-execute on fail")
        layout.addRow(self.force_reexecute_check)

        # Auto-export
        self.auto_export_check = QCheckBox("Auto-export results")
        layout.addRow(self.auto_export_check)

        return widget

    def _create_appearance_tab(self) -> QWidget:
        """Create the appearance settings tab."""
        widget = QWidget()
        layout = QFormLayout(widget)

        # Theme
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["system", "light", "dark"])
        layout.addRow("Theme:", self.theme_combo)

        # Font size
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setValue(10)
        layout.addRow("Font Size:", self.font_size_spin)

        return widget

    def _load_settings(self) -> None:
        """Load current settings into the UI."""
        # General
        self.log_level_combo.setCurrentText(config.log_level)
        self.max_concurrency_spin.setValue(config.max_concurrency)
        self.telemetry_check.setChecked(config.telemetry_enabled)

        # Paths
        # self.volatility_path_edit.setText(str(config.volatility_path))  # TODO: Add to config
        self.sessions_dir_edit.setText(str(config.sessions_dir))

        # Analysis
        self.cache_results_check.setChecked(config.cache_enabled)
        self.force_reexecute_check.setChecked(config.force_reexecute_on_fail)
        self.auto_export_check.setChecked(config.auto_export)

        # Appearance
        # self.theme_combo.setCurrentText(config.theme)  # TODO: Add to config
        # self.font_size_spin.setValue(config.font_size)  # TODO: Add to config
        self.theme_combo.setCurrentText(ThemeManager.get_current_theme().value)
        self.font_size_spin.setValue(config.font_size)

    def _save_settings(self) -> None:
        """Save settings from UI to config."""
        # General
        config.log_level = self.log_level_combo.currentText()
        config.max_concurrency = self.max_concurrency_spin.value()
        config.telemetry_enabled = self.telemetry_check.isChecked()

        # Paths
        # config.volatility_path = Path(self.volatility_path_edit.text())  # TODO: Add to config
        config.sessions_dir = Path(self.sessions_dir_edit.text())

        # Analysis
        config.cache_enabled = self.cache_results_check.isChecked()
        config.force_reexecute_on_fail = self.force_reexecute_check.isChecked()
        config.auto_export = self.auto_export_check.isChecked()

        # Appearance
        # config.theme = self.theme_combo.currentText()  # TODO: Add to config
        # config.font_size = self.font_size_spin.value()  # TODO: Add to config
        theme = Theme(self.theme_combo.currentText())
        ThemeManager.set_theme(theme)
        config.theme = self.theme_combo.currentText()
        config.font_size = self.font_size_spin.value()

    def _browse_volatility_path(self) -> None:
        """Browse for Volatility executable."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Volatility Executable", "", "Executable files (*.exe);;All Files (*)"
        )
        if path:
            self.volatility_path_edit.setText(path)

    def _browse_sessions_dir(self) -> None:
        """Browse for sessions directory."""
        path = QFileDialog.getExistingDirectory(
            self, "Select Sessions Directory", str(self.sessions_dir_edit.text())
        )
        if path:
            self.sessions_dir_edit.setText(path)

    def _accept(self) -> None:
        """Handle OK button."""
        self._save_settings()
        self.accept()

    def _apply(self) -> None:
        """Handle Apply button."""
        self._save_settings()
