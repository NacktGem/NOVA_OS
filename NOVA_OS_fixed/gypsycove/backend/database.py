"""
Database configuration for the GypsyCove backend.

This module defines the SQLAlchemy engine, session and base classes used by
GypsyCove.  The default database is a SQLite file located in the working
directory, but can be overridden by setting the `GYPSYCOVE_DATABASE_URL`
environment variable.  To initialise the database tables, call
``init_db()`` at application startup.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("GYPSYCOVE_DATABASE_URL", "sqlite:///./gypsycove.db")

# When using SQLite, ``check_same_thread`` must be disabled for multithreaded
# FastAPI applications.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def init_db() -> None:
    """Create all tables for the models defined in :mod:`gypsycove.backend.models`."""
    # Import models here so that they are registered properly before
    # ``create_all`` is called.  Otherwise no tables will be generated.
    from . import models  # noqa: F401

    Base.metadata.create_all(bind=engine)