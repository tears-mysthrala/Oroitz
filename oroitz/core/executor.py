"""Volatility 3 execution wrapper for Oroitz."""

import json
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union

from pydantic import BaseModel

from oroitz.core.cache import cache
from oroitz.core.config import config
from oroitz.core.telemetry import log_event, logger

# Volatility 3 imports with proper type checking
if TYPE_CHECKING:
    import volatility3.framework.automagic as automagic
    import volatility3.framework.contexts as contexts
    import volatility3.framework.plugins as plugins
    from volatility3.cli import CommandLine

try:
    import volatility3.framework.automagic as automagic
    import volatility3.framework.contexts as contexts
    import volatility3.framework.plugins as plugins
    from volatility3.cli import CommandLine

    VOLATILITY_AVAILABLE = True
except ImportError:
    VOLATILITY_AVAILABLE = False
    automagic = None  # type: ignore
    contexts = None  # type: ignore
    plugins = None  # type: ignore
    CommandLine = None  # type: ignore


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
        self, plugin_name: str, image_path: str, **kwargs: Any
    ) -> Tuple[Optional[List[Dict[str, Any]]], int, bool]:
        """Execute a Volatility 3 plugin using Python API."""
        if not VOLATILITY_AVAILABLE:
            logger.warning("Volatility 3 Python API not available, falling back to mock data")
            log_event(
                "plugin_fallback",
                {"plugin": plugin_name, "reason": "volatility_unavailable"},
            )
            return self._get_mock_data(plugin_name), 0, True

        # Use Python API for better integration
        try:
            # Create context and configure
            ctx = contexts.Context()  # type: ignore
            ctx.config["automagic.LayerStacker.single_location"] = f"file://{image_path}"

            # Get available automagics (returns list of classes)
            automagic_classes = automagic.available(ctx)  # type: ignore

            # Choose appropriate automagics for the plugin
            chosen_automagics = automagic.choose_automagic(automagic_classes, plugin_name)  # type: ignore

            # Apply automagics to context
            for amagic in chosen_automagics:
                if amagic.__class__.__name__ == "LayerStacker":
                    ctx.config["automagic.LayerStacker.single_location"] = f"file://{image_path}"
                amagic(ctx)

            # Construct plugin
            plugin = plugins.construct_plugin(ctx, plugin_name, **kwargs)  # type: ignore

            # Run plugin
            treegrid = plugin.run()

            # Convert treegrid to list of dicts
            result = []
            for row in treegrid.get_renderable().rows:  # type: ignore
                result.append(dict(row))

            return result, 1, False

        except Exception as e:
            logger.warning("Volatility 3 Python API failed: %s", e)
            logger.info("Falling back to CLI method")
            return self._execute_volatility_plugin_cli(plugin_name, image_path, **kwargs)

    def _execute_volatility_plugin_cli(
        self, plugin_name: str, image_path: str, **kwargs: Any
    ) -> Tuple[Optional[List[Dict[str, Any]]], int, bool]:
        """Execute a Volatility 3 plugin using CLI as fallback."""
        if not self._volatility_available:
            logger.warning("Volatility 3 CLI not available, falling back to mock data")
            log_event(
                "plugin_fallback",
                {"plugin": plugin_name, "reason": "volatility_unavailable"},
            )
            return self._get_mock_data(plugin_name), 0, True

        # Adjust timeout based on image size for large images
        image_size_gb = self._get_image_size_gb(image_path)
        timeout_seconds = self._calculate_timeout(image_size_gb)

        logger.info(f"Image size: {image_size_gb:.2f} GB, using timeout: {timeout_seconds}s")

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
                    timeout=timeout_seconds,  # Use dynamic timeout
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

        # Fallback: ensure we return a valid tuple on all code paths. This
        # should be rare, but defensively return mock data so callers always
        # receive a (list|None, int, bool) tuple instead of falling off the
        # end of the function (which is what Pylance warns about).
        logger.debug(
            "Falling back to mock data for %s with no exception after attempts=%d",
            plugin_name,
            attempts_taken,
        )
        return self._get_mock_data(plugin_name), int(attempts_taken or 0), True

    def _get_image_size_gb(self, image_path: str) -> float:
        """Get image file size in GB."""
        try:
            from pathlib import Path

            return Path(image_path).stat().st_size / (1024**3)
        except (OSError, AttributeError):
            return 0.0

    def _calculate_timeout(self, image_size_gb: float) -> int:
        """Calculate appropriate timeout based on image size."""
        # Base timeout of 5 minutes for small images
        base_timeout = 300

        # Add 2 minutes per GB for larger images
        if image_size_gb > 1.0:
            additional_timeout = int(image_size_gb * 120)  # 2 minutes per GB
            total_timeout = base_timeout + additional_timeout
            # Cap at 30 minutes for very large images
            return min(total_timeout, 1800)
        else:
            return base_timeout

    def _get_mock_data(self, plugin_name: str) -> List[Dict[str, Any]]:
        """Fallback to mock data when Volatility execution fails."""
        if plugin_name == "windows.pslist":
            return self._mock_pslist()
        elif plugin_name == "windows.netscan":
            return self._mock_netscan()
        elif plugin_name == "windows.malfind":
            return self._mock_malfind()
        elif plugin_name == "windows.pstree":
            return self._mock_pstree()
        elif plugin_name == "windows.dlllist":
            return self._mock_dlllist()
        elif plugin_name == "windows.handles":
            return self._mock_handles()
        elif plugin_name == "windows.psscan":
            return self._mock_psscan()
        elif plugin_name == "windows.sockscan":
            return self._mock_sockscan()
        elif plugin_name == "windows.connections":
            return self._mock_connections()
        elif plugin_name == "windows.timeliner":
            return self._mock_timeliner()
        elif plugin_name == "windows.getservicesids":
            return self._mock_getservicesids()
        else:
            return []

    def execute_plugin(
        self,
        plugin_name: str,
        image_path: str,
        session_id: Optional[str] = None,
        **kwargs: Any,
    ) -> ExecutionResult:
        """Execute a single Volatility plugin."""
        start_time = time.time()
        timestamp = start_time

        # Use session_id or default
        cache_session_id = session_id or "default"

        # Check cache first
        cache_key_params = {"image_path": image_path, **kwargs}
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
                plugin_name, image_path, **kwargs
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

    def execute_workflow(self, workflow_spec: Any, image_path: str) -> List[ExecutionResult]:
        """Execute all plugins in a workflow."""
        results: List[ExecutionResult] = []

        # Adjust concurrency based on image size for large images
        image_size_gb = self._get_image_size_gb(image_path)
        if image_size_gb > 2.0:  # For images > 2GB, reduce concurrency
            adjusted_concurrency = max(1, self.max_concurrency // 2)
            logger.info(
                f"Large image detected ({image_size_gb:.2f} GB), "
                f"reducing concurrency to {adjusted_concurrency}"
            )
        else:
            adjusted_concurrency = self.max_concurrency

        # For very large images (> 4GB), execute sequentially to avoid memory pressure
        if image_size_gb > 4.0:
            logger.info(
                f"Very large image detected ({image_size_gb:.2f} GB), "
                "executing plugins sequentially"
            )
            for plugin in workflow_spec.plugins:
                result = self.execute_plugin(plugin.name, image_path, **plugin.parameters)
                results.append(result)
        else:
            # Use thread pool for normal-sized images
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor(
                max_workers=adjusted_concurrency
            ) as executor:
                futures = []
                future_to_index = {}
                for i, plugin in enumerate(workflow_spec.plugins):
                    future = executor.submit(
                        self.execute_plugin, plugin.name, image_path, **plugin.parameters
                    )
                    futures.append(future)
                    future_to_index[future] = i

                # Collect results in completion order, then sort by original order
                completed_results = []
                for future in concurrent.futures.as_completed(futures):
                    result = future.result()
                    index = future_to_index[future]
                    completed_results.append((index, result))

                # Sort by original order and extract just the results
                completed_results.sort(key=lambda x: x[0])
                results = [result for _, result in completed_results]

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

    def _mock_pstree(self) -> List[Dict[str, Union[str, int, None]]]:
        """Mock data for pstree plugin."""
        return [
            {
                "PID": 4,
                "PPID": 0,
                "ImageFileName": "System",
                "Offset": "0x12345678",
                "Threads": 100,
                "Handles": 500,
                "CreateTime": "2023-01-01T00:00:00Z",
            },
            {
                "PID": 1234,
                "PPID": 4,
                "ImageFileName": "notepad.exe",
                "Offset": "0x87654321",
                "Threads": 8,
                "Handles": 150,
                "CreateTime": "2023-01-01T12:00:00Z",
            },
        ]

    def _mock_dlllist(self) -> List[Dict[str, Union[str, int, None]]]:
        """Mock data for dlllist plugin."""
        return [
            {
                "PID": 1234,
                "Process": "notepad.exe",
                "Base": "0x77400000",
                "Size": 1048576,
                "Name": "kernel32.dll",
                "Path": "C:\\Windows\\System32\\kernel32.dll",
                "LoadTime": "2023-01-01T12:00:00Z",
            },
            {
                "PID": 1234,
                "Process": "notepad.exe",
                "Base": "0x77500000",
                "Size": 524288,
                "Name": "user32.dll",
                "Path": "C:\\Windows\\System32\\user32.dll",
                "LoadTime": "2023-01-01T12:00:01Z",
            },
        ]

    def _mock_handles(self) -> List[Dict[str, Union[str, int, None]]]:
        """Mock data for handles plugin."""
        return [
            {
                "PID": 1234,
                "Process": "notepad.exe",
                "Offset": "0x12345678",
                "HandleValue": 0x1C,
                "Type": "File",
                "GrantedAccess": "0x12019f",
                "Name": "C:\\Users\\user\\Documents\\test.txt",
            },
            {
                "PID": 1234,
                "Process": "notepad.exe",
                "Offset": "0x87654321",
                "HandleValue": 0x20,
                "Type": "Key",
                "GrantedAccess": "0x20019",
                "Name": "\\REGISTRY\\MACHINE\\SOFTWARE\\Microsoft\\Windows",
            },
        ]

    def _mock_psscan(self) -> List[Dict[str, Union[str, int, bool, None]]]:
        """Mock data for psscan plugin."""
        return [
            {
                "Offset": "0x12345678",
                "PID": 1234,
                "PPID": 876,
                "ImageFileName": "notepad.exe",
                "CreateTime": "2023-01-01T12:00:00Z",
                "ExitTime": None,
                "Threads": 8,
                "Handles": 150,
                "SessionId": 1,
                "Wow64": True,
            },
            {
                "Offset": "0x87654321",
                "PID": 5678,
                "PPID": 4,
                "ImageFileName": "explorer.exe",
                "CreateTime": "2023-01-01T11:00:00Z",
                "ExitTime": None,
                "Threads": 12,
                "Handles": 300,
                "SessionId": 1,
                "Wow64": False,
            },
        ]

    def _mock_sockscan(self) -> List[Dict[str, Union[str, int, None]]]:
        """Mock data for sockscan plugin."""
        return [
            {
                "Offset": "0x12345678",
                "PID": 1234,
                "Port": 12345,
                "Proto": 6,
                "AddressFamily": 2,
                "CreateTime": "2023-01-01T12:00:00Z",
                "LocalAddr": "192.168.1.100",
                "ForeignAddr": "8.8.8.8",
            },
        ]

    def _mock_connections(self) -> List[Dict[str, Union[str, int, None]]]:
        """Mock data for connections plugin."""
        return [
            {
                "Offset": "0x12345678",
                "PID": 1234,
                "Owner": "notepad.exe",
                "CreateTime": "2023-01-01T12:00:00Z",
                "LocalAddr": "192.168.1.100",
                "LocalPort": 12345,
                "ForeignAddr": "8.8.8.8",
                "ForeignPort": 53,
                "State": "ESTABLISHED",
            },
        ]

    def _mock_timeliner(self) -> List[Dict[str, Union[str, int, None]]]:
        """Mock data for timeliner plugin."""
        return [
            {
                "Plugin": "windows.pslist",
                "Description": "Process notepad.exe created",
                "CreatedDate": "2023-01-01T12:00:00Z",
                "AccessedDate": None,
                "ModifiedDate": None,
                "ChangedDate": None,
            },
            {
                "Plugin": "windows.netscan",
                "Description": "Network connection established",
                "CreatedDate": "2023-01-01T12:01:00Z",
                "AccessedDate": None,
                "ModifiedDate": None,
                "ChangedDate": None,
            },
        ]

    def _mock_getservicesids(self) -> List[Dict[str, Union[str, int, None]]]:
        """Mock data for getservicesids plugin."""
        return [
            {
                "SID": "S-1-5-18",
                "Name": "NT AUTHORITY\\SYSTEM",
                "Service": "System",
                "Domain": "NT AUTHORITY",
            },
            {
                "SID": "S-1-5-19",
                "Name": "NT AUTHORITY\\LOCAL SERVICE",
                "Service": "Local Service",
                "Domain": "NT AUTHORITY",
            },
        ]
