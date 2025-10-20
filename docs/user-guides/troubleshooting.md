# Troubleshooting Guide

This guide helps resolve common issues when using Oroitz for memory forensics analysis.

## Installation Issues

### Poetry Not Found

**Error**: `poetry: command not found`

**Solution**:

```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Add to PATH
export PATH="$HOME/.local/bin:$PATH"

# Verify installation
poetry --version
```

### Python Version Issues

**Error**: `Python 3.11 or higher required`

**Solution**:

```bash
# Check current version
python3 --version

# Install Python 3.11+ if needed
# On Ubuntu/Debian:
sudo apt update
sudo apt install python3.11 python3.11-venv

# On macOS with Homebrew:
brew install python@3.11

# On Windows: Download from python.org
```

### Dependency Installation Fails

**Error**: Poetry install fails with package conflicts

**Solution**:

```bash
# Clear Poetry cache
poetry cache clear --all pypi

# Update Poetry
poetry self update

# Try installation again
poetry install

# If still failing, check lock file
poetry lock --no-update
poetry install
```

## Runtime Issues

### CLI Command Not Found

**Error**: `python -m oroitz.cli: No module named oroitz`

**Solution**:

```bash
# Ensure you're in the correct directory
cd /path/to/oroitz

# Activate Poetry shell
poetry shell

# Or prefix commands with poetry run
poetry run python -m oroitz.cli --help
```

### Memory Image Not Found

**Error**: `File 'memory.dump' does not exist`

**Solution**:

```bash
# Check file exists
ls -la memory.dump

# Use absolute path
python -m oroitz.cli quick-triage /full/path/to/memory.dump

# Check file permissions
stat memory.dump
```

### Unsupported Memory Image

**Error**: `Analysis failed - unsupported OS or corrupted image`

**Supported Systems**:

- Windows (7, 8, 10, 11, Server variants)
- Linux (most distributions with kernel 3.0+)
- macOS (10.14+)

**Solution**:

```bash
# Check image format
file memory.dump

# Try with known good sample
python -m oroitz.cli quick-triage samples/memdump.mem

# Verify Volatility 3 can read the image
volatility3 -f memory.dump imageinfo
```

### Analysis Takes Too Long

**Symptoms**: Command runs for >10 minutes without output

**Solutions**:

- Check system resources (RAM, CPU)
- Try smaller memory image for testing
- Use `top` or `htop` to monitor resource usage
- Kill and restart if needed

### Mock Data Warning

**Warning**: `Volatility 3 CLI not available, falling back to mock data`

**Solution**: This is normal for development. For real analysis:

```bash
# Install Volatility 3
pip install volatility3

# Or use the provided memory samples
python -m oroitz.cli quick-triage samples/memdump.mem
```

## GUI Issues

### GUI Won't Start

**Error**: PySide6 import errors or window doesn't appear

**Solutions**:

```bash
# Install GUI dependencies
poetry install

# Check display (Linux)
echo $DISPLAY

# Try with virtual display (Linux)
poetry run python -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; import PySide6"

# Check Python version compatibility
python3 --version  # Should be 3.11+
```

### GUI Freezes During Analysis

**Symptoms**: Interface becomes unresponsive

**Solutions**:

- Wait for completion (large images take time)
- Monitor system resources
- Close other memory-intensive applications
- Try smaller test image first

### Export Fails in GUI

**Error**: Cannot save file

**Solutions**:

- Check write permissions in target directory
- Ensure sufficient disk space
- Try different filename/location
- Check if file is already open

## TUI Issues

### TUI Won't Start

**Error**: Textual import errors

**Solutions**:

```bash
# Install TUI dependencies
poetry install

# Check terminal capabilities
echo $TERM

# Try different terminal
# Ensure terminal is at least 80x24 characters
```

### TUI Display Issues

**Symptoms**: Garbled text, wrong colors, layout problems

**Solutions**:

- Use a modern terminal (iTerm2, GNOME Terminal, Windows Terminal)
- Ensure terminal supports 256 colors
- Set terminal size to at least 120x30
- Try: `export TERM=xterm-256color`

### Keyboard Input Not Working

**Symptoms**: Arrow keys don't navigate

**Solutions**:

- Ensure terminal sends correct key codes
- Try different terminal application
- Check if running inside tmux/screen (may need configuration)

## Data Analysis Issues

### Empty Results

**Symptoms**: Analysis completes but no data returned

**Causes**:

- Corrupted memory image
- Unsupported OS version
- Volatility 3 installation issues

**Solutions**:

```bash
# Verify image integrity
file memory.dump
stat memory.dump

# Check with Volatility 3 directly
volatility3 -f memory.dump imageinfo
```

### Unexpected Data Format

**Symptoms**: JSON structure different than expected

**Solutions**:

- Check schema documentation
- Use `jq` to explore structure: `cat results.json | jq '.processes[0]'`
- Validate with Python: `python3 -c "import json; print(json.load(open('results.json')).keys())"`

### Large File Sizes

**Issue**: Result files are very large

**Solutions**:

- Use compression: `gzip results.json`
- Export only needed data: `jq '.processes' results.json > processes.json`
- Use CSV for spreadsheet analysis

## Performance Optimization

### Speed Up Analysis

```bash
# Use faster storage (SSD preferred)
# Ensure adequate RAM (8GB+ recommended)
# Close unnecessary applications
```

### Reduce Memory Usage

```bash
# Process smaller images first
# Use streaming analysis if available
# Monitor with `top` or `htop`
# Kill long-running processes if needed
```

### Optimize Storage

```bash
# Use external storage for large memory images
# Compress old result files
# Clean up temporary files regularly
```

## Getting Help

### Debug Information

```bash
# Get system information
python3 -c "import sys, platform; print(f'Python: {sys.version}'); print(f'OS: {platform.platform()}')"

# Check installed packages
poetry show

# Test basic functionality
python3 -c "import oroitz.core.workflow; print('Core import OK')"
```

### Log Files

Oroitz logs to console by default. For more detailed logging:

```bash
# Enable debug logging
python -m oroitz.cli --log-level DEBUG quick-triage memory.dump

# Redirect logs to file
python -m oroitz.cli quick-triage memory.dump 2>&1 | tee analysis.log
```

### Community Support

- Check [GitHub Issues](https://github.com/tears-mysthrala/Oroitz/issues) for similar problems
- File bug reports with:
  - Full error messages
  - System information
  - Steps to reproduce
  - Memory image details (if possible)

### Professional Support

For enterprise deployments or complex issues, consider:

- Commercial Volatility support
- Forensic consulting services
- Training courses on memory analysis
