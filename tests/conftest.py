"""
Shared test fixtures for beat-books-data.

Provides:
- db_session: In-memory SQLite session with all tables created
- client: FastAPI TestClient with DB dependency override
"""

import os

# Force sqlite for tests — must be set before any src imports.
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import pytest
from decimal import Decimal
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from src.entities.base import Base
from src.entities.team_offense import TeamOffense
from src.entities.passing_stats import PassingStats

# Import ALL entity modules so Base.metadata.create_all() registers them.
import src.entities.team_offense  # noqa: F401
import src.entities.team_defense  # noqa: F401
import src.entities.standings  # noqa: F401
import src.entities.games  # noqa: F401
import src.entities.team_game  # noqa: F401
import src.entities.passing_stats  # noqa: F401
import src.entities.rushing_stats  # noqa: F401
import src.entities.receiving_stats  # noqa: F401
import src.entities.defense_stats  # noqa: F401
import src.entities.kicking_stats  # noqa: F401
import src.entities.punting_stats  # noqa: F401
import src.entities.return_stats  # noqa: F401
import src.entities.scoring_stats  # noqa: F401
import src.entities.kicking  # noqa: F401
import src.entities.punting  # noqa: F401
import src.entities.returns  # noqa: F401


@pytest.fixture
def db_session():
    """In-memory SQLite for unit tests. Never hits production DB."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)

    TestSession = sessionmaker(bind=engine)
    session = TestSession()
    yield session
    session.close()
    engine.dispose()


@pytest.fixture
def client(db_session: Session):
    """FastAPI TestClient with DB dependency overridden to use in-memory SQLite."""
    from fastapi.testclient import TestClient
    from src.core.database import get_db
    from src.main import app

    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app, raise_server_exceptions=False) as tc:
        yield tc
    app.dependency_overrides.clear()
