"""Volatility 3 execution wrapper for Oroitz."""

import json
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional, Tuple, Union

from pydantic import BaseModel

from oroitz.core.cache import cache
from oroitz.core.config import config
from oroitz.core.telemetry import log_event, logger

# Volatility 3 imports - only for checking availability
VOLATILITY_AVAILABLE = True
try:
    import volatility3
except ImportError:
    VOLATILITY_AVAILABLE = False
    volatility3 = None


class ExecutionResult(BaseModel):
    """Result of a plugin execution."""

    plugin_name: str
    success: bool
    output: Optional[Any] = None
    error: Optional[str] = None
    duration: float
    timestamp: float
    attempts: int = 1
    used_mock: bool = False


class Executor:
    """Handles execution of Volatility plugins."""

    def __init__(self) -> None:
        self.max_concurrency = config.max_concurrency
        self.executor = ThreadPoolExecutor(max_workers=self.max_concurrency)
        # Check if volatility3 CLI is available
        self._volatility_available = self._check_volatility_cli()

    def _check_volatility_cli(self) -> bool:
        """Check if volatility3 CLI is available."""
        try:
            # Try using poetry run vol first
            result = subprocess.run(
                ["poetry", "run", "vol"], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 2:  # 2 means help/usage shown, which means vol is available
                self._vol_command = ["poetry", "run", "vol"]
                return True

            # Fallback to just vol
            result = subprocess.run(["vol"], capture_output=True, text=True, timeout=10)
            if result.returncode == 2:
                self._vol_command = ["vol"]
                return True

            return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _execute_volatility_plugin(
        self, plugin_name: str, image_path: str, profile: str = "", **kwargs: Any
    ) -> Tuple[Optional[List[Dict[str, Any]]], int, bool]:
        """Execute a Volatility 3 plugin using CLI and return normalized output."""
        if not self._volatility_available:
            logger.warning("Volatility 3 CLI not available, falling back to mock data")
            log_event(
                "plugin_fallback",
                {"plugin": plugin_name, "reason": "volatility_unavailable"},
            )
            return self._get_mock_data(plugin_name), 0, True

        # Retry loop for transient failures
        attempts = max(1, getattr(config, "volatility_retry_attempts", 1))
        backoff = float(getattr(config, "volatility_retry_backoff_seconds", 0))

        last_exception = None
        attempts_taken = 0
        for attempt in range(1, attempts + 1):
            try:
                # Build command - Volatility 3 auto-detects symbol tables
                cmd = self._vol_command + ["-f", image_path, "-r", "json"]

                # Add plugin name
                cmd.append(plugin_name)

                # Add any additional parameters
                for key, value in kwargs.items():
                    if isinstance(value, bool):
                        if value:
                            cmd.append(f"--{key}")
                    else:
                        cmd.append(f"--{key}={value}")

                logger.info("Running command: %s", " ".join(cmd))

                # Execute command
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300,  # 5 minute timeout
                    cwd=None,  # Use current directory
                )

                if result.returncode != 0:
                    # Non-zero return code - treat as possible transient failure
                    logger.warning(
                        "Volatility plugin %s failed (attempt %d/%d): %s",
                        plugin_name,
                        attempt,
                        attempts,
                        result.stderr,
                    )
                    last_exception = RuntimeError(result.stderr)
                    log_event(
                        "plugin_retry",
                        {"plugin": plugin_name, "attempt": attempt, "reason": result.stderr},
                    )
                    # If more attempts remain, retry (sleep only if backoff > 0)
                    if attempt < attempts:
                        if backoff > 0:
                            time.sleep(backoff * (2 ** (attempt - 1)))
                        continue
                    attempts_taken = attempt
                    log_event(
                        "plugin_fallback",
                        {"plugin": plugin_name, "attempts": attempts},
                    )
                    return self._get_mock_data(plugin_name), attempts_taken, True

                # Parse JSON output
                try:
                    output_data = json.loads(result.stdout)
                except json.JSONDecodeError as e:
                    logger.warning("Failed to parse JSON output from %s: %s", plugin_name, e)
                    log_event(
                        "plugin_retry",
                        {"plugin": plugin_name, "attempt": attempt, "reason": "json_error"},
                    )
                    logger.debug("Raw output: %s", result.stdout[:500])
                    if attempt < attempts:
                        if backoff > 0:
                            time.sleep(backoff * (2 ** (attempt - 1)))
                        continue
                    attempts_taken = attempt
                    log_event(
                        "plugin_fallback",
                        {"plugin": plugin_name, "attempts": attempts},
                    )
                    return self._get_mock_data(plugin_name), attempts_taken, True

                # Volatility 3 JSON output is usually wrapped in a structure
                # Extract the actual data
                if isinstance(output_data, dict):
                    # Find the data array - it might be under different keys
                    for key, value in output_data.items():
                        if isinstance(value, list) and value and isinstance(value[0], dict):
                            attempts_taken = attempt
                            return value, attempts_taken, False
                    # If no list found, return empty list
                    attempts_taken = attempt
                    return [], attempts_taken, False
                elif isinstance(output_data, list):
                    attempts_taken = attempt
                    return output_data, attempts_taken, False
                else:
                    logger.warning("Unexpected output format from %s", plugin_name)
                    attempts_taken = attempt
                    log_event(
                        "plugin_fallback",
                        {
                            "plugin": plugin_name,
                            "attempts": attempts,
                            "reason": "unexpected_format",
                        },
                    )
                    return self._get_mock_data(plugin_name), attempts_taken, True

            except subprocess.TimeoutExpired as e:
                logger.error(
                    "Volatility plugin %s timed out (attempt %d/%d)",
                    plugin_name,
                    attempt,
                    attempts,
                )
                last_exception = e
                log_event(
                    "plugin_retry",
                    {"plugin": plugin_name, "attempt": attempt, "reason": str(e)},
                )
                if attempt < attempts:
                    if backoff > 0:
                        time.sleep(backoff * (2 ** (attempt - 1)))
                    continue
                attempts_taken = attempt
                log_event(
                    "plugin_fallback",
                    {"plugin": plugin_name, "attempts": attempts, "reason": str(e)},
                )
                return self._get_mock_data(plugin_name), attempts_taken, True
            except Exception as e:
                logger.error(
                    "Failed to execute Volatility plugin %s (attempt %d/%d): %s",
                    plugin_name,
                    attempt,
                    attempts,
                    e,
                )
                last_exception = e
                if attempt < attempts:
                    if backoff > 0:
                        time.sleep(backoff * (2 ** (attempt - 1)))
                    continue
                attempts_taken = attempt
                return self._get_mock_data(plugin_name), attempts_taken, True

        # If we get here, and last_exception is set, return mock data as fallback
        if last_exception is not None:
            logger.debug("Returning mock data for %s after %d attempts", plugin_name, attempts)
            log_event(
                "plugin_fallback",
                {"plugin": plugin_name, "attempts": attempts, "reason": str(last_exception)},
            )
            return self._get_mock_data(plugin_name), attempts, True

    def _get_mock_data(self, plugin_name: str) -> List[Dict[str, Any]]:
        """Fallback to mock data when Volatility execution fails."""
        if plugin_name == "windows.pslist":
            return self._mock_pslist()
        elif plugin_name == "windows.netscan":
            return self._mock_netscan()
        elif plugin_name == "windows.malfind":
            return self._mock_malfind()
        else:
            return []

    def execute_plugin(
        self,
        plugin_name: str,
        image_path: str,
        profile: str = "",
        session_id: Optional[str] = None,
        **kwargs: Any,
    ) -> ExecutionResult:
        """Execute a single Volatility plugin."""
        start_time = time.time()
        timestamp = start_time

        # Use session_id or default
        cache_session_id = session_id or "default"

        # Check cache first
        cache_key_params = {"image_path": image_path, "profile": profile, **kwargs}
        cached_result = cache.get(cache_session_id, plugin_name, cache_key_params)
        if cached_result is not None:
            logger.info(f"Using cached result for {plugin_name}")
            return ExecutionResult(
                plugin_name=plugin_name,
                success=True,
                output=cached_result,
                error=None,
                duration=0.0,  # Cached, no execution time
                timestamp=timestamp,
            )

        try:
            log_event("plugin_start", {"plugin": plugin_name, "image": image_path})

            # Execute real Volatility 3 plugin
            output, attempts_taken, used_mock = self._execute_volatility_plugin(
                plugin_name, image_path, profile, **kwargs
            )

            # Cache the result (store only the output)
            cache.set(cache_session_id, plugin_name, cache_key_params, output)

            success = True
            error = None
            log_event(
                "plugin_success", {"plugin": plugin_name, "duration": time.time() - start_time}
            )

        except Exception as e:
            success = False
            output: Optional[List[Dict[str, Any]]] = None  # Error case, output is None
            error = str(e)
            logger.error(f"Plugin {plugin_name} failed: {e}")
            log_event("plugin_error", {"plugin": plugin_name, "error": error})

        duration = time.time() - start_time

        # Ensure attempts and used_mock are set even on exceptions/cached results
        attempts_value = int(locals().get("attempts_taken", 0))
        used_mock_value = bool(locals().get("used_mock", False))

        return ExecutionResult(
            plugin_name=plugin_name,
            success=success,
            output=output,
            error=error,
            duration=duration,
            timestamp=timestamp,
            attempts=attempts_value,
            used_mock=used_mock_value,
        )

    def execute_workflow(
        self, workflow_spec: Any, image_path: str, profile: str = ""
    ) -> List[ExecutionResult]:
        """Execute all plugins in a workflow."""
        results: List[ExecutionResult] = []

        for plugin in workflow_spec.plugins:
            result = self.execute_plugin(plugin.name, image_path, profile, **plugin.parameters)
            results.append(result)

        return results

    def _mock_pslist(self) -> List[Dict[str, Union[str, int, bool, None]]]:
        """Mock data for pslist plugin."""
        return [
            {
                "PID": 4,
                "ImageFileName": "System",
                "PPID": 0,
                "Threads": 100,
                "Handles": 500,
                "SessionId": 0,
                "Wow64": False,
                "CreateTime": "2023-01-01T00:00:00Z",
                "ExitTime": None,
            },
            {
                "PID": 1234,
                "ImageFileName": "notepad.exe",
                "PPID": 876,
                "Threads": 8,
                "Handles": 150,
                "SessionId": 1,
                "Wow64": True,
                "CreateTime": "2023-01-01T12:00:00Z",
                "ExitTime": None,
            },
        ]

    def _mock_netscan(self) -> List[Dict[str, Union[str, int, None]]]:
        """Mock data for netscan plugin."""
        return [
            {
                "Offset": "0x12345678",
                "PID": 1234,
                "Owner": "notepad.exe",
                "Created": "2023-01-01T12:00:00Z",
                "LocalAddr": "192.168.1.100",
                "LocalPort": 12345,
                "ForeignAddr": "8.8.8.8",
                "ForeignPort": 53,
                "State": "ESTABLISHED",
            },
        ]

    def _mock_malfind(self) -> List[Dict[str, Union[str, int, None]]]:
        """Mock data for malfind plugin."""
        return [
            {
                "PID": 5678,
                "Process": "suspicious.exe",
                "Start VPN": "0x400000",
                "End VPN": "0x500000",
                "Tag": "MzHeader",
                "Protection": "PAGE_EXECUTE_READWRITE",
                "CommitCharge": 1024,
                "PrivateMemory": 2048,
            },
        ]
