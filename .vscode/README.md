# VS Code Configuration for Oroitz

This directory contains VS Code configuration files to set up the development environment for the Oroitz project.

## What's Configured

### Testing Extension

- **Python Testing**: Configured to use pytest with Poetry
- **Test Discovery**: Automatic discovery of tests in the `tests/` directory (excludes TUI tests due to import conflicts)
- **Test Running**: Support for running GUI tests, core tests, and TUI tests separately

### Python Extension

- **Interpreter**: Uses Poetry virtual environment (`.venv/bin/python`)
- **Linting**: Ruff enabled with auto-fix on save
- **Formatting**: Black enabled with format on save
- **Environment Activation**: Automatic terminal environment activation

### Tasks

- **Install Dependencies**: `poetry install`
- **Run All Tests**: Default test task using pytest
- **Run GUI Tests Only**: Test GUI components only
- **Run TUI Tests Only**: Test TUI components only (isolated)
- **Run UI Validation**: Run comprehensive UI test validation
- **Format Code**: Run Black formatter
- **Lint Code**: Run Ruff linter
- **Fix Lint Issues**: Auto-fix linting issues

### Debug Configurations

- **Debug Tests**: Debug pytest test runs
- **Debug GUI**: Debug the PySide6 GUI application
- **Debug TUI**: Debug the Textual TUI application
- **Debug CLI**: Debug the Click CLI application
- **Run UI Validation**: Debug the UI validation script

## How to Use

1. **Install Dependencies**: Run the "Install Dependencies" task from Command Palette (`Ctrl+Shift+P` → "Tasks: Run Task" → "Install Dependencies")

2. **Run Tests**:
   - Use the Testing sidebar (flask icon) to run individual tests (GUI and core tests only)
   - Use "Run All Tests" task for GUI and core test suite
   - Use "Run TUI Tests Only" task for TUI tests (runs in isolation)
   - Use "Run UI Validation" for comprehensive GUI/TUI testing

3. **Debug Tests**: Use the debug configuration "Debug Tests" to debug test execution

4. **Code Quality**: Code will be automatically formatted and linted on save

## Troubleshooting

If tests don't appear in the Testing sidebar:

1. Make sure Poetry dependencies are installed
2. Reload VS Code window (`Ctrl+Shift+P` → "Developer: Reload Window")
3. Check that the Python interpreter is set to the Poetry virtual environment

If testing extension still shows as not configured:

1. Ensure the Python extension is installed and enabled
2. Check that `python.testing.pytestEnabled` is `true` in settings
3. Verify pytest is installed in the Poetry environment

### TUI Tests

TUI tests are excluded from automatic discovery due to PySide6/Textual import conflicts. To run TUI tests:

1. Use the "Run TUI Tests Only" task from Command Palette
2. Or run `python test_tui_runner.py` directly in terminal
3. For comprehensive testing, use "Run UI Validation" task
