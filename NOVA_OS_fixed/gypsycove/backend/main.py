"""
GypsyCove API.

This FastAPI application exposes endpoints for managing and retrieving
educational courses.  It demonstrates a simple CRUD interface built on
top of SQLAlchemy.  Authentication and permissions are not yet
implemented; future revisions could integrate with an identity provider.
"""

from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel

from .database import SessionLocal, init_db
from .models import Course


app = FastAPI(title="GypsyCove API")


@app.on_event("startup")
def on_startup() -> None:
    """Initialise the database when the application starts."""
    init_db()


def get_db():
    """Provide a transactional scope for database operations."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class CourseCreate(BaseModel):
    """Schema for creating a new course."""
    title: str
    description: Optional[str] = None
    content_url: Optional[str] = None
    category: Optional[str] = None


class CourseOut(CourseCreate):
    """Schema for returning course data to clients."""
    id: int

    class Config:
        orm_mode = True


@app.get("/health")
def health() -> dict[str, str]:
    """Return API health status."""
    return {"status": "ok"}


@app.get("/courses", response_model=List[CourseOut])
def list_courses(db=Depends(get_db)) -> List[CourseOut]:
    """Return all courses in the database."""
    return db.query(Course).all()


@app.get("/courses/{course_id}", response_model=CourseOut)
def get_course(course_id: int, db=Depends(get_db)) -> CourseOut:
    """Retrieve a single course by its ID."""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@app.post("/courses", response_model=CourseOut, status_code=201)
def create_course(course: CourseCreate, db=Depends(get_db)) -> CourseOut:
    """Create a new course."""
    db_course = Course(**course.model_dump())
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course


@app.delete("/courses/{course_id}", status_code=204)
def delete_course(course_id: int, db=Depends(get_db)) -> None:
    """Delete a course by its ID."""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    db.delete(course)
    db.commit()
    return None