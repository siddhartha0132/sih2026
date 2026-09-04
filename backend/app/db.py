"""
Database setup — SQLite for the hackathon demo.

Why SQLite: zero external services to stand up before Thursday's demo, but it's
a real relational DB with real persistence (a file on disk), not an in-memory
mock. Swapping to Postgres later is a one-line change to DATABASE_URL.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "gramvyapaar.db")
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{DB_PATH}")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    # Import models here so they're registered on Base before create_all runs.
    from app import models_db  # noqa: F401
    Base.metadata.create_all(bind=engine)
