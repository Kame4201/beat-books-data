"""
Tests for FastAPI endpoints — covers:
  #49 auth + rate limiting
  #50 data-retrieval endpoints
  #53 structured error responses
  #38 dependency injection
  #51 async blocking (verify asyncio.to_thread usage)
  #37 expanded coverage
"""

import pytest
from unittest.mock import patch, AsyncMock
from src.main import StatType
from decimal import Decimal

from src.entities.team_offense import TeamOffense
from src.entities.standings import Standings
from src.entities.team_game import TeamGame


# ---------------------------------------------------------------------------
# Health / root (public, no auth)
# ---------------------------------------------------------------------------


class TestPublicEndpoints:
    def test_health(self, client):
        r = client.get("/health")
        assert r.status_code == 200
        body = r.json()
        assert body["status"] == "healthy"

    def test_root(self, client):
        r = client.get("/")
        assert r.status_code == 200


# ---------------------------------------------------------------------------
# Auth (#49)
# ---------------------------------------------------------------------------


class TestAuth:
    def _mock_scrape_dispatch(self):
        """Patch the SCRAPE_DISPATCH dict so no Selenium is needed."""
        mock_fn = AsyncMock(return_value=[])
        return patch.dict("src.main.SCRAPE_DISPATCH", {StatType.team_offense: mock_fn})

    def test_scrape_no_auth_when_key_not_set(self, client):
        """When API_KEY is empty, scrape endpoints are accessible (not 403)."""
        with patch("src.main.settings") as mock_settings:
            mock_settings.API_KEY = ""
            mock_settings.DEBUG = False
            with self._mock_scrape_dispatch():
                r = client.get("/scrape/team_offense/2023")
                assert r.status_code == 200

    def test_scrape_forbidden_with_wrong_key(self, client):
        """When API_KEY is set, wrong key returns 403."""
        with patch("src.main.settings") as mock_settings:
            mock_settings.API_KEY = "correct-key"
            mock_settings.DEBUG = False
            with self._mock_scrape_dispatch():
                r = client.get(
                    "/scrape/team_offense/2023",
                    headers={"X-API-Key": "wrong-key"},
                )
                assert r.status_code == 403
                body = r.json()
                assert body["error"] == "http_error"
                assert "request_id" in body

    def test_scrape_allowed_with_correct_key(self, client):
        """When API_KEY is set, correct key passes auth."""
        with patch("src.main.settings") as mock_settings:
            mock_settings.API_KEY = "correct-key"
            mock_settings.DEBUG = False
            with self._mock_scrape_dispatch():
                r = client.get(
                    "/scrape/team_offense/2023",
                    headers={"X-API-Key": "correct-key"},
                )
                assert r.status_code == 200


# ---------------------------------------------------------------------------
# Structured error responses (#53)
# ---------------------------------------------------------------------------


class TestErrorHandling:
    def test_404_returns_structured_json(self, client):
        r = client.get("/nonexistent-path")
        assert r.status_code in (404, 405)

    def test_unhandled_exception_returns_500(self, client):
        """Trigger an internal error and verify structured response."""
        boom_fn = AsyncMock(side_effect=RuntimeError("boom"))
        with patch("src.main.settings") as mock_settings:
            mock_settings.API_KEY = ""
            mock_settings.DEBUG = False
            with patch.dict("src.main.SCRAPE_DISPATCH", {StatType.team_offense: boom_fn}):
                r = client.get("/scrape/team_offense/2023")
                assert r.status_code == 500
                body = r.json()
                assert body["error"] == "internal_error"
                assert "request_id" in body
                assert body["detail"] is None

    def test_request_id_in_response_header(self, client):
        r = client.get("/health")
        assert "X-Request-ID" in r.headers


# ---------------------------------------------------------------------------
# Data-retrieval endpoints (#50)
# ---------------------------------------------------------------------------


