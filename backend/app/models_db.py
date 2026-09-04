"""
SQLAlchemy ORM models for the Personal-use login + saved-history feature.

Open-use requests never touch these tables at all (see routes.py — history
is only written when a valid auth token is attached to the request).
"""
import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone_or_email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    history_entries = relationship(
        "HistoryEntry", back_populates="user", cascade="all, delete-orphan"
    )


class HistoryEntry(Base):
    """
    One saved advisory run for a logged-in (personal-use) user.

    `business_name` is a free-text label the user gives their mock/real
    business plan so that multiple check-ins on the *same* venture (e.g. the
    "1 hour in -> 3 hours later -> 5 hours later" demo walkthrough) can be
    grouped and shown as a timeline rather than a flat list of unrelated runs.
    """
    __tablename__ = "history_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    business_name = Column(String, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Stored as JSON text: the full AdvisoryRequest + AdvisoryResponse payload,
    # so a saved report can be re-rendered exactly as it was generated.
    request_json = Column(Text, nullable=False)
    response_json = Column(Text, nullable=False)

    user = relationship("User", back_populates="history_entries")
