"""Service layer for odds business logic. NO SQL here."""

from datetime import UTC, datetime
from typing import Any

import httpx
from sqlalchemy.orm import Session

from src.core.config import settings
from src.dtos.odds_dto import OddsCreate
from src.repositories.odds_repo import OddsRepository


class OddsService:
    """
    Business logic for fetching and storing odds data.
    Integrates with The Odds API (https://the-odds-api.com/).
    """

    def __init__(self, db_session: Session):
        self.db = db_session
        self.api_key = settings.ODDS_API_KEY
        self.base_url = settings.ODDS_API_BASE_URL

    async def fetch_odds_from_api(
        self, sport: str = "americanfootball_nfl", markets: str = "h2h,spreads,totals"
    ) -> list[dict[str, Any]]:
        """
        Fetch current odds from The Odds API.

        Args:
            sport: Sport identifier (default: americanfootball_nfl)
            markets: Comma-separated markets (h2h=moneyline, spreads, totals=over/under)

        Returns:
            List of game odds from API

        Raises:
            httpx.HTTPError: If API request fails
        """
        if not self.api_key:
            raise ValueError("ODDS_API_KEY not configured in settings")

        url = f"{self.base_url}/v4/sports/{sport}/odds"
        params = {
            "apiKey": self.api_key,
            "regions": "us",
            "markets": markets,
            "oddsFormat": "american",
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()

    def parse_api_response_to_dtos(
        self,
        api_data: list[dict[str, Any]],
        season: int,
        week: int,
        is_opening: bool = False,
        is_closing: bool = False,
    ) -> list[OddsCreate]:
        """
        Parse The Odds API response into OddsCreate DTOs.

        Args:
            api_data: Raw API response data
            season: NFL season year
            week: Week number
            is_opening: Mark these as opening lines
            is_closing: Mark these as closing lines

        Returns:
            List of validated OddsCreate DTOs
        """
        odds_dtos = []
        timestamp = datetime.now(UTC)

        for game in api_data:
            commence_time = datetime.fromisoformat(
                game["commence_time"].replace("Z", "+00:00")
            )
            game_date = commence_time.date()

            home_team = game.get("home_team", "")
            away_team = game.get("away_team", "")

            # Convert full team names to abbreviations (simplified - would need mapping)
            home_abbr = self._team_name_to_abbr(home_team)
            away_abbr = self._team_name_to_abbr(away_team)

            # Parse bookmaker data
            for bookmaker in game.get("bookmakers", []):
                sportsbook = bookmaker.get("title", "")

                spread_home = None
                spread_away = None
                moneyline_home = None
                moneyline_away = None
                over_under = None

                # Extract market data
                for market in bookmaker.get("markets", []):
                    market_key = market.get("key")

                    if market_key == "spreads":
                        for outcome in market.get("outcomes", []):
                            if outcome.get("name") == home_team:
                                spread_home = outcome.get("point")
                            elif outcome.get("name") == away_team:
                                spread_away = outcome.get("point")

                    elif market_key == "h2h":
                        for outcome in market.get("outcomes", []):
                            if outcome.get("name") == home_team:
                                moneyline_home = outcome.get("price")
                            elif outcome.get("name") == away_team:
                                moneyline_away = outcome.get("price")

                    elif market_key == "totals":
                        for outcome in market.get("outcomes", []):
                            if outcome.get("name") == "Over":
                                over_under = outcome.get("point")

                # Create DTO
                odds_dto = OddsCreate(
                    season=season,
                    week=week,
                    game_date=game_date,
                    home_team=home_abbr,
                    away_team=away_abbr,
                    sportsbook=sportsbook,
                    spread_home=spread_home,
                    spread_away=spread_away,
                    moneyline_home=moneyline_home,
                    moneyline_away=moneyline_away,
                    over_under=over_under,
                    timestamp=timestamp,
                    is_opening=is_opening,
                    is_closing=is_closing,
                )
                odds_dtos.append(odds_dto)

        return odds_dtos

    def _team_name_to_abbr(self, full_name: str) -> str:
        """
        Convert full team name to abbreviation.
        TODO: Implement full mapping or load from database.
        """
        # Simplified mapping - should be more comprehensive
        team_map = {
            "Kansas City Chiefs": "KC",
            "Baltimore Ravens": "BAL",
            "San Francisco 49ers": "SF",
            "Philadelphia Eagles": "PHI",
            "Dallas Cowboys": "DAL",
            "Buffalo Bills": "BUF",
            "Miami Dolphins": "MIA",
            "Detroit Lions": "DET",
            # Add all 32 teams...
        }
        return team_map.get(full_name, full_name[:3].upper())

    async def fetch_and_store_current_odds(
        self, season: int, week: int, is_opening: bool = False, is_closing: bool = False
    ) -> list[int]:
        """
        Fetch current odds from API and store in database.

        Args:
            season: NFL season
            week: Week number
            is_opening: Mark as opening lines
            is_closing: Mark as closing lines

        Returns:
            List of created odds record IDs
        """
        # Fetch from API
        api_data = await self.fetch_odds_from_api()

        # Parse to DTOs
        odds_dtos = self.parse_api_response_to_dtos(
            api_data, season, week, is_opening, is_closing
        )

        # Store in database (skip duplicates)
        stored_ids: list[int] = []
        for dto in odds_dtos:
            odds_record = OddsRepository.create_or_skip(self.db, dto)
            stored_ids.append(int(odds_record.id))

        return stored_ids

    def get_closing_line_value(
        self, season: int, week: int, team: str, sportsbook: str = "consensus"
    ) -> dict[str, Any] | None:
        """
        Calculate closing line value for a team.
        CLV = difference between your bet and closing line.

        Args:
            season: Season year
            week: Week number
            team: Team abbreviation
            sportsbook: Sportsbook name (default: consensus)

        Returns:
            Dictionary with CLV metrics or None if not found
        """
        closing_lines = OddsRepository.get_by_team(
            self.db, team, season, week, is_closing=True
        )

        if not closing_lines:
            return None

        # Filter by sportsbook if specified
        if sportsbook != "consensus":
            closing_lines = [
                line for line in closing_lines if line.sportsbook == sportsbook
            ]

        if not closing_lines:
            return None

        # Return the most recent closing line
        latest = max(closing_lines, key=lambda x: x.timestamp)

        return {
            "spread_home": float(latest.spread_home) if latest.spread_home else None,
            "spread_away": float(latest.spread_away) if latest.spread_away else None,
            "moneyline_home": latest.moneyline_home,
            "moneyline_away": latest.moneyline_away,
            "over_under": float(latest.over_under) if latest.over_under else None,
            "sportsbook": latest.sportsbook,
            "timestamp": latest.timestamp,
        }
