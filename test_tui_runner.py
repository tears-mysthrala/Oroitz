#!/usr/bin/env python3
"""
Standalone TUI test runner to avoid PySide6/Textual import conflicts.
This script imports Textual components first, before any PySide6 code.
"""

import os
import sys

# Set environment variables to minimize PySide6 interference
os.environ["SHIBOKEN_DISABLE_SIGNATURE_CACHE"] = "1"
os.environ["QT_QPA_PLATFORM"] = "offscreen"
# Disable PySide6 entirely if possible
os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = "/dev/null"

# Import textual components FIRST, before any other imports
try:
    import textual
    from textual.app import App
    from textual.containers import Container, Horizontal, Vertical
    from textual.pilot import Pilot
    from textual.screen import Screen
    from textual.widgets import Button, DataTable, Input, Select

    print("✓ Textual imports successful")
except ImportError as e:
    print(f"✗ Textual import failed: {e}")
    sys.exit(1)

# Now import our TUI modules
try:
    from oroitz.ui.tui.screens import HomeScreen, ResultsScreen, RunScreen, SessionWizardScreen

    print("✓ TUI modules imported successfully")
except ImportError as e:
    print(f"✗ TUI module import failed: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

# Import test dependencies
try:
    import pytest

    print("✓ Test dependencies imported successfully")
except ImportError as e:
    print(f"✗ Test dependency import failed: {e}")
    sys.exit(1)

if __name__ == "__main__":
    # Import test modules after Textual is loaded
    try:
        import tests.ui.test_tui as test_module

        print("✓ Test module imported successfully")
    except ImportError as e:
        print(f"✗ Test module import failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

    # Run a simple test manually
    try:
        print("Running basic TUI tests...")

        # Test 1: App creation
        test_module.seed_workflows()
        app = test_module.OroitzTUI()
        assert app is not None
        assert app.session is None
        print("✓ App creation test passed")

        # Test 2: Session management
        session = test_module.Session(image_path="/test.img", profile="windows")
        app.set_current_session(session)
        assert app.get_current_session() == session
        app.set_current_session(None)
        assert app.get_current_session() is None
        print("✓ Session management test passed")

        print("✓ All basic TUI tests passed!")

    except Exception as e:
        print(f"✗ Test execution failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
