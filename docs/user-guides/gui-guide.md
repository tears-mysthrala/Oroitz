# GUI User Guide

The Oroitz GUI provides an intuitive desktop application for memory forensics analysis with visual workflows and interactive results exploration.

## Launching the GUI

```bash
# From the project directory
poetry run python -m oroitz.ui.gui

# Or if in poetry shell
python -m oroitz.ui.gui
```

## Main Interface Overview

The GUI consists of several key components:

- **Landing View**: Welcome screen with quick access to recent sessions and new analysis
- **Session Wizard**: Step-by-step setup for new memory analysis sessions
- **Session Dashboard**: Real-time progress monitoring during analysis
- **Results Explorer**: Interactive data tables with filtering and export capabilities
- **Settings Dialog**: Configuration options for themes, export paths, and preferences

## Creating Your First Analysis

### Step 1: Start a New Session

1. Launch the GUI application
2. On the landing page, click **"New Session"**
3. The session wizard will open

### Step 2: Configure Analysis Parameters

1. **Select Workflow**: Choose "Quick Triage" for an overview analysis
2. **Choose Memory Image**:
   - Click "Browse" to select your memory dump file
   - Supported formats: `.mem`, `.raw`, `.vmem`, `.img`
   - Volatility 3 will automatically detect the appropriate symbol tables for your image

### Step 3: Run Analysis

1. Click **"Start Analysis"**
2. The session dashboard will show real-time progress
3. Wait for completion (typically 1-5 minutes depending on image size)

### Step 4: Explore Results

1. Once analysis completes, click **"View Results"**
2. The results explorer opens with three main tabs:
   - **Processes**: Running process information
   - **Network**: Network connections and sockets
   - **Malfind**: Suspicious memory regions

## Using the Results Explorer

### Filtering Data

- **Search**: Use the search box to filter rows by any column value
- **Column Filters**: Click column headers to sort or filter specific columns
- **Multi-select**: Hold Ctrl/Cmd to select multiple rows for export

### Exporting Results

1. Select the data you want to export (or select all)
2. Click **"Export"** button
3. Choose format:
   - **JSON**: Structured data for further analysis
   - **CSV**: Spreadsheet-compatible format
4. Select save location and filename

### Viewing Details

- **Double-click rows** to view detailed information
- **Right-click** for context menu options
- **Column resizing** by dragging column borders

## Advanced Features

### Session Management

- **Save Sessions**: Automatically saves session configuration for reuse
- **Load Previous**: Access recent sessions from the landing page
- **Session History**: View analysis history and re-run previous analyses

### Theming and Customization

1. Go to **Settings** (gear icon in toolbar)
2. Choose from available themes:
   - Light theme for bright environments
   - Dark theme for low-light conditions
3. Configure default export locations
4. Set preferred Volatility profiles

### Keyboard Shortcuts

- **Ctrl+N**: New session
- **Ctrl+O**: Open existing session
- **Ctrl+E**: Export current results
- **Ctrl+S**: Save session
- **F1**: Show help
- **Esc**: Close dialogs

## Workflow Types

### Quick Triage

**Best for**: Initial incident response and overview analysis

**Includes**:

- Process listing with anomaly detection
- Network connection enumeration
- Memory region analysis for suspicious code

**Typical runtime**: 2-3 minutes

### Process Deep Dive

**Best for**: Detailed process analysis and malware investigation

**Includes**:

- Complete process trees
- DLL and handle enumeration
- Process memory mapping

**Typical runtime**: 5-8 minutes

### Network Focus

**Best for**: Network-based threat hunting and C2 detection

**Includes**:

- All network connections and sockets
- Connection state analysis
- Associated process correlation

**Typical runtime**: 3-5 minutes

### Timeline Overview

**Best for**: Temporal analysis of system events

**Includes**:

- Chronological event timeline
- Process creation/exit events
- Network connection timelines

**Typical runtime**: 4-6 minutes

## Troubleshooting

### Common Issues

#### Analysis Won't Start

**Symptoms**: "Start Analysis" button is disabled or clicking does nothing

**Solutions**:

- Ensure a valid memory image file is selected
- Verify the file exists and is readable
- Check that a workflow is selected

#### Empty Results

**Symptoms**: Analysis completes but shows no data

**Solutions**:

- Verify the memory image is valid and not corrupted
- Ensure Volatility 3 is properly installed and accessible
- Check the GUI logs for specific error messages

#### GUI Freezes During Analysis

**Symptoms**: Interface becomes unresponsive during processing

**Solutions**:

- Wait for completion (large images can take time)
- Check system resources (RAM, CPU)
- Close other memory-intensive applications

#### Export Fails

**Symptoms**: Error when trying to export results

**Solutions**:

- Ensure write permissions to the selected directory
- Check available disk space
- Try a different export format

### Performance Tips

- **Large Images**: Use SSD storage for faster I/O
- **Memory Usage**: Ensure at least 8GB RAM for images >2GB
- **Caching**: Re-running the same analysis is faster due to caching
- **Background Processing**: GUI remains responsive during analysis

### Getting Help

- **Tooltips**: Hover over buttons and controls for help
- **Status Bar**: Shows current operation and progress
- **Log Panel**: View detailed execution logs in the dashboard
- **About Dialog**: Access version information and documentation links

## Integration with Other Tools

### Export Formats

- **JSON**: Compatible with jq, Python, JavaScript analysis tools
- **CSV**: Import into Excel, pandas, R for statistical analysis

### Scripting Integration

```python
# Load GUI-exported JSON in Python
import json

with open('results.json', 'r') as f:
    data = json.load(f)

# Analyze processes
processes = data['processes']
suspicious = [p for p in processes if p['handles'] > 1000]

print(f"Found {len(suspicious)} processes with high handle counts")
```

## Best Practices

1. **Start Small**: Begin with Quick Triage to understand the system
2. **Verify Images**: Ensure memory images are valid and from supported OS versions
3. **Export Early**: Save results before closing sessions
4. **Regular Backups**: Keep copies of important analysis results
5. **Version Control**: Track changes in analysis approaches

For CLI usage or advanced scripting, see the [CLI User Guide](cli-guide.md).
