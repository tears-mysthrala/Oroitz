"""Tests for output module."""

import pytest
from pydantic import ValidationError

from oroitz.core.output import (
    MalfindHit,
    NetworkConnection,
    OutputNormalizer,
    ProcessInfo,
    QuickTriageOutput,
)


def test_normalize_pslist():
    """Test normalizing pslist output."""
    normalizer = OutputNormalizer()

    raw_output = [
        {
            "pid": 123,
            "name": "notepad.exe",
            "ppid": 456,
            "threads": 8,
            "handles": 150,
            "session": 1,
            "wow64": True,
            "create_time": "2023-01-01T12:00:00Z",
        }
    ]

    normalized = normalizer.normalize_pslist(raw_output)

    assert len(normalized) == 1
    process = normalized[0]
    assert isinstance(process, ProcessInfo)
    assert process.pid == 123
    assert process.name == "notepad.exe"
    assert process.ppid == 456
    assert process.threads == 8


def test_normalize_netscan():
    """Test normalizing netscan output."""
    normalizer = OutputNormalizer()

    raw_output = [
        {
            "offset": "0x12345678",
            "pid": 1234,
            "owner": "notepad.exe",
            "created": "2023-01-01T12:00:00Z",
            "local_addr": "192.168.1.100:12345",
            "remote_addr": "8.8.8.8:53",
            "state": "ESTABLISHED",
        }
    ]

    normalized = normalizer.normalize_netscan(raw_output)

    assert len(normalized) == 1
    conn = normalized[0]
    assert isinstance(conn, NetworkConnection)
    assert conn.pid == 1234
    assert conn.owner == "notepad.exe"
    assert conn.state == "ESTABLISHED"


def test_normalize_malfind():
    """Test normalizing malfind output."""
    normalizer = OutputNormalizer()

    raw_output = [
        {
            "pid": 5678,
            "process_name": "suspicious.exe",
            "start": "0x400000",
            "end": "0x500000",
            "tag": "MzHeader",
            "protection": "PAGE_EXECUTE_READWRITE",
            "commit_charge": 1024,
            "private_memory": 2048,
        }
    ]

    normalized = normalizer.normalize_malfind(raw_output)

    assert len(normalized) == 1
    hit = normalized[0]
    assert isinstance(hit, MalfindHit)
    assert hit.pid == 5678
    assert hit.process_name == "suspicious.exe"
    assert hit.tag == "MzHeader"


def test_normalize_quick_triage():
    """Test normalizing complete quick triage output."""
    from oroitz.core.executor import ExecutionResult

    normalizer = OutputNormalizer()

    # Mock execution results
    results = [
        ExecutionResult(
            plugin_name="windows.pslist",
            success=True,
            output=[
                {"pid": 4, "name": "System"},
                {"pid": 123, "name": "notepad.exe"},
            ],
            error=None,
            duration=1.0,
            timestamp=1234567890.0,
        ),
        ExecutionResult(
            plugin_name="windows.netscan",
            success=True,
            output=[
                {
                    "pid": 123,
                    "local_addr": "127.0.0.1:80",
                    "remote_addr": "0.0.0.0:0",
                    "state": "LISTENING",
                },
            ],
            error=None,
            duration=0.5,
            timestamp=1234567890.5,
        ),
        ExecutionResult(
            plugin_name="windows.malfind",
            success=True,
            output=[
                {"pid": 999, "process_name": "bad.exe", "tag": "Suspicious"},
            ],
            error=None,
            duration=2.0,
            timestamp=1234567892.0,
        ),
    ]

    normalized = normalizer.normalize_quick_triage(results)

    assert isinstance(normalized, QuickTriageOutput)
    assert len(normalized.processes) == 2
    assert len(normalized.network_connections) == 1
    assert len(normalized.malfind_hits) == 1

    assert normalized.processes[0].pid == 4
    assert normalized.processes[0].name == "System"
    assert normalized.network_connections[0].state == "LISTENING"
    assert normalized.malfind_hits[0].process_name == "bad.exe"


def test_schema_validation_process_info():
    """Test schema validation for ProcessInfo."""
    # Valid process
    process = ProcessInfo(pid=123, name="test.exe")
    assert process.pid == 123

    # Invalid: negative pid
    with pytest.raises(ValidationError):
        ProcessInfo(pid=-1, name="test.exe")

    # Invalid: empty name
    with pytest.raises(ValidationError):
        ProcessInfo(pid=123, name="")

    # Invalid: negative threads
    with pytest.raises(ValidationError):
        ProcessInfo(pid=123, name="test.exe", threads=-1)


def test_schema_validation_network_connection():
    """Test schema validation for NetworkConnection."""
    # Valid connection
    conn = NetworkConnection(pid=123, state="ESTABLISHED")
    assert conn.pid == 123

    # Invalid: negative pid
    with pytest.raises(ValidationError):
        NetworkConnection(pid=-1, state="LISTENING")


def test_schema_validation_malfind_hit():
    """Test schema validation for MalfindHit."""
    # Valid hit
    hit = MalfindHit(pid=123, tag="MzHeader")
    assert hit.pid == 123

    # Invalid: negative pid
    with pytest.raises(ValidationError):
        MalfindHit(pid=-1, tag="Suspicious")

    # Invalid: negative commit_charge
    with pytest.raises(ValidationError):
        MalfindHit(pid=123, commit_charge=-1)
