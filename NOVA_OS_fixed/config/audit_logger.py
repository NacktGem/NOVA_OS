"""
Audit logging utilities.

This module provides a simple wrapper around Python's logging library to record
audit events. In a real implementation, events should be written to a
tamper‑evident log or secure database.
"""

import logging

logger = logging.getLogger("audit")


def log_event(event: str, data: dict) -> None:
    """Log an audit event with associated data."""
    logger.info(f"{event}: {data}")