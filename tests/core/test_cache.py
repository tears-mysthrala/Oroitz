"""Tests for cache module."""

import tempfile
from pathlib import Path

from oroitz.core.cache import Cache


def test_cache_creation():
    """Test cache creation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache_dir = Path(tmpdir) / "cache"
        cache = Cache(cache_dir)
        assert cache.cache_dir == cache_dir
        assert cache.cache_dir.exists()


def test_cache_operations():
    """Test cache set/get operations."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = Cache(Path(tmpdir))

        # Test cache miss
        result = cache.get("session1", "windows.pslist", {})
        assert result is None

        # Test cache set
        test_data = {"pid": 123, "name": "test.exe"}
        cache.set("session1", "windows.pslist", {}, test_data)

        # Test cache hit
        result = cache.get("session1", "windows.pslist", {})
        assert result == test_data

        # Test different parameters don't match
        result = cache.get("session1", "windows.pslist", {"param": "value"})
        assert result is None


def test_cache_clear():
    """Test cache clearing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = Cache(Path(tmpdir))

        # Add some data
        cache.set("session1", "plugin1", {}, "data1")
        cache.set("session1", "plugin2", {}, "data2")

        # Verify data exists
        assert cache.get("session1", "plugin1", {}) == "data1"
        assert cache.get("session1", "plugin2", {}) == "data2"

        # Clear cache
        cache.clear()

        # Verify data is gone
        assert cache.get("session1", "plugin1", {}) is None
        assert cache.get("session1", "plugin2", {}) is None


def test_cache_stats():
    """Test cache statistics."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = Cache(Path(tmpdir))

        # Empty cache
        stats = cache.get_stats()
        assert stats["total_entries"] == 0
        assert stats["cache_size_mb"] >= 0

        # Add data
        cache.set("session1", "plugin1", {}, "some data")
        cache.set("session1", "plugin2", {}, "more data")

        stats = cache.get_stats()
        assert stats["total_entries"] == 2
        assert stats["cache_size_mb"] > 0