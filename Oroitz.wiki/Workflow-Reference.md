# Workflow Reference

This guide provides detailed information about each available workflow in Oroitz, including what data they collect, typical use cases, and output formats.

## Quick Triage

**Overview**: The primary entry point for memory forensics analysis. Provides a comprehensive overview of system state with minimal runtime.

**Plugins Executed**:

- `windows.pslist` - Process listing with basic information
- `windows.netscan` - Network connections and sockets
- `windows.malfind` - Suspicious memory regions

**Output Data**:

### Processes

```json
{
  "pid": 1234,
  "name": "notepad.exe",
  "ppid": 876,
  "threads": 8,
  "handles": 150,
  "session": 1,
  "wow64": true,
  "create_time": "2023-01-01T12:00:00Z",
  "exit_time": null,
  "anomalies": []
}
```

**Fields**:

- `pid`: Process ID (integer)
- `name`: Process executable name (string)
- `ppid`: Parent process ID (integer, optional)
- `threads`: Number of threads (integer, optional)
- `handles`: Number of open handles (integer, optional)
- `session`: Session ID (integer, optional)
- `wow64`: 32-bit process on 64-bit system (boolean, optional)
- `create_time`: Process creation timestamp (ISO 8601 string, optional)
- `exit_time`: Process exit timestamp (ISO 8601 string, optional)
- `anomalies`: List of detected anomalies (array of strings)

### Network Connections

```json
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
```

**Fields**:

- `offset`: Memory offset of connection structure (hex string, optional)
- `pid`: Owning process ID (integer, optional)
- `owner`: Process name (string, optional)
- `created`: Connection creation timestamp (ISO 8601 string, optional)
- `local_addr`: Local IP address (string, optional)
- `local_port`: Local port number (integer, optional)
- `remote_addr`: Remote IP address (string, optional)
- `remote_port`: Remote port number (integer, optional)
- `state`: Connection state (string, optional)

### Malfind Hits

```json
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
```

**Fields**:

- `pid`: Process ID (integer, optional)
- `process_name`: Process executable name (string, optional)
- `start`: Memory region start address (hex string, optional)
- `end`: Memory region end address (hex string, optional)
- `tag`: Memory content signature (string, optional)
- `protection`: Memory protection flags (string, optional)
- `commit_charge`: Committed memory pages (integer, optional)
- `private_memory`: Private memory pages (integer, optional)

**Typical Runtime**: 2-3 minutes
**Use Cases**: Initial triage, incident response overview, system reconnaissance

## Process Deep Dive

**Overview**: Comprehensive process analysis including relationships, dependencies, and resource usage.

**Plugins Executed**:

- `windows.pstree` - Process tree hierarchy
- `windows.dlllist` - DLL dependencies
- `windows.handles` - Open handles and resources
- `windows.psscan` - Hidden/unlinked processes

**Output Data**:

### Process Tree

Hierarchical representation of process relationships with parent-child connections.

### DLL Inventory

```json
{
  "pid": 1234,
  "process_name": "notepad.exe",
  "dll_base": "0x77400000",
  "dll_name": "kernel32.dll",
  "dll_path": "C:\\Windows\\System32\\kernel32.dll",
  "size": 851968,
  "load_count": 1
}
```

### Handle Information

```json
{
  "pid": 1234,
  "handle_value": "0x1a4",
  "handle_type": "File",
  "handle_name": "\\Device\\HarddiskVolume2\\Windows\\System32\\notepad.exe",
  "granted_access": "0x12019f"
}
```

**Typical Runtime**: 5-8 minutes
**Use Cases**: Malware analysis, process investigation, dependency mapping

## Network Focus

**Overview**: Detailed network activity analysis for command-and-control detection and network forensics.

**Plugins Executed**:

- `windows.netscan` - Network connections
- `windows.sockscan` - Socket information
- `windows.connections` - Connection details

**Output Data**:

### Network Connections (Enhanced)

Extended connection information with additional metadata and state analysis.

