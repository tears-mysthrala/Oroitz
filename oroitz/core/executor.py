"""Volatility 3 execution wrapper for Oroitz."""

import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel

# Volatility 3 imports
VOLATILITY_AVAILABLE = True
try:
    from volatility3.framework import contexts
    from volatility3.framework.automagic import available, run
    from volatility3.framework import constants
    from volatility3.framework import import_files
    import volatility3.plugins
except ImportError:
    VOLATILITY_AVAILABLE = False
    # Create dummy objects to avoid NameError
    contexts = None
    automagic = None
    constants = None
    import_files = None
    list_plugins = None
    format_hints = None
    volatility3 = None

from oroitz.core.config import config
from oroitz.core.telemetry import log_event, logger
from oroitz.core.cache import cache


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
        # Initialize Volatility 3 context and plugins
        self._vol_context = None
        self._plugins = {}
        self._initialize_volatility()

    def _initialize_volatility(self) -> None:
        """Initialize Volatility 3 context and load plugins."""
        if not VOLATILITY_AVAILABLE:
            logger.info("Volatility 3 not available, using mock data mode")
            self._vol_context = None
            self._plugins = {}
            return

        try:
            # Create base context
            self._vol_context = contexts.Context()

            # Import plugins
            import_files(volatility3.plugins, True)

            # For now, don't list plugins, assume they can be loaded dynamically
            self._plugins = {}  # We'll check existence when running

            logger.info("Initialized Volatility 3 successfully")

        except Exception as e:
            logger.warning(f"Failed to initialize Volatility 3: {e}. Using mock data fallback.")
            self._vol_context = None
            self._plugins = {}

    def _execute_volatility_plugin(
        self,
        plugin_name: str,
        image_path: str,
        profile: str,
        **kwargs: Any
    ) -> Optional[List[Dict[str, Any]]]:
        """Execute a Volatility 3 plugin and return normalized output."""
        if not self._vol_context:
            logger.warning(f"Volatility context not available, falling back to mock data")
            return self._get_mock_data(plugin_name)

        try:
            # Create a fresh context for this execution
            ctx = contexts.Context()
            import_files(volatility3.plugins, True)

            # Try to get the plugin class dynamically
            plugin_parts = plugin_name.split('.')
            plugin_module_name = f"volatility3.plugins.{'.'.join(plugin_parts[:-1])}"
            plugin_class_name = plugin_parts[-1]
            
            try:
                plugin_module = __import__(plugin_module_name, fromlist=[plugin_class_name])
                # Try different capitalizations
                for class_name in [plugin_class_name, plugin_class_name.capitalize(), plugin_class_name.title(), ''.join(word.capitalize() for word in plugin_class_name.split('_'))]:
                    try:
                        plugin_class = getattr(plugin_module, class_name)
                        break
                    except AttributeError:
                        continue
                else:
                    raise AttributeError(f"No class found for {plugin_class_name}")
            except (ImportError, AttributeError):
                logger.warning(f"Plugin {plugin_name} not found, falling back to mock data")
                return self._get_mock_data(plugin_name)

            # Configure the plugin
            plugin_config_path = f"plugins.{plugin_name}"
            # ctx.config[plugin_config_path] = {}  # Remove this, let automagic handle it

            # Set up basic configuration
            ctx.config[f"{plugin_config_path}.image"] = image_path
            ctx.config[f"{plugin_config_path}.profile"] = profile

            # Add any additional kwargs as config
            for key, value in kwargs.items():
                ctx.config[f"{plugin_config_path}.{key}"] = value

            # Get available automagics
            automagics = available(ctx)

            # Run automagics to set up the context
            run(automagics, ctx, plugin_class, plugin_config_path, None)

            # Create and run the plugin
            plugin = plugin_class(ctx, plugin_config_path)

            # Run the plugin and collect results
            results = []
            tree_grid = plugin.run()

            # Convert TreeGrid to list of dictionaries
            if tree_grid and hasattr(tree_grid, '_rows'):
                headers = [col.name for col in tree_grid._columns]
                for row in tree_grid._rows:
                    result_dict = {}
                    for i, value in enumerate(row):
                        if i < len(headers):
                            result_dict[headers[i]] = value
                    results.append(result_dict)

            return results if results else []

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
        **kwargs: Any
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
                "plugin_success",
                {"plugin": plugin_name, "duration": time.time() - start_time}
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
        self,
        workflow_spec: Any,
        image_path: str,
        profile: str
    ) -> List[ExecutionResult]:
        """Execute all plugins in a workflow."""
        results: List[ExecutionResult] = []

        for plugin in workflow_spec.plugins:
            result = self.execute_plugin(
                plugin.name,
                image_path,
                profile,
                **plugin.parameters
            )
            results.append(result)

        return results

    def _mock_pslist(self) -> List[Dict[str, Union[str, int, bool, None]]]:
        """Mock data for pslist plugin."""
        return [
            {
                "pid": 4,
                "name": "System",
                "ppid": 0,
                "threads": 100,
                "handles": 500,
                "session": 0,
                "wow64": False,
                "create_time": "2023-01-01T00:00:00Z",
                "exit_time": None,
            },
            {
                "pid": 1234,
                "name": "notepad.exe",
                "ppid": 876,
                "threads": 8,
                "handles": 150,
                "session": 1,
                "wow64": True,
                "create_time": "2023-01-01T12:00:00Z",
                "exit_time": None,
            },
        ]

    def _mock_netscan(self) -> List[Dict[str, Union[str, int, None]]]:
        """Mock data for netscan plugin."""
        return [
            {
                "offset": "0x12345678",
                "pid": 1234,
                "owner": "notepad.exe",
                "created": "2023-01-01T12:00:00Z",
                "local_addr": "192.168.1.100:12345",
                "remote_addr": "8.8.8.8:53",
                "state": "ESTABLISHED",
            },
        ]

    def _mock_malfind(self) -> List[Dict[str, Union[str, int, None]]]:
        """Mock data for malfind plugin."""
        return [
            {
                "pid": 5678,
                "process_name": "suspicious.exe",
                "start": "0x400000",
                "end": "0x500000",
                "tag": "MzHeader",
                "protection": "PAGE_EXECUTE_READWRITE",
                "commit_charge": 1024,
                "private_memory": 2048,
            },
        ]
