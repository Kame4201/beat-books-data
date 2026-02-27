"""Tests for POST /scrape/batch/{season} endpoint."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from src.core.database import get_db
from src.entities.base import Base
from src.main import app


@pytest.fixture()
def db_session():
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
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


class TestBatchScrapeRoute:
    def test_dry_run_returns_skipped(self, client):
        """POST with dry_run=true skips actual scraping."""
        resp = client.post(
            "/scrape/batch/2024",
            json={"stats": ["team_offense", "standings"], "dry_run": True},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["season"] == 2024
        assert len(body["results"]) == 2
        assert all(r["status"] == "skipped (dry_run)" for r in body["results"])

    def test_batch_dispatches_scrape_functions(self, client):
        """POST dispatches to the correct scrape functions."""
        mock_fn = AsyncMock(return_value={"records": 32})

        with patch.dict("src.main.SCRAPE_DISPATCH", {"team_offense": mock_fn}):
            resp = client.post(
                "/scrape/batch/2024",
                json={"stats": ["team_offense"], "dry_run": False},
            )
        assert resp.status_code == 200
        body = resp.json()
        assert body["results"][0]["status"] == "success"
        mock_fn.assert_called_once()

    def test_batch_handles_scrape_error(self, client):
        """POST continues on scrape error and reports it."""
        mock_fn = AsyncMock(side_effect=RuntimeError("scrape failed"))

        with patch.dict("src.main.SCRAPE_DISPATCH", {"team_offense": mock_fn}):
            resp = client.post(
                "/scrape/batch/2024",
                json={"stats": ["team_offense"], "dry_run": False},
            )
        assert resp.status_code == 200
        body = resp.json()
        assert body["results"][0]["status"] == "error"
        assert "scrape failed" in body["results"][0]["error"]

    def test_batch_default_all_stats(self, client):
        """POST with no stats specified defaults to all stat types."""
        resp = client.post(
            "/scrape/batch/2024",
            json={"dry_run": True},
        )
        assert resp.status_code == 200
        body = resp.json()
        # Should include all 15 stat types
        assert len(body["results"]) == 15
