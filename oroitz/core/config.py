"""Configuration management for Oroitz core engine."""

from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Application configuration with defaults and overrides."""

    # Core paths
    config_file: Optional[Path] = None
    cache_dir: Path = Path.home() / ".oroitz" / "cache"
    sessions_dir: Path = Path.home() / ".oroitz" / "sessions"
    log_level: str = "INFO"
    max_concurrency: int = 4

    # Volatility settings
    volatility_path: Optional[Path] = None
    symbols_path: Optional[Path] = None
    # Execution retry settings (Phase 6 hardening)
    volatility_retry_attempts: int = 2
    volatility_retry_backoff_seconds: float = 1.0

    # GUI settings
    telemetry_enabled: bool = False
    cache_enabled: bool = True
    force_reexecute_on_fail: bool = False
    auto_export: bool = False
    theme: str = "system"
    font_size: int = 10

    model_config = SettingsConfigDict(
        env_prefix="OROITZ_",
        env_file=".env",
        extra="ignore",
    )

    @classmethod
    def from_file(cls, file_path: Path) -> "Config":
        """Load configuration from a TOML file."""
        # For now, basic; later add TOML support
        return cls(config_file=file_path)


# Global config instance
config = Config()
