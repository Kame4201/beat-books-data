"""
Shared test fixtures for beat-books-data.

Provides:
- db_session: In-memory SQLite session with all tables created
"""

import os

# Force sqlite for tests so we never accidentally hit a real database.
# Must be set before any src imports (Settings() validates at import time).
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

# Strip unknown env vars that may exist in .env but aren't in Settings.
for _key in list(os.environ):
    if _key.startswith("SCRAPE_BACKEND"):
        del os.environ[_key]

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
