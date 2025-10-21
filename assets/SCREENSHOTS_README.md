# Oroitz Screenshots and Visual Assets Guide

This document outlines the screenshots and visual assets needed for Oroitz documentation.

## Required Screenshots

### GUI Screenshots

1. **Landing Page** (`gui-landing.png`)
   - Main landing view with session options
   - Should show the clean, modern interface

2. **New Session Wizard** (`gui-session-wizard.png`)
   - Session creation wizard with workflow selection
   - Show the step-by-step process

3. **Session Dashboard** (`gui-dashboard.png`)
   - Active session with progress indicators
   - Show workflow execution status

4. **Results Explorer** (`gui-results.png`)
   - Results table with filtering and export options
   - Demonstrate data exploration capabilities

5. **Settings Dialog** (`gui-settings.png`)
   - Application settings and configuration
   - Show theming and preference options

### TUI Screenshots

1. **Home Screen** (`tui-home.png`)
   - Textual interface main screen
   - Show keyboard navigation hints

2. **Session Wizard** (`tui-wizard.png`)
   - Terminal-based session creation
   - Demonstrate the guided workflow

3. **Results Screen** (`tui-results.png`)
   - DataTable with export options
   - Show structured output display

### CLI Screenshots

1. **Help Output** (`cli-help.png`)
   - `oroitz --help` command output
   - Show available commands and options

2. **Quick Triage Execution** (`cli-execution.png`)
   - Running quick triage analysis
   - Show progress and output

## Asset Creation Instructions

### For GUI Screenshots

1. Launch the GUI: `poetry run python -m oroitz.ui.gui`
2. Navigate to each screen
3. Take screenshots using your system's screenshot tool
4. Crop to show the application window only
5. Save as PNG format with descriptive names

### For TUI Screenshots

1. Launch the TUI: `poetry run python -m oroitz.ui.tui`
2. Use terminal screenshot capabilities or copy-paste output
3. For best results, use a terminal with good font rendering
4. Save terminal output as images

### For CLI Screenshots

1. Run commands in terminal
2. Use terminal screenshot or save output to file
3. Ensure commands are clearly visible

## File Naming Convention

- `gui-{feature}.png` - GUI screenshots
- `tui-{feature}.png` - TUI screenshots
- `cli-{feature}.png` - CLI screenshots

## Image Specifications

- Format: PNG (preferred) or JPEG
- Resolution: At least 1920x1080 for crisp display
- Background: Consistent terminal/GUI theme
- Annotations: Minimal, focus on functionality

## Current Status

This guide serves as a placeholder until actual screenshots can be created and added to the `assets/` directory. The screenshots should be added before final documentation publication.
