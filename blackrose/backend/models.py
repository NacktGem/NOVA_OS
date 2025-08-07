"""
Database models for the Black Rose backend.

Defines ORM models for theme purchases, DMCA reports, and consent logs.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from .database import Base


class ThemePurchase(Base):
    __tablename__ = "theme_purchases"

    id = Column(Integer, primary_key=True, index=True)
    theme = Column(String, nullable=False)
    user_id = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)


class DMCAReport(Base):
    __tablename__ = "dmca_reports"

    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String, nullable=False)
    user_id = Column(String, nullable=False)
    violation = Column(Boolean, default=False, nullable=False)
    method = Column(String, nullable=True)
    details = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    hash = Column(String, nullable=True)


class ConsentLog(Base):
    __tablename__ = "consent_logs"

    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String, nullable=False)
    model_id = Column(String, nullable=False)
    valid = Column(Boolean, default=False, nullable=False)
    reason = Column(String, nullable=True)
    hash = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)