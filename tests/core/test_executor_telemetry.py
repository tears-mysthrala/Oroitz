"""Telemetry tests for executor retry/fallback events."""

from unittest.mock import patch

from oroitz.core.config import config
from oroitz.core.executor import Executor


def test_retry_and_fallback_telemetry():
    # Configure retries
    config.volatility_retry_attempts = 2
    config.volatility_retry_backoff_seconds = 0

    executor = Executor()
    executor._volatility_available = True
    executor._vol_command = ["vol"]

    from oroitz.core.cache import cache

    cache.clear()

    # Simulate two failing runs to hit failure
    fail = type("R", (), {"returncode": 1, "stdout": "", "stderr": "err"})

    with patch("oroitz.core.executor.subprocess.run", side_effect=[fail, fail]):
        # Patch the log_event as imported into the executor module
        with patch("oroitz.core.executor.log_event") as mock_log:
            executor.execute_plugin("windows.pslist", "/fake/image", "windows")

            # Should have emitted retry and error events
            calls = [c[0][0] for c in mock_log.call_args_list]
            assert "plugin_retry" in calls
            assert "plugin_error" in calls
