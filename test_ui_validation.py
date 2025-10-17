#!/usr/bin/env python3
"""
Comprehensive UI Test Validation Script

This script runs GUI and TUI tests separately to avoid PySide6/Textual import conflicts.
It validates that both interfaces work correctly in isolation.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_gui_tests():
    """Run GUI tests in isolation."""
    print("🔍 Running GUI tests (PySide6)...")
    try:
        # Run GUI tests with poetry
        result = subprocess.run([
            "poetry", "run", "pytest",
            "tests/ui/test_gui.py",
            "-v",
            "--tb=short"
        ], capture_output=True, text=True, cwd=Path(__file__).parent)

        print("GUI Test Output:")
        print(result.stdout)
        if result.stderr:
            print("GUI Test Errors:")
            print(result.stderr)

        return result.returncode == 0
    except Exception as e:
        print(f"❌ GUI test execution failed: {e}")
        return False

def run_tui_tests():
    """Run TUI tests in isolation using the dedicated runner."""
    print("🔍 Running TUI tests (Textual)...")
    try:
        # Use the dedicated TUI test runner with poetry
        result = subprocess.run([
            "poetry", "run", "python", "test_tui_runner.py"
        ], capture_output=True, text=True, cwd=Path(__file__).parent)

        print("TUI Test Output:")
        print(result.stdout)
        if result.stderr:
            print("TUI Test Errors:")
            print(result.stderr)

        return result.returncode == 0
    except Exception as e:
        print(f"❌ TUI test execution failed: {e}")
        return False

def main():
    """Run comprehensive UI test validation."""
    print("🚀 Starting Comprehensive UI Test Validation")
    print("=" * 50)

    gui_success = run_gui_tests()
    print()

    tui_success = run_tui_tests()
    print()

    print("📊 Test Results Summary:")
    print(f"GUI Tests: {'✅ PASSED' if gui_success else '❌ FAILED'}")
    print(f"TUI Tests: {'✅ PASSED' if tui_success else '❌ FAILED'}")

    if gui_success and tui_success:
        print("\n🎉 All UI tests passed! Both GUI and TUI interfaces are working correctly.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())