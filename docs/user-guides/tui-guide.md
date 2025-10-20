# TUI User Guide

The Oroitz Terminal User Interface (TUI) provides a keyboard-driven, text-based interface for memory forensics analysis using the Textual framework.

## Launching the TUI

```bash
# From the project directory
poetry run python -m oroitz.ui.tui

# Or if in poetry shell
python -m oroitz.ui.tui
```

## Interface Overview

The TUI is organized into several screens:

- **Home Screen**: Workflow selection and navigation
- **Session Wizard**: Step-by-step analysis configuration
- **Run Screen**: Real-time analysis progress and logs
- **Results Screen**: Data tables with keyboard navigation

## Navigation Basics

### Keyboard Controls

- **Arrow Keys**: Navigate menus and lists
- **Enter**: Select items or confirm actions
- **Tab**: Move between form fields
- **Esc**: Go back or cancel
- **Ctrl+C**: Quit the application

### Screen Flow

```text
Home Screen → Session Wizard → Run Screen → Results Screen
     ↑              ↓              ↓              ↓
     └──────────────┴──────────────┴──────────────┘
```

## Creating an Analysis

### Step 1: Select Workflow

1. Launch the TUI
2. Use **arrow keys** to highlight a workflow (e.g., "Quick Triage")
3. Press **Enter** to select

### Step 2: Configure Session

The session wizard will guide you through:

1. **Memory Image Path**:
   - Type or paste the full path to your memory dump
   - Use Tab to move to the next field
   - Supported formats: `.mem`, `.raw`, `.vmem`

2. **Volatility Profile**:
   - Use arrow keys to select from available profiles
   - Common options:
     - `Win10x64_19041` (Windows 10)
     - `Win7SP1x64` (Windows 7)
     - `LinuxUbuntu1804x64` (Ubuntu Linux)

3. **Confirm and Start**:
   - Review your settings
   - Press Enter on "Start Analysis"

### Step 3: Monitor Progress

The Run Screen shows:

- **Progress indicators** for each plugin
- **Real-time logs** of execution
- **Status messages** and any errors

### Step 4: Explore Results

Once analysis completes:

- Press **Enter** or **'r'** to view results
- Navigate between result categories with **Tab**
- Use **arrow keys** to browse data
- Press **'e'** to export results

## Results Navigation

### Data Tables

- **Arrow Keys**: Navigate cells
- **Page Up/Down**: Scroll through large datasets
- **Home/End**: Jump to top/bottom
- **Enter**: View detailed information (when available)

### Export Options

From the results screen:

- Press **'e'** to open export dialog
- Choose format: JSON or CSV
- Enter filename or accept default
- Results save to current directory

### Keyboard Shortcuts

- **'q'**: Quit current screen
- **'h'**: Show help (context-sensitive)
- **'s'**: Save current session
- **'r'**: Refresh/reload data
- **'f'**: Focus search/filter (when available)

## Available Workflows

### Quick Triage

**Purpose**: Rapid overview of system state

**Data Provided**:

- Process listing with basic information
- Network connections and listening ports
- Suspicious memory regions (malfind)

**Typical Runtime**: 2-3 minutes

**Use Case**: Initial incident response assessment

### Process Deep Dive

**Purpose**: Comprehensive process analysis

**Data Provided**:

- Complete process trees
- DLL dependencies and versions
- Handle information and access rights

**Typical Runtime**: 5-8 minutes

**Use Case**: Malware analysis and process investigation

### Network Focus

**Purpose**: Network-centric analysis

**Data Provided**:

- All network connections and sockets
- Connection states and protocols
- Associated process information

**Typical Runtime**: 3-5 minutes

**Use Case**: C2 detection and network forensics

### Timeline Overview

**Purpose**: Temporal event analysis

**Data Provided**:

- Chronological system events
- Process lifecycle events
- Network connection timelines

**Typical Runtime**: 4-6 minutes

**Use Case**: Event reconstruction and timeline analysis

