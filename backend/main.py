"""
FastAPI application for the NovaOS backend.

This application exposes health checks and log management endpoints.
System logs can be created and retrieved via the `/logs` endpoint. The
database is initialised at startup. Additional endpoints can be added
to manage other NovaOS services and subsystems.
"""

from datetime import datetime
from fastapi import FastAPI, Depends
from pydantic import BaseModel

from .database import SessionLocal, init_db
from .models import SystemLog


app = FastAPI(title="NovaOS API")


@app.on_event("startup")
def on_startup() -> None:
    """Initialise database tables when the app starts."""
    init_db()


def get_db():
    """Provide a session to the database for dependency injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class LogEntry(BaseModel):
    """Pydantic model representing a new log entry."""

    event: str
    level: str = "INFO"
    details: str | None = None


@app.get("/")
def read_root() -> dict[str, str]:
    """Root endpoint providing a simple message."""
    return {"message": "NovaOS API"}


@app.get("/health")
def health() -> dict[str, str]:
    """Health check endpoint to verify the service is running."""
    return {"status": "ok"}


@app.post("/logs")
def create_log(entry: LogEntry, db=Depends(get_db)) -> dict[str, int]:
    """
    Create a system log entry.

    Args:
        entry: The log entry data.
        db: Injected SQLAlchemy session.

    Returns:
        A dictionary containing the created log's ID.
    """
    log = SystemLog(
        event=entry.event,
        level=entry.level,
        timestamp=datetime.utcnow(),
        details=entry.details,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return {"id": log.id}


@app.get("/logs")
def list_logs(limit: int = 100, db=Depends(get_db)) -> list[SystemLog]:
    """
    Retrieve recent system logs.

    Args:
        limit: Maximum number of logs to return.
        db: Injected SQLAlchemy session.

    Returns:
        A list of log entries ordered by most recent first.
    """
    return (
        db.query(SystemLog)
        .order_by(SystemLog.timestamp.desc())
        .limit(limit)
        .all()
    )