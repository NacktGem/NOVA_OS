"""
SQLAlchemy models for NovaOS backend.

Defines a SystemLog model to store system and agent logs. Each log entry
records an event name, severity level, timestamp, and optional details.
Additional models can be added here as NovaOS functionality grows.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text

from .database import Base


class SystemLog(Base):
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, index=True)
    event = Column(String, nullable=False)
    level = Column(String, nullable=False, default="INFO")
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    details = Column(Text, nullable=True)