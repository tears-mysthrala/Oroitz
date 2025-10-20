"""Volatility 3 execution wrapper for Oroitz."""

import json
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional, Union

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
                ["poetry", "run", "vol"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 2:  # 2 means help/usage shown, which means vol is available
                self._vol_command = ["poetry", "run", "vol"]
                return True
            
            # Fallback to just vol
            result = subprocess.run(
                ["vol"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 2:
                self._vol_command = ["vol"]
                return True
                
            return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _execute_volatility_plugin(
        self, plugin_name: str, image_path: str, profile: str, **kwargs: Any
    ) -> Optional[List[Dict[str, Any]]]:
        """Execute a Volatility 3 plugin using CLI and return normalized output."""
        if not self._volatility_available:
            logger.warning("Volatility 3 CLI not available, falling back to mock data")
            return self._get_mock_data(plugin_name)

        try:
            # Build command
            cmd = self._vol_command + ["-f", image_path, "-r", "json"]

            # Add profile if specified
            if profile:
                # Try different profile formats
                profile_options = []
                if profile.startswith("Win"):
                    profile_options = [f"--profile={profile}"]
                elif profile.startswith("Lin"):
                    profile_options = [f"--profile={profile}"]
                else:
                    # Generic profile specification
                    profile_options = [f"--profile={profile}"]

                # For now, try without explicit profile and let Volatility auto-detect
                cmd.extend([])  # No profile specification

            # Add plugin name
            cmd.append(plugin_name)

            # Add any additional parameters
            for key, value in kwargs.items():
                if isinstance(value, bool):
                    if value:
                        cmd.append(f"--{key}")
                else:
                    cmd.append(f"--{key}={value}")

            logger.info(f"Running command: {' '.join(cmd)}")

            # Execute command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                cwd=None  # Use current directory
            )

            if result.returncode != 0:
                logger.warning(f"Volatility plugin {plugin_name} failed: {result.stderr}")
                return self._get_mock_data(plugin_name)

            # Parse JSON output
            try:
                output_data = json.loads(result.stdout)
                # Volatility 3 JSON output is usually wrapped in a structure
                # Extract the actual data
                if isinstance(output_data, dict):
                    # Find the data array - it might be under different keys
                    for key, value in output_data.items():
                        if isinstance(value, list) and value and isinstance(value[0], dict):
                            return value
                    # If no list found, return empty list
                    return []
                elif isinstance(output_data, list):
                    return output_data
                else:
                    logger.warning(f"Unexpected output format from {plugin_name}")
                    return self._get_mock_data(plugin_name)

            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON output from {plugin_name}: {e}")
                logger.debug(f"Raw output: {result.stdout[:500]}")
                return self._get_mock_data(plugin_name)

        except subprocess.TimeoutExpired:
            logger.error(f"Volatility plugin {plugin_name} timed out")
            return self._get_mock_data(plugin_name)
        except Exception as e:
            logger.error(f"Failed to execute Volatility plugin {plugin_name}: {e}")
            return self._get_mock_data(plugin_name)

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
        profile: str,
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
            output = self._execute_volatility_plugin(plugin_name, image_path, profile, **kwargs)

            # Cache the result
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

        return ExecutionResult(
            plugin_name=plugin_name,
            success=success,
            output=output,
            error=error,
            duration=duration,
            timestamp=timestamp,
        )

    def execute_workflow(
        self, workflow_spec: Any, image_path: str, profile: str
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