### Socket Information

```json
{
  "offset": "0x8234c8e0",
  "pid": 1234,
  "socket": "0x8234c8e0",
  "family": "AF_INET",
  "protocol": "TCP",
  "local_addr": "0.0.0.0:80",
  "remote_addr": "0.0.0.0:0",
  "state": "LISTENING"
}
```

### Connection Details

```json
{
  "pid": 1234,
  "owner": "httpd.exe",
  "create_time": "2023-01-01T10:30:00Z",
  "local_addr": "192.168.1.100:80",
  "remote_addr": "10.0.0.5:54321",
  "state": "ESTABLISHED",
  "bytes_sent": 1024,
  "bytes_received": 2048
}
```

**Typical Runtime**: 3-5 minutes
**Use Cases**: C2 detection, network forensics, lateral movement analysis

## Timeline Overview

**Overview**: Chronological reconstruction of system events for temporal analysis and event correlation.

**Plugins Executed**:

- `windows.timeliner` - System event timeline
- `windows.getservicesids` - Service account information

**Output Data**:

### Timeline Events

```json
{
  "timestamp": "2023-01-01T12:00:00Z",
  "source": "Process",
  "event_type": "Process Create",
  "description": "Process notepad.exe (PID: 1234) created by explorer.exe (PID: 876)",
  "details": {
    "pid": 1234,
    "ppid": 876,
    "image_path": "C:\\Windows\\System32\\notepad.exe"
  }
}
```

**Fields**:

- `timestamp`: Event timestamp (ISO 8601 string)
- `source`: Event source category (string)
- `event_type`: Specific event type (string)
- `description`: Human-readable description (string)
- `details`: Structured event data (object)

### Service Accounts

```json
{
  "service_name": "Windows Update",
  "service_path": "C:\\Windows\\System32\\svchost.exe",
  "account_name": "LocalSystem",
  "account_sid": "S-1-5-18",
  "start_type": "Automatic",
  "current_state": "Running"
}
```

**Typical Runtime**: 4-6 minutes
**Use Cases**: Event reconstruction, timeline analysis, incident timeline creation

## Output Formats

All workflows produce results in the following formats:

### JSON Export

Structured data suitable for:

- Programmatic analysis
- Import into other tools
- Long-term storage
- API integration

### CSV Export

Tabular data suitable for:

- Spreadsheet analysis (Excel, Google Sheets)
- Database import
- Reporting tools
- Manual review

### Schema Validation

All outputs are validated against Pydantic schemas ensuring:

- Data type consistency
- Required field presence
- Value range validation
- Automatic error detection

## Performance Characteristics

| Workflow | Runtime | Memory Usage | CPU Usage | Disk I/O |
|----------|---------|--------------|-----------|----------|
| Quick Triage | 2-3 min | Low | Medium | Low |
| Process Deep Dive | 5-8 min | Medium | High | Medium |
| Network Focus | 3-5 min | Low | Medium | Low |
| Timeline Overview | 4-6 min | High | High | High |

## Selecting a Workflow

### For Incident Response

1. **Start with Quick Triage** - Get overview in 2-3 minutes
2. **Follow with Process Deep Dive** - If suspicious processes found
3. **Use Network Focus** - If network indicators present
4. **Create Timeline** - For event reconstruction

### For Malware Analysis

1. **Quick Triage** - Initial assessment
2. **Process Deep Dive** - DLL analysis and handle inspection
3. **Network Focus** - C2 communication detection
4. **Timeline Overview** - Infection chain reconstruction

### For Network Forensics

1. **Network Focus** - Primary network analysis
2. **Quick Triage** - Process context
3. **Timeline Overview** - Network event correlation

## Custom Workflows

Oroitz supports extensible workflows. To add custom workflows:

1. Define workflow specification in `oroitz.core.workflow`
2. Implement data normalization in `oroitz.core.output`
3. Add UI support in GUI/TUI interfaces
4. Update documentation

See the [development documentation](../README.md) for implementation details.
