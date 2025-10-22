"""Tests for executor retry and fallback behavior."""

import json
from unittest.mock import MagicMock, patch

from oroitz.core.config import config
from oroitz.core.executor import Executor


def _make_result(returncode: int, stdout: str = "", stderr: str = ""):
    mock = MagicMock()
    mock.returncode = returncode
    mock.stdout = stdout
    mock.stderr = stderr
    return mock


def test_retry_then_success(monkeypatch):
    """Simulate a transient failure followed by success; ensure attempts count increments."""
    # Reduce backoff to 0 for test speed and set attempts to 3
    config.volatility_retry_attempts = 3
    config.volatility_retry_backoff_seconds = 0

    # Clear any existing cache to ensure retries are exercised
    from oroitz.core.cache import cache

    cache.clear()

    executor = Executor()
    # Force the executor to believe volatility is available and set command
    executor._volatility_available = True
    executor._vol_command = ["vol"]

    # First attempt fails, second succeeds
    fail = _make_result(1, stdout="", stderr="transient")
    success_stdout = json.dumps([{"PID": 42, "ImageFileName": "proc.exe"}])
    success = _make_result(0, stdout=success_stdout, stderr="")

    # Force Python API to fail so we test CLI retry logic
    with (
        patch("oroitz.core.executor.contexts.Context", side_effect=Exception("Python API failed")),
        patch("oroitz.core.executor.subprocess.run", side_effect=[fail, success]),
    ):
        result = executor.execute_plugin("windows.pslist", "/fake/image")

    assert result.success
    assert result.output is not None
    assert result.attempts == 2
    assert result.used_mock is False


def test_permanent_failure_fallback(monkeypatch):
    """Simulate repeated failures to ensure fallback to mock data and used_mock is True."""
    # Use 3 attempts and no backoff to speed up
    config.volatility_retry_attempts = 3
    config.volatility_retry_backoff_seconds = 0

    # Clear any existing cache to ensure retries are exercised
    from oroitz.core.cache import cache

    cache.clear()

    executor = Executor()
    executor._volatility_available = True
    executor._vol_command = ["vol"]

    fail = _make_result(1, stdout="", stderr="error")

    # All attempts fail
    with (
        patch("oroitz.core.executor.contexts.Context", side_effect=Exception("Python API failed")),
        patch("oroitz.core.executor.subprocess.run", side_effect=[fail, fail, fail]),
    ):
        result = executor.execute_plugin("windows.pslist", "/fake/image")

    assert result.success  # fallback returns mock data, but marked as success
    assert result.used_mock is True
    assert result.attempts == config.volatility_retry_attempts
    assert isinstance(result.output, list)
