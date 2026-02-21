"""
Shared test fixtures for beat-books-data.

Provides:
- db_session: In-memory SQLite session with all tables created
"""

import os

# Set DATABASE_URL before any src imports so Settings() validation doesn't
# fail during test collection in CI (where no .env file exists).
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from src.entities.base import Base


@pytest.fixture
def db_session():
    """In-memory SQLite for unit tests. Never hits production DB."""
    engine = create_engine("sqlite:///:memory:")

    # Enable foreign key support for SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    # Create all tables from ORM models
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    engine.dispose()
