"""
Minimal API for GypsyCove Academy.

This FastAPI application provides a health check and a sample endpoint
to list available courses. Replace these stubs with real course logic
and authentication as you expand the platform.
"""

from fastapi import FastAPI

app = FastAPI(title="GypsyCove API")


@app.get("/health")
def health():
    """Return API health status."""
    return {"status": "ok"}


@app.get("/courses")
def list_courses():
    """Return a sample list of courses."""
    return [
        {"id": 1, "title": "Introduction to AI", "description": "Learn the basics of artificial intelligence."},
        {"id": 2, "title": "Secure Coding", "description": "Best practices for building secure applications."},
    ]