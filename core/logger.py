"""
System logging utilities.

Provides simple wrappers around Python's logging library to record events
from different subsystems of the Nova OS.
"""

import logging

logger = logging.getLogger("NovaOS")


def log_event(event: str) -> None:
    """Log an event message."""
    logger.info(event)


def log_system_event(message: str) -> None:
    """Log a system‑level message."""
    logger.info(message)