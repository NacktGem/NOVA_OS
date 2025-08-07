"""
Database setup for the Black Rose backend.

This module configures SQLAlchemy for use with FastAPI. It defines a
Base class for model definitions, creates an engine based on the
DATABASE_URL environment variable (defaulting to a local SQLite
database), and exposes a SessionLocal factory for obtaining database
sessions.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./database.db")

# Create the SQLAlchemy engine. Use connect_args for SQLite to enable
# multi-threaded use inside FastAPI.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()


def init_db() -> None:
    """Create database tables if they do not exist."""
    import logging
    from . import models  # noqa: F401 – import models to register with Base
    logging.info("Creating database tables if absent...")
    Base.metadata.create_all(bind=engine)