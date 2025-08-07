"""
Database configuration for NovaOS backend.

Defines the SQLAlchemy engine, session, and base class. The database URL
defaults to a local SQLite file but can be overridden by setting the
`NOVA_DATABASE_URL` environment variable. Use `init_db()` to create
tables on startup.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


DATABASE_URL = os.getenv("NOVA_DATABASE_URL", "sqlite:///./novaos.db")

# Determine connection args for SQLite only. When using SQLite with SQLAlchemy
# in a multi-threaded application (FastAPI), we must disable check_same_thread.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# Create SQLAlchemy engine and session factory
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative models
Base = declarative_base()


def init_db() -> None:
    """Create all tables for models that inherit from Base."""
    # Import models here so that they register with the Base before
    # create_all is invoked. Otherwise, no tables will be created.
    from . import models  # noqa: F401
    Base.metadata.create_all(bind=engine)