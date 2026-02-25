"""Unit tests for odds service with mocked API responses."""

import pytest
from datetime import datetime, date, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from decimal import Decimal

from src.services.odds_service import OddsService
from src.dtos.odds_dto import OddsCreate
from src.entities.odds import Odds


class TestOddsService:
    """Test suite for OddsService business logic."""

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        return MagicMock()

    @pytest.fixture
    def odds_service(self, mock_db_session):
        """Create OddsService instance with mocked DB."""
        return OddsService(mock_db_session)

    @pytest.fixture
    def sample_api_response(self):
        """Sample response from The Odds API."""
        return [
            {
                "id": "game123",
                "sport_key": "americanfootball_nfl",
                "commence_time": "2024-09-08T20:00:00Z",
                "home_team": "Kansas City Chiefs",
                "away_team": "Baltimore Ravens",
                "bookmakers": [
                    {
                        "key": "draftkings",
                        "title": "DraftKings",
                        "markets": [
                            {
                                "key": "spreads",
                                "outcomes": [
                                    {
                                        "name": "Kansas City Chiefs",
                                        "price": -110,
                                        "point": -3.0,
                                    },
                                    {
                                        "name": "Baltimore Ravens",
                                        "price": -110,
                                        "point": 3.0,
                                    },
                                ],
                            },
                            {
                                "key": "h2h",
                                "outcomes": [
                                    {"name": "Kansas City Chiefs", "price": -150},
                                    {"name": "Baltimore Ravens", "price": 130},
                                ],
                            },
                            {
                                "key": "totals",
                                "outcomes": [
                                    {"name": "Over", "point": 47.5},
                                    {"name": "Under", "point": 47.5},
                                ],
                            },
                        ],
                    }
                ],
            }
        ]

    def test_parse_api_response_to_dtos(self, odds_service, sample_api_response):
        """Test parsing API response into DTOs."""
        season = 2024
        week = 1

        dtos = odds_service.parse_api_response_to_dtos(
            sample_api_response, season, week, is_closing=True
        )

        assert len(dtos) == 1
        dto = dtos[0]

        assert isinstance(dto, OddsCreate)
        assert dto.season == 2024
        assert dto.week == 1
        assert dto.sportsbook == "DraftKings"
        assert dto.spread_home == -3.0
        assert dto.spread_away == 3.0
        assert dto.moneyline_home == -150
        assert dto.moneyline_away == 130
        assert dto.over_under == 47.5
        assert dto.is_closing is True
        assert dto.is_opening is False

    @pytest.mark.asyncio
    async def test_fetch_odds_from_api_success(self, odds_service, sample_api_response):
        """Test successful API fetch."""
        # Set api_key directly since it's captured at init time
        odds_service.api_key = "test_api_key"
        odds_service.base_url = "https://api.test.com"

        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.json.return_value = sample_api_response
            mock_response.raise_for_status = MagicMock()

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            result = await odds_service.fetch_odds_from_api()

            assert result == sample_api_response

    @pytest.mark.asyncio
    async def test_fetch_odds_from_api_no_key(self, odds_service):
        """Test API fetch fails without API key."""
        odds_service.api_key = ""

        with pytest.raises(ValueError, match="ODDS_API_KEY not configured"):
            await odds_service.fetch_odds_from_api()

    def test_team_name_to_abbr(self, odds_service):
        """Test team name abbreviation conversion."""
        assert odds_service._team_name_to_abbr("Kansas City Chiefs") == "KC"
        assert odds_service._team_name_to_abbr("Baltimore Ravens") == "BAL"
        # Unknown team should return first 3 chars uppercase
        assert odds_service._team_name_to_abbr("Unknown Team") == "UNK"

    @pytest.mark.asyncio
    async def test_fetch_and_store_current_odds(
        self, odds_service, sample_api_response, mock_db_session
    ):
        """Test fetching and storing odds end-to-end."""
        season = 2024
        week = 1

        # Mock the API fetch
        odds_service.fetch_odds_from_api = AsyncMock(return_value=sample_api_response)

        # Mock the repository create_or_skip
        with patch("src.services.odds_service.OddsRepository") as mock_repo:
            mock_odds = MagicMock()
            mock_odds.id = 1
            mock_repo.create_or_skip.return_value = mock_odds

            result = await odds_service.fetch_and_store_current_odds(
                season, week, is_closing=True
            )

            assert len(result) == 1
            assert result[0] == 1
            mock_repo.create_or_skip.assert_called_once()

    def test_get_closing_line_value(self, odds_service, mock_db_session):
        """Test calculating closing line value."""
        season = 2024
        week = 1
        team = "KC"

        # Mock repository response
        mock_odds = MagicMock()
        mock_odds.spread_home = Decimal("-3.0")
        mock_odds.spread_away = Decimal("3.0")
        mock_odds.moneyline_home = -150
        mock_odds.moneyline_away = 130
        mock_odds.over_under = Decimal("47.5")
        mock_odds.sportsbook = "DraftKings"
        mock_odds.timestamp = datetime(2024, 9, 8, 20, 0, tzinfo=timezone.utc)

        with patch("src.services.odds_service.OddsRepository") as mock_repo:
            mock_repo.get_by_team.return_value = [mock_odds]

            clv = odds_service.get_closing_line_value(season, week, team, "DraftKings")

            assert clv is not None
            assert clv["spread_home"] == -3.0
            assert clv["moneyline_home"] == -150
            assert clv["over_under"] == 47.5
            assert clv["sportsbook"] == "DraftKings"

    def test_get_closing_line_value_not_found(self, odds_service, mock_db_session):
        """Test CLV returns None when no closing lines found."""
        with patch("src.services.odds_service.OddsRepository") as mock_repo:
            mock_repo.get_by_team.return_value = []

            clv = odds_service.get_closing_line_value(2024, 1, "KC")

            assert clv is None
