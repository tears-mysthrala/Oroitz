#!/usr/bin/env python3
"""
Build script for creating Oroitz installers using PyInstaller.

This script creates standalone executables for CLI, GUI, and TUI interfaces
across multiple platforms (Windows, macOS, Linux).
"""

import os
import platform
import subprocess
import sys
from pathlib import Path


def run_command(cmd, cwd=None):
    """Run a command and return success status."""
    try:
        result = subprocess.run(
            cmd, shell=True, cwd=cwd, check=True, capture_output=True, text=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {cmd}")
        print(f"Error: {e.stderr}")
        return False, e.stderr


def build_executable(entry_point, name, console=True, additional_args=None):
    """Build a single executable using PyInstaller."""
    cmd = [
        "poetry",
        "run",
        "pyinstaller",
        "--onefile",  # Single executable file
        "--clean",  # Clean cache
        "--noconfirm",  # Don't ask for confirmation
        f"--name={name}",
        "--collect-all",
        "textual",  # Collect all textual modules
        "--collect-all",
        "volatility3",  # Collect all volatility3 modules and data
    ]

    if console:
        cmd.append("--console")
    else:
        cmd.append("--windowed")

    if additional_args:
        cmd.extend(additional_args)

    cmd.append(entry_point)

    print(f"Building {name}...")
    success, output = run_command(" ".join(cmd))
    if success:
        print(f"✓ Successfully built {name}")
    else:
        print(f"✗ Failed to build {name}")
    return success


def main():
    """Main build function."""
    print("Oroitz Installer Builder")
    print("=" * 40)

    # Ensure we're in the project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    # Check if PyInstaller is installed
    try:
        import PyInstaller

        print(f"PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        print("PyInstaller not found. Installing...")
        success, _ = run_command("poetry install --with dev")
        if not success:
            print("Failed to install dependencies")
            return 1

    # Determine platform
    system = platform.system().lower()
    print(f"Building on {system}")

    # Build CLI executable
    cli_success = build_executable("oroitz/cli/__main__.py", f"oroitz-cli-{system}", console=True)

    # Build GUI executable (windowed)
    gui_additional_args = [
        "--add-data",
        f"oroitz/ui/gui{os.pathsep}oroitz/ui/gui",  # Include GUI resources
    ]
    gui_success = build_executable(
        "oroitz/ui/gui/__main__.py",
        f"oroitz-gui-{system}",
        console=False,
        additional_args=gui_additional_args,
    )

    # Build TUI executable
    tui_success = build_executable(
        "oroitz/ui/tui/__main__.py",
        f"oroitz-tui-{system}",
        console=True,
        additional_args=[
            "--add-data",
            "oroitz/ui/tui:oroitz/ui/tui",  # Include TUI resources including styles
        ],
    )

    # Summary
    print("\nBuild Summary:")
    print(f"CLI: {'✓' if cli_success else '✗'}")
    print(f"GUI: {'✓' if gui_success else '✗'}")
    print(f"TUI: {'✓' if tui_success else '✗'}")

    if all([cli_success, gui_success, tui_success]):
        print("\n✓ All executables built successfully!")
        print(f"Executables are in: {project_root / 'dist'}")
        return 0
    else:
        print("\n✗ Some builds failed. Check output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
