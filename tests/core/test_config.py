"""Tests for config module."""

import os
from pathlib import Path

from oroitz.core.config import Config


def test_config_defaults():
    """Test default configuration values."""
    config = Config()
    assert config.cache_dir == Path.home() / ".oroitz" / "cache"
    assert config.log_level == "INFO"
    assert config.max_concurrency == 4


def test_config_env_vars():
    """Test configuration from environment variables."""
    os.environ["OROITZ_LOG_LEVEL"] = "DEBUG"
    os.environ["OROITZ_MAX_CONCURRENCY"] = "8"
    config = Config()
    assert config.log_level == "DEBUG"
    assert config.max_concurrency == 8
    # Clean up
    del os.environ["OROITZ_LOG_LEVEL"]
    del os.environ["OROITZ_MAX_CONCURRENCY"]