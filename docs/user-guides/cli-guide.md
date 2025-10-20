# CLI User Guide

The Oroitz Command Line Interface (CLI) provides powerful scripting and automation capabilities for memory forensics analysis.

## Getting Started

```bash
# Activate the virtual environment
poetry shell

# View available commands
python -m oroitz.cli --help
```

## Quick Triage Analysis

The most common operation is running a quick triage analysis:

```bash
python -m oroitz.cli quick-triage /path/to/memory.dump --profile Win10x64_19041 --output results.json
```

### Command Options

- `--profile`: Volatility profile (e.g., `Win10x64_19041`, `Win2008SP1x86`, `LinuxUbuntu1804x64`)
- `--output`: Optional JSON output file path
- `--help`: Show help information

### Example Output

```json
{
  "processes": [
    {
      "pid": 4,
      "name": "System",
      "ppid": 0,
      "threads": 100,
      "handles": 500,
      "session": 0,
      "wow64": false,
      "create_time": "2023-01-01T00:00:00Z",
      "exit_time": null,
      "anomalies": []
    }
  ],
  "network_connections": [
    {
      "offset": "0x12345678",
      "pid": 1234,
      "owner": "notepad.exe",
      "created": "2023-01-01T12:00:00Z",
      "local_addr": "192.168.1.100",
      "local_port": 12345,
      "remote_addr": "8.8.8.8",
      "remote_port": 53,
      "state": "ESTABLISHED"
    }
  ],
  "malfind_hits": [
    {
      "pid": 5678,
      "process_name": "suspicious.exe",
      "start": "0x400000",
      "end": "0x500000",
      "tag": "MzHeader",
      "protection": "PAGE_EXECUTE_READWRITE",
      "commit_charge": 1024,
      "private_memory": 2048
    }
  ]
}
```

## Working with Results

### Using jq for Analysis

```bash
# Count total processes
jq '.processes | length' results.json

# Find processes with many handles
jq '.processes[] | select(.handles > 1000) | {pid, name, handles}' results.json

# List network connections
jq '.network_connections[] | {pid, owner, local_addr, remote_addr, state}' results.json

# Find suspicious processes (high handle count, unusual names)
jq '.processes[] | select(.handles > 500 or (.name | contains("temp") or contains("susp"))) | {pid, name, handles}' results.json
```

### Export to CSV

Oroitz results can be converted to CSV using jq:

```bash
# Export processes to CSV
jq -r '.processes[] | [.pid, .name, .ppid, .threads, .handles] | @csv' results.json > processes.csv

# Export network connections to CSV
jq -r '.network_connections[] | [.pid, .owner, .local_addr, .remote_addr, .state] | @csv' results.json > network.csv
```

## Automation Examples

### Batch Processing Multiple Images

```bash
#!/bin/bash
# batch_triage.sh

IMAGES_DIR="/path/to/memory/images"
OUTPUT_DIR="./results"
PROFILE="Win10x64_19041"

mkdir -p "$OUTPUT_DIR"

for image in "$IMAGES_DIR"/*.mem; do
    basename=$(basename "$image" .mem)
    output="$OUTPUT_DIR/${basename}_triage.json"

    echo "Processing $image..."
    python -m oroitz.cli quick-triage "$image" --profile "$PROFILE" --output "$output"

    # Quick summary
    process_count=$(jq '.processes | length' "$output")
    network_count=$(jq '.network_connections | length' "$output")
    malfind_count=$(jq '.malfind_hits | length' "$output")

    echo "  Processes: $process_count"
    echo "  Network connections: $network_count"
    echo "  Malfind hits: $malfind_count"
done
```

### Integration with Other Tools

```bash
# Process results with Python
python -m oroitz.cli quick-triage memory.dump --output results.json

# Load and analyze in Python
python3 << 'EOF'
import json
with open('results.json') as f:
    data = json.load(f)

# Find suspicious processes
suspicious = []
for proc in data['processes']:
    if proc['handles'] > 1000 or 'susp' in proc['name'].lower():
        suspicious.append(proc)

print(f"Found {len(suspicious)} suspicious processes")
for proc in suspicious[:5]:  # Show first 5
    print(f"  PID {proc['pid']}: {proc['name']} ({proc['handles']} handles)")
EOF
```

## Error Handling

The CLI provides clear error messages for common issues:

### Invalid Profile

```bash
python -m oroitz.cli quick-triage memory.dump --profile InvalidProfile
# Error: Profile 'InvalidProfile' is not supported
```

### Missing Image File

```bash
python -m oroitz.cli quick-triage nonexistent.dump --profile Win10x64_19041
# Error: File 'nonexistent.dump' does not exist
```

### Volatility Execution Issues

```bash
python -m oroitz.cli quick-triage memory.dump --profile Win10x64_19041
# Falls back to mock data with warning if Volatility 3 is not available
```

## Advanced Usage

### Custom Profiles

Oroitz supports standard Volatility 3 profiles:

- Windows: `Win7SP1x64`, `Win10x64_19041`, `Win2008SP1x86`
- Linux: `LinuxUbuntu1804x64`, `LinuxCentOS7x64`
- macOS: `Mac10_15_7ARM`, `Mac10_14_6x64`

### Memory Image Requirements

- Raw memory dumps (`.mem`, `.raw`)
- VMware memory files (`.vmem`)
- VirtualBox memory files
- Hyper-V memory files

### Performance Considerations

- Large memory images (>4GB) may take several minutes to analyze
- Results are cached automatically for faster re-analysis
- Use `--output` to save results and avoid re-running analysis

## Troubleshooting

### Common Issues

#### Volatility 3 not found

- Ensure Volatility 3 is installed: `pip install volatility3`
- Or use the provided mock data fallback

#### Profile not supported

- Check available profiles: `python -m oroitz.cli quick-triage --help`
- Verify the profile matches your memory image OS/version

#### Permission denied

- Ensure read access to memory image files
- Check write permissions for output directories

### Getting Help

```bash
# Show all commands
python -m oroitz.cli --help

# Show quick-triage options
python -m oroitz.cli quick-triage --help
```

For more advanced usage or to report issues, see the [main documentation](../README.md).
