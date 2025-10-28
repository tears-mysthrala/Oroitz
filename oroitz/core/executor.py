"""Volatility 3 execution wrapper for Oroitz."""

import json
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

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
    import volatility3
    import volatility3.framework as framework
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
    ) -> Tuple[Optional[List[Dict[str, Any]]], int]:
        """Execute a Volatility 3 plugin using Python API."""
        if not VOLATILITY_AVAILABLE:
            raise RuntimeError("Volatility 3 Python API not available")

        # Use Python API for better integration
        try:
            # Create context and configure
            ctx = contexts.Context()  # type: ignore
            ctx.config["automagic.LayerStacker.single_location"] = f"file://{image_path}"

            # Import plugin files and build list (mirror CLI behavior)
            failures = framework.import_files(volatility3.plugins, True)  # type: ignore
            if failures:
                logger.debug("Volatility plugin import failures: %s", failures)
            plugin_list = framework.list_plugins()

            # Resolve plugin name to the plugin class/type expected by volatility3
            plugin_class = plugin_list.get(plugin_name)
            if plugin_class is None:
                # Try to find plugin by partial name match
                # (e.g., 'windows.pslist' -> 'windows.pslist.PsList')
                matching_plugins = [
                    name for name in plugin_list.keys() if plugin_name in name.lower()
                ]
                if matching_plugins:
                    # Take the first match (should be the most relevant)
                    plugin_name_full = matching_plugins[0]
                    plugin_class = plugin_list[plugin_name_full]
                    logger.info(f"Resolved plugin name '{plugin_name}' to '{plugin_name_full}'")
                else:
                    raise RuntimeError(f"Could not find Volatility plugin: {plugin_name}")

            # Get available automagics (returns list of classes)
            automagic_classes = automagic.available(ctx)  # type: ignore

            # Choose appropriate automagics for the plugin (pass the plugin class/type)
            assert automagic is not None  # VOLATILITY_AVAILABLE ensures this
            chosen_automagics = automagic.choose_automagic(automagic_classes, plugin_class)  # type: ignore

            # Construct plugin (pass the plugin class/type, and follow construct_plugin signature)
            # construct_plugin(ctx, automagics, plugin, base_config_path, progress_callback, open_method)  # noqa: E501
            # For our use, we can pass an empty base_config_path and a simple progress callback
            def _noop_progress(progress, msg):
                return None

            constructed = plugins.construct_plugin(
                ctx,
                chosen_automagics,
                plugin_class,
                "plugins",
                _noop_progress,
                plugins.__dict__.get("FileHandler", None),
            )

            plugin = constructed

            # Run plugin
            treegrid = plugin.run()

            # Convert treegrid to list of dicts
            result = []
            for row in treegrid.get_renderable().rows:  # type: ignore
                result.append(dict(row))

            return result, 1

        except Exception as e:
            logger.warning("Volatility 3 Python API failed: %s", e)
            logger.info("Falling back to CLI method")
            return self._execute_volatility_plugin_cli(plugin_name, image_path, **kwargs)

    def _execute_volatility_plugin_cli(
        self, plugin_name: str, image_path: str, **kwargs: Any
    ) -> Tuple[Optional[List[Dict[str, Any]]], int]:
        """Execute a Volatility 3 plugin using CLI as fallback."""
        if not self._volatility_available:
            raise RuntimeError("Volatility 3 CLI not available")

        # Adjust timeout based on image size for large images
        image_size_gb = self._get_image_size_gb(image_path)
        timeout_seconds = self._calculate_timeout(image_size_gb)

        logger.info(f"Image size: {image_size_gb:.2f} GB, using timeout: {timeout_seconds}s")

        # Retry loop for transient failures
        attempts = max(1, getattr(config, "volatility_retry_attempts", 1))
        backoff = float(getattr(config, "volatility_retry_backoff_seconds", 0))
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
                    log_event(
                        "plugin_retry",
                        {"plugin": plugin_name, "attempt": attempt, "reason": result.stderr},
                    )
                    # If more attempts remain, retry (sleep only if backoff > 0)
                    if attempt < attempts:
                        if backoff > 0:
                            time.sleep(backoff * (2 ** (attempt - 1)))
                        continue
                    raise RuntimeError(
                        f"Plugin {plugin_name} failed after {attempts} attempts: {result.stderr}"
                    )

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
                    raise RuntimeError(
                        f"Plugin {plugin_name} failed to parse JSON after {attempts} attempts"
                    )

                # Volatility 3 JSON output is usually wrapped in a structure
                # Extract the actual data
                if isinstance(output_data, dict):
                    # Find the data array - it might be under different keys
                    for key, value in output_data.items():
                        if isinstance(value, list) and value and isinstance(value[0], dict):
                            attempts_taken = attempt
                            return value, attempts_taken
                    # If no list found, return empty list
                    attempts_taken = attempt
                    return [], attempts_taken
                elif isinstance(output_data, list):
                    attempts_taken = attempt
                    return output_data, attempts_taken
                else:
                    logger.warning("Unexpected output format from %s", plugin_name)
                    attempts_taken = attempt
                    raise RuntimeError(f"Plugin {plugin_name} returned unexpected output format")

            except subprocess.TimeoutExpired as e:
                logger.error(
                    "Volatility plugin %s timed out (attempt %d/%d)",
                    plugin_name,
                    attempt,
                    attempts,
                )
                log_event(
                    "plugin_retry",
                    {"plugin": plugin_name, "attempt": attempt, "reason": str(e)},
                )
                if attempt < attempts:
                    if backoff > 0:
                        time.sleep(backoff * (2 ** (attempt - 1)))
                    continue
                raise RuntimeError(f"Plugin {plugin_name} timed out after {attempts} attempts")
            except Exception as e:
                logger.error(
                    "Failed to execute Volatility plugin %s (attempt %d/%d): %s",
                    plugin_name,
                    attempt,
                    attempts,
                    e,
                )
                if attempt < attempts:
                    if backoff > 0:
                        time.sleep(backoff * (2 ** (attempt - 1)))
                    continue
                raise RuntimeError(f"Plugin {plugin_name} failed after {attempts} attempts: {e}")

        # This should not be reached, as the loop either succeeds or raises an exception

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

    def execute_plugin(
        self,
        plugin_name: str,
        image_path: str,
        session_id: Optional[str] = None,
        force_reexecute: bool = False,
        **kwargs: Any,
    ) -> ExecutionResult:
        """Execute a single Volatility plugin."""
        start_time = time.time()
        timestamp = start_time

        # Use session_id or default
        cache_session_id = session_id or "default"

        cache_key_params = {"image_path": image_path, **kwargs}

        # Check cache first, unless force_reexecute is True
        if not force_reexecute:
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
                    attempts=0,  # Cached, no attempts
                    used_mock=False,  # Cached results are real, not mock
                )
        else:
            logger.info(f"Force re-executing {plugin_name}, bypassing cache.")

        try:
            log_event("plugin_start", {"plugin": plugin_name, "image": image_path})

            # Execute real Volatility 3 plugin
            output, attempts_taken = self._execute_volatility_plugin(
                plugin_name, image_path, **kwargs
            )

            # Cache the result (store only the output)
            cache.set(cache_session_id, plugin_name, cache_key_params, output)

            success = True
            error = None
            used_mock = False
            log_event(
                "plugin_success", {"plugin": plugin_name, "duration": time.time() - start_time}
            )

        except Exception as e:
            # Fallback to mock data when Volatility fails (ADR-0004)
            logger.warning(f"Volatility execution failed for {plugin_name}, using mock data: {e}")
            output = self._generate_mock_data(plugin_name)
            success = True  # Mock data is considered successful
            error = None
            used_mock = True
            attempts_taken = 0  # Mock doesn't use attempts
            log_event("plugin_mock_fallback", {"plugin": plugin_name, "error": str(e)})

        duration = time.time() - start_time

        # Ensure attempts is set even on exceptions/cached results
        attempts_value = int(locals().get("attempts_taken", 0))

        return ExecutionResult(
            plugin_name=plugin_name,
            success=success,
            output=output,
            error=error,
            duration=duration,
            timestamp=timestamp,
            attempts=attempts_value,
            used_mock=used_mock,
        )

    def execute_workflow(
        self, workflow_spec: Any, image_path: str, force_reexecute: bool = False
    ) -> List[ExecutionResult]:
        """Execute all plugins in a workflow."""
        results: List[ExecutionResult] = []

        # Detect OS to filter compatible plugins
        detected_os = self._detect_os(image_path)
        if detected_os:
            logger.info(f"Detected OS: {detected_os}")
            # Filter plugins to only those compatible with detected OS
            compatible_plugins = [
                plugin
                for plugin in workflow_spec.plugins
                if plugin.name.startswith(f"{detected_os}.")
                or not any(plugin.name.startswith(f"{os}.") for os in ["windows", "linux", "mac"])
            ]
            if len(compatible_plugins) != len(workflow_spec.plugins):
                logger.info(
                    f"Filtered {len(workflow_spec.plugins) - len(compatible_plugins)} "
                    "incompatible plugins"
                )
            workflow_spec.plugins = compatible_plugins
        else:
            logger.warning("Could not detect OS, executing all plugins (may fail)")

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
                result = self.execute_plugin(
                    plugin.name,
                    image_path,
                    force_reexecute=config.force_reexecute_on_fail,
                    **plugin.parameters,
                )
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
                        self.execute_plugin,
                        plugin.name,
                        image_path,
                        force_reexecute=config.force_reexecute_on_fail,
                        **plugin.parameters,
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

    def _detect_os(self, image_path: str) -> Optional[str]:
        """Detect the OS of the memory image."""
        if not VOLATILITY_AVAILABLE:
            return None

        os_plugins = {"windows": "windows.info", "linux": "linux.info", "mac": "mac.info"}

        for os_name, plugin in os_plugins.items():
            try:
                # Try to run the info plugin
                ctx = contexts.Context()
                ctx.config["automagic.LayerStacker.single_location"] = f"file://{image_path}"

                automagic_classes = automagic.available(ctx)
                chosen_automagics = automagic.choose_automagic(automagic_classes, plugin)

                for amagic in chosen_automagics:
                    if amagic.__class__.__name__ == "LayerStacker":
                        ctx.config["automagic.LayerStacker.single_location"] = (
                            f"file://{image_path}"
                        )
                    amagic(ctx, config_path=config.config_file)

                # Try to construct the plugin
                plugins.construct_plugin(ctx, plugin)
                # If no exception, OS detected
                return os_name
            except Exception:
                continue

        return None

    def _generate_mock_data(self, plugin_name: str) -> List[Dict[str, Any]]:
        """Generate deterministic mock data for testing when Volatility is unavailable."""
        if "pslist" in plugin_name:
            return [
                {
                    "PID": 4,
                    "PPID": 0,
                    "ImageFileName": "System",
                    "Offset(V)": "0x12345678",
                    "Threads": 8,
                    "Handles": 100,
                    "SessionId": 0,
                    "Wow64": False,
                    "CreateTime": "2023-01-01T00:00:00.000000+00:00",
                    "ExitTime": None,
                },
                {
                    "PID": 1234,
                    "PPID": 4,
                    "ImageFileName": "smss.exe",
                    "Offset(V)": "0x87654321",
                    "Threads": 2,
                    "Handles": 50,
                    "SessionId": 0,
                    "Wow64": False,
                    "CreateTime": "2023-01-01T00:00:01.000000+00:00",
                    "ExitTime": None,
                },
            ]
        elif "netscan" in plugin_name:
            return [
                {
                    "Offset(V)": "0xabcdef12",
                    "PID": 1234,
                    "Size": 123,
                    "Proto": "TCPv4",
                    "LocalAddr": "192.168.1.100",
                    "LocalPort": 443,
                    "ForeignAddr": "10.0.0.1",
                    "ForeignPort": 80,
                    "State": "ESTABLISHED",
                    "Created": "2020-12-31T16:30:00.000000+00:00",  # String instead of int
                    "Owner": "chrome.exe",
                }
            ]
        elif "malfind" in plugin_name:
            return [
                {
                    "PID": 5678,
                    "Process": "suspicious.exe",
                    "Start VPN": "0x400000",
                    "End VPN": "0x500000",
                    "Tag": "VadS",
                    "Protection": "PAGE_EXECUTE_READWRITE",
                    "CommitCharge": 1,
                    "PrivateMemory": 4096,
                    "FileOffset": 0,
                    "FileName": None,
                }
            ]
        elif "hashdump" in plugin_name:
            return [
                {
                    "Username": "Administrator",
                    "UID": 500,
                    "GID": 500,
                    "Hash": "aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0",
                    "Type": "NTLM",
                },
                {
                    "Username": "user1",
                    "UID": 1000,
                    "GID": 1000,
                    "Hash": "e19ccf75ee54e06b06a5907af13cef42:31d6cfe0d16ae931b73c59d7e0c089c0",
                    "Type": "NTLM",
                },
            ]
        elif "lsadump" in plugin_name or "cachedump" in plugin_name:
            return [
                {
                    "Username": "Administrator",
                    "UID": 500,
                    "GID": 500,
                    "HomeDir": "/home/admin",
                    "Shell": "/bin/bash",
                    "Description": "Administrator account",
                },
                {
                    "Username": "user1",
                    "UID": 1000,
                    "GID": 1000,
                    "HomeDir": "/home/user1",
                    "Shell": "/bin/bash",
                    "Description": "Regular user",
                },
            ]
        elif "getsids" in plugin_name:
            return [
                {
                    "Name": "Administrator",
                    "SID": "S-1-5-21-1367486129-1636748403-2738611465-500",
                    "PID": 2496,
                    "Process": "explorer.exe",
                },
                {
                    "Name": "Domain Users",
                    "SID": "S-1-5-21-1367486129-1636748403-2738611465-513",
                    "PID": 2496,
                    "Process": "explorer.exe",
                },
                {
                    "Name": "Administrators",
                    "SID": "S-1-5-32-544",
                    "PID": 2496,
                    "Process": "explorer.exe",
                },
            ]
        else:
            # Generic mock data for unknown plugins - return empty list
            return []