## Advanced Features

### Command Mode

Press **':'** to enter command mode for advanced operations:

```shell
```bash
:help              # Show available commands
:save filename     # Save current session
:load filename     # Load saved session
:export json       # Export to JSON
:filter pid=1234   # Filter results
:search notepad    # Search for text
```

### Filtering and Search

- **Global Search**: Press **'/'** then type search term
- **Column Filters**: Navigate to column headers and press Enter
- **Saved Filters**: Use command mode to apply complex filters

### Session Management

- **Auto-save**: Sessions automatically save progress
- **Resume**: Restart TUI to continue previous analysis
- **Multiple Sessions**: Work with different memory images simultaneously

## Troubleshooting

### Common Issues

#### TUI Won't Start

**Symptoms**: Application fails to launch or shows import errors

**Solutions**:

- Ensure Textual is installed: `poetry install`
- Check Python version (3.11+ required)
- Try running in a different terminal

#### No Data Displayed

**Symptoms**: Tables appear empty after analysis

**Solutions**:

- Verify memory image file exists and is readable
- Check Volatility profile matches the image
- Review logs for error messages

#### Slow Performance

**Symptoms**: Interface is sluggish or unresponsive

**Solutions**:

- Close other terminal applications
- Ensure adequate system resources
- Try a smaller memory image for testing

#### Export Fails

**Symptoms**: Error when attempting to export

**Solutions**:

- Check write permissions in current directory
- Ensure sufficient disk space
- Try a different filename

### Performance Tips

- **Terminal Size**: Use at least 120x30 characters
- **Memory Images**: Start with smaller images (<1GB) for testing
- **Caching**: Re-running analysis on same image is faster
- **Background**: Avoid running other intensive processes

### Error Messages

#### Profile not supported

- Choose a different Volatility profile
- Verify profile matches your memory image OS

#### File not found

- Check the memory image path is correct
- Ensure file permissions allow reading

#### Analysis failed

- Check system logs for detailed error information
- Try with a different memory image
- Verify Volatility 3 installation

### Filtering and Searching Results

- **Global Search**: Press **'/'** then type search term
- **Column Filters**: Navigate to column headers and press Enter
- **Saved Filters**: Use command mode to apply complex filters

## Integration Examples

### With CLI Tools

```bash
# Export from TUI, then process with CLI tools
# In TUI: press 'e', export as JSON
cat results.json | jq '.processes[] | select(.name | contains("susp"))'

# Convert to CSV for spreadsheet analysis
python -c "
import json, csv
with open('results.json') as f:
    data = json.load(f)
with open('processes.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerow(['PID', 'Name', 'Handles'])
    for p in data['processes']:
        writer.writerow([p['pid'], p['name'], p['handles']])
"
```

### Scripting Automation

```python
# Load TUI results in Python scripts
import json

def analyze_results(filename):
    with open(filename) as f:
        data = json.load(f)

    # Find suspicious processes
    suspicious = []
    for proc in data['processes']:
        if proc['handles'] > 1000 or 'susp' in proc['name'].lower():
            suspicious.append(proc)

    return suspicious

results = analyze_results('triage_results.json')
print(f"Found {len(results)} suspicious processes")
```

## Best Practices

1. **Start Simple**: Begin with Quick Triage to understand the system
2. **Use Appropriate Profiles**: Match profile to memory image characteristics
3. **Export Regularly**: Save results before navigating away
4. **Learn Shortcuts**: Keyboard navigation becomes faster with practice
5. **Check Logs**: Review execution logs for warnings or errors

## Getting Help

- **Built-in Help**: Press **'h'** or **'?'** in most screens
- **Command Help**: Type `:help` in command mode
- **Logs**: Check the run screen for detailed execution information
- **Issues**: Report bugs on GitHub with TUI logs

For GUI usage or CLI automation, see the [GUI User Guide](gui-guide.md) and [CLI User Guide](cli-guide.md).
