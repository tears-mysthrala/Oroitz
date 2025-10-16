"""Configuration management for Oroitz core engine."""

from pathlib import Path
from typing import Optional

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Application configuration with defaults and overrides."""

    # Core paths
    config_file: Optional[Path] = None
    cache_dir: Path = Path.home() / ".oroitz" / "cache"
    log_level: str = "INFO"
    max_concurrency: int = 4

    # Volatility settings
    volatility_path: Optional[Path] = None
    symbols_path: Optional[Path] = None

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