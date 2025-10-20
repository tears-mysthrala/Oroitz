# Getting Started with Oroitz

Welcome to Oroitz! This guide will help you get up and running with memory forensics analysis using our cross-platform Volatility 3 wrapper.

## What is Oroitz?

Oroitz provides a unified interface for running Volatility 3 memory forensics workflows through:

- **CLI**: Command-line interface for scripting and automation
- **GUI**: Desktop application with visual workflow execution
- **TUI**: Terminal-based interface for keyboard-driven analysis

All interfaces share the same core engine, ensuring consistent results across platforms.

## Installation

### Prerequisites

- Python 3.11 or later
- Poetry (dependency manager)

### Install Steps

1. **Clone the repository:**

   ```bash
   git clone https://github.com/tears-mysthrala/Oroitz.git
   cd Oroitz
   ```

2. **Install dependencies:**

   ```bash
   poetry install
   ```

3. **Verify installation:**

   ```bash
   poetry run python -m oroitz.cli --help
   ```

## Your First Analysis

### Quick Start with CLI

1. **Run quick triage on a memory sample:**

   ```bash
   poetry run python -m oroitz.cli quick-triage samples/memdump.mem --profile Win2008SP1x86 --output results.json
   ```

2. **View the results:**

   ```bash
   cat results.json | jq '.processes | length'  # Count processes
   cat results.json | jq '.network_connections[0]'  # First network connection
   ```

### Using the GUI

1. **Launch the GUI:**

   ```bash
   poetry run python -m oroitz.ui.gui
   ```

2. **Create a new session:**
   - Click "New Session" on the landing page
   - Select "Quick Triage" workflow
   - Choose your memory image file
   - Select the appropriate Volatility profile
   - Click "Start Analysis"

3. **Explore results:**
   - View process listings in the dashboard
   - Use the results explorer to filter and export data
   - Export findings to JSON or CSV

### Using the TUI

1. **Launch the TUI:**

   ```bash
   poetry run python -m oroitz.ui.tui
   ```

2. **Navigate with keyboard:**
   - Use arrow keys to select workflows
   - Press Enter to choose "Quick Triage"
   - Fill in the session wizard (image path, profile)
   - View results in the data table
   - Press 'e' to export results

## Understanding Workflows

Oroitz organizes analysis into **workflows** - predefined sequences of Volatility plugins:

- **Quick Triage**: Overview of processes, network connections, and suspicious memory regions
- **Process Deep Dive**: Detailed process tree analysis with DLL and handle information
- **Network Focus**: Comprehensive network activity analysis
- **Timeline Overview**: Chronological timeline of memory events

## Memory Samples

The `samples/` directory includes real memory images for testing:

- `memdump.mem`: Windows Server 2008 SP1 x86 sample
- Additional samples available in the repository

## Next Steps

- [CLI User Guide](cli-guide.md) - Detailed command-line usage
- [GUI User Guide](gui-guide.md) - Desktop application tutorial
- [TUI User Guide](tui-guide.md) - Terminal interface guide
- [Workflow Reference](workflow-reference.md) - Complete workflow documentation
- [Troubleshooting](troubleshooting.md) - Common issues and solutions

## Getting Help

- Check the [GitHub Issues](https://github.com/tears-mysthrala/Oroitz/issues) for known problems
- Review the [README](../README.md) for development status
- File a bug report if you encounter issues

Happy analyzing! 🔍
