"""Telemetry and logging for Oroitz."""

import logging
import sys
from typing import Any, Dict

# Configure simple logging to avoid Rich import issues
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(name)s - %(message)s",
    stream=sys.stdout,
)

logger = logging.getLogger("oroitz")


def log_event(event: str, data: Dict[str, Any]) -> None:
    """Log a structured event."""
    logger.info(f"Event: {event}", extra=data)


def setup_logging(level: str = "INFO") -> None:
    """Setup logging configuration."""
    logger.setLevel(getattr(logging, level.upper()))
