"""Regression tests for GET /api/v1/games/{season} endpoint."""

from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from src.core.database import get_db
from src.entities.base import Base
from src.entities.games import Games
from src.main import app


@pytest.fixture()
def db_session():
    """Create a test database session with games table."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture()
def client(db_session):
    """Create a test client with DB session override."""

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture()
def seed_games(db_session):
    """Seed test games data."""
    games = [
        Games(
            season=2024,
            week=1,
            game_day="Sun",
            game_date=date(2024, 9, 8),
            winner="Kansas City Chiefs",
            loser="Baltimore Ravens",
            pts_w=27,
            pts_l=20,
        ),
        Games(
            season=2024,
            week=1,
            game_day="Sun",
            game_date=date(2024, 9, 8),
            winner="Philadelphia Eagles",
            loser="Green Bay Packers",
            pts_w=34,
            pts_l=29,
        ),
        Games(
            season=2024,
            week=2,
            game_day="Sun",
            game_date=date(2024, 9, 15),
            winner="Buffalo Bills",
            loser="Miami Dolphins",
            pts_w=31,
            pts_l=10,
        ),
    ]
    db_session.add_all(games)
    db_session.commit()
    return games


class TestGamesEndpoint:
    """Tests for /api/v1/games/{season}."""

    def test_games_returns_200(self, client, seed_games):
        """GET /api/v1/games/2024 returns 200 with data."""
        resp = client.get("/api/v1/games/2024")
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] == 3
        assert len(body["data"]) == 3

    def test_games_empty_season(self, client, seed_games):
        """GET /api/v1/games/1999 returns 200 with empty data."""
        resp = client.get("/api/v1/games/1999")
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] == 0
        assert body["data"] == []

    def test_games_week_filter(self, client, seed_games):
        """GET /api/v1/games/2024?week=1 filters by week."""
        resp = client.get("/api/v1/games/2024?week=1")
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] == 2
        assert body["week"] == 1

    def test_games_pagination(self, client, seed_games):
        """GET /api/v1/games/2024?limit=1&offset=1 paginates."""
        resp = client.get("/api/v1/games/2024?limit=1&offset=1")
        assert resp.status_code == 200
        body = resp.json()
        assert len(body["data"]) == 1
        assert body["total"] == 3
        assert body["offset"] == 1
        assert body["limit"] == 1

    def test_games_sort_order(self, client, seed_games):
        """GET /api/v1/games/2024?sort_by=week&order=desc returns desc."""
        resp = client.get("/api/v1/games/2024?sort_by=week&order=desc")
        assert resp.status_code == 200
        body = resp.json()
        weeks = [g["week"] for g in body["data"]]
        assert weeks[0] >= weeks[-1]
