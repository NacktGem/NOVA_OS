"""
ORM models for GypsyCove.

At present, GypsyCove manages a catalogue of courses that users can enrol in.
Each course has a title, a description, an optional URL pointing to the
course content (such as a video or markdown file), and an optional
category grouping.  Additional fields such as authors, difficulty levels
and durations can be introduced later as the platform evolves.
"""

from sqlalchemy import Column, Integer, String, Text
from .database import Base


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    content_url = Column(String, nullable=True)
    category = Column(String, nullable=True)