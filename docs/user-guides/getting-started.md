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

- Python 3.11 or 3.12 (3.11 recommended for maximum compatibility with all Volatility3 plugins)
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
   poetry run python scripts/setup_volatility_plugins.py --dest vendor/volatility_plugins --update-env
   ```

   The helper script downloads the Volatility community plugin pack (community3) required for hash extraction workflows and records the plugin path in `.env`.

3. **Verify installation:**

   ```bash
   poetry run python -m oroitz.cli --help
   ```

## Your First Analysis

### Quick Start with CLI

1. **Run quick triage on a memory sample:**

   ```bash
   poetry run python -m oroitz.cli quick-triage samples/memdump.mem --output results.json
   ```

2. **Enumerate accounts and hashes (requires community plugins):**

   ```bash
   poetry run python -m oroitz.cli accounts samples/memdump.mem --output accounts.json
   ```

3. **View the results:**

   ```bash
   cat results.json | jq '.processes | length'  # Count processes
   cat accounts.json | jq '.hashes | length'    # Hash records (if available)
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
   - Click "Start Analysis" (Volatility 3 auto-detects the appropriate symbol tables)

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
   - Fill in the session wizard (image path only - Volatility 3 auto-detects symbol tables)
   - View results in the data table
   - Press 'e' to export results

## Understanding Workflows

Oroitz organizes analysis into **workflows** - predefined sequences of Volatility plugins:

- **Quick Triage**: Overview of processes, network connections, and suspicious memory regions
- **Process Deep Dive**: Detailed process tree analysis with DLL and handle information
- **Network Focus**: Comprehensive network activity analysis
- **Timeline Overview**: Chronological timeline of memory events

## Memory Samples

The repository does not include large memory images directly. Instead the
`samples/` directory contains metadata and helper scripts to obtain sample
images for local testing. This keeps the repository small and avoids
committing sensitive or large binaries.

Canonical metadata: `assets/samples.json`.

To download recommended samples (for example the small `memdump.7z` used in
examples), use the provided helper script:

```bash
python scripts/fetch_samples.py --list
python scripts/fetch_samples.py --id samsclass-memdump
```

For a larger curated list of memory sample links see the community-maintained
aggregator: [pinesol93/MemoryForensicSamples](https://github.com/pinesol93/MemoryForensicSamples)

Always verify the original data source and respect licensing and privacy
requirements before downloading or sharing memory images.

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
