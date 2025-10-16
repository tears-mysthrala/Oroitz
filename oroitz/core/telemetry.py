"""Telemetry and logging for Oroitz."""

import logging
from typing import Any, Dict

from rich.logging import RichHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[RichHandler()],
)

logger = logging.getLogger("oroitz")


def log_event(event: str, data: Dict[str, Any]) -> None:
    """Log a structured event."""
    logger.info(f"Event: {event}", extra=data)


def setup_logging(level: str = "INFO") -> None:
    """Setup logging configuration."""
    logger.setLevel(getattr(logging, level.upper()))