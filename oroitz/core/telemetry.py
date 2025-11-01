"""Telemetry and logging for Oroitz."""

import json
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
    """Log a structured event as JSON for easier parsing."""
    try:
        payload = {"event": event, **(data or {})}
        logger.info(json.dumps(payload, ensure_ascii=False))
    except Exception:
        # Fallback to plain message on any serialization error
        logger.info(f"Event: {event}")


def setup_logging(level: str = "INFO") -> None:
    """Setup logging configuration."""
    logger.setLevel(getattr(logging, level.upper()))