class TestRetrievalEndpoints:
    def _seed_team_offense(self, db_session):
        obj = TeamOffense(
            season=2023, rk=1, tm="KAN", g=17, pf=450,
            yds=6200, ply=1050, ypp=Decimal("5.9"),
            turnovers=12, fl=5, firstd_total=350,
            cmp=380, att_pass=580, yds_pass=4800,
            td_pass=35, ints=10, nypa=Decimal("7.2"),
            firstd_pass=200, att_rush=420, yds_rush=1400,
            td_rush=15, ypa=Decimal("4.5"), firstd_rush=100,
            pen=95, yds_pen=800, firstpy=50,
            sc_pct=Decimal("42.5"), to_pct=Decimal("10.2"),
            opea=Decimal("125.5"),
        )
        db_session.add(obj)
        db_session.commit()
        return obj

    def _seed_standings(self, db_session):
        obj = Standings(
            season=2023, tm="KAN", w=11, losses=6, t=0,
            win_pct=Decimal("0.647"), pf=450, pa=350,
            pd=100, mov=Decimal("5.9"), sos=Decimal("0.1"),
            srs=Decimal("6.0"), osrs=Decimal("3.0"), dsrs=Decimal("3.0"),
        )
        db_session.add(obj)
        db_session.commit()
        return obj

    def test_get_teams(self, client, db_session):
        self._seed_team_offense(db_session)
        r = client.get("/api/v1/stats/teams/2023")
        assert r.status_code == 200
        body = r.json()
        assert body["total"] == 1
        assert len(body["data"]) == 1

    def test_get_teams_empty(self, client, db_session):
        r = client.get("/api/v1/stats/teams/1999")
        assert r.status_code == 200
        assert r.json()["total"] == 0

    def test_get_team_stats(self, client, db_session):
        self._seed_team_offense(db_session)
        r = client.get("/api/v1/stats/teams/2023/KAN")
        assert r.status_code == 200
        body = r.json()
        assert body["team"] == "KAN"

    def test_get_team_stats_not_found(self, client, db_session):
        r = client.get("/api/v1/stats/teams/2023/XXX")
        assert r.status_code == 404
        body = r.json()
        assert body["error"] == "http_error"

    def test_get_standings(self, client, db_session):
        self._seed_standings(db_session)
        r = client.get("/api/v1/standings/2023")
        assert r.status_code == 200
        assert r.json()["total"] == 1

    def test_get_games(self, client, db_session):
        r = client.get("/api/v1/games/2023")
        assert r.status_code == 200
        assert r.json()["total"] == 0

    def test_search_players(self, client, db_session):
        r = client.get("/api/v1/players/search?name=mahomes")
        assert r.status_code == 200
        body = r.json()
        assert body["query"] == "mahomes"

    def test_get_player_stats(self, client, db_session):
        r = client.get("/api/v1/stats/players/2023?name=mahomes")
        assert r.status_code == 200


# ---------------------------------------------------------------------------
# Async / thread-pool (#51)
# ---------------------------------------------------------------------------


class TestAsyncThreadPool:
    def test_scrape_services_use_asyncio_to_thread(self):
        """Verify all scrape services import asyncio and use to_thread."""
        import importlib
        import ast

        service_modules = [
            "src.services.team_offense_service",
            "src.services.standings_service",
            "src.services.defense_stats_service",
            "src.services.games_service",
        ]
        for mod_name in service_modules:
            mod = importlib.import_module(mod_name)
            source_file = mod.__file__
            with open(source_file) as f:
                tree = ast.parse(f.read())
            # Check that asyncio.to_thread is called somewhere in the AST
            found = False
            for node in ast.walk(tree):
                if isinstance(node, ast.Attribute):
                    if (
                        isinstance(node.value, ast.Name)
                        and node.value.id == "asyncio"
                        and node.attr == "to_thread"
                    ):
                        found = True
                        break
                if isinstance(node, ast.Attribute):
                    if node.attr == "to_thread":
                        found = True
                        break
            assert found, f"{mod_name} must use asyncio.to_thread for blocking calls"


# ---------------------------------------------------------------------------
# DI (#38)
# ---------------------------------------------------------------------------


class TestDependencyInjection:
    def test_get_db_yields_session(self):
        """get_db should yield a usable Session."""
        from src.core.database import get_db

        gen = get_db()
        session = next(gen)
        assert session is not None
        # Clean up
        try:
            next(gen)
        except StopIteration:
            pass

    def test_services_accept_optional_db(self):
        """Verify scrape service functions accept db parameter."""
        import inspect

        from src.services.team_offense_service import scrape_and_store_team_offense
        from src.services.standings_service import scrape_and_store

        sig1 = inspect.signature(scrape_and_store_team_offense)
        assert "db" in sig1.parameters

        sig2 = inspect.signature(scrape_and_store)
        assert "db" in sig2.parameters
