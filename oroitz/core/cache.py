"""Caching layer for Oroitz."""

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Optional, Union

from oroitz.core.config import config
from oroitz.core.telemetry import logger


class Cache:
    """Filesystem-based cache for plugin results."""

    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or config.cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_key(self, session_id: str, plugin_name: str, parameters: Dict[str, Any]) -> str:
        """Generate cache key from session, plugin, and parameters."""
        key_data: Dict[str, Any] = {
            "session_id": session_id,
            "plugin_name": plugin_name,
            "parameters": parameters,
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_str.encode()).hexdigest()

    def get(self, session_id: str, plugin_name: str, parameters: Dict[str, Any]) -> Optional[Any]:
        """Get cached result if exists."""
        cache_key = self._get_cache_key(session_id, plugin_name, parameters)
        cache_file = self.cache_dir / f"{cache_key}.json"

        if cache_file.exists():
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    result: Any = json.load(f)
                logger.debug(f"Cache hit for {plugin_name}")
                return result
            except Exception as e:
                logger.warning(f"Failed to load cache for {plugin_name}: {e}")
                # Remove corrupted cache file
                cache_file.unlink(missing_ok=True)

        logger.debug(f"Cache miss for {plugin_name}")
        return None

    def set(
        self, session_id: str, plugin_name: str, parameters: Dict[str, Any], result: Any
    ) -> None:
        """Cache a result."""
        cache_key = self._get_cache_key(session_id, plugin_name, parameters)
        cache_file = self.cache_dir / f"{cache_key}.json"

        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2)
            logger.debug(f"Cached result for {plugin_name}")
        except Exception as e:
            logger.warning(f"Failed to cache result for {plugin_name}: {e}")

    def clear(self) -> None:
        """Clear all cached results."""
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
        logger.info("Cache cleared")

    def get_stats(self) -> Dict[str, Union[int, float]]:
        """Get cache statistics."""
        cache_files = list(self.cache_dir.glob("*.json"))
        total_size = sum(f.stat().st_size for f in cache_files) if cache_files else 0
        return {
            "total_entries": len(cache_files),
            "cache_size_mb": total_size / (1024 * 1024),
        }


# Global cache instance
cache = Cache()
