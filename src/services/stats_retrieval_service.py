"""Service layer for retrieving NFL stats data."""
from __future__ import annotations

from typing import Optional
from sqlalchemy.orm import Session

from src.repositories.team_offense_repo import TeamOffenseRepository
from src.repositories.passing_stats_repo import PassingStatsRepository
from src.repositories.rushing_stats_repo import RushingStatsRepository
from src.repositories.receiving_stats_repo import ReceivingStatsRepository
from src.repositories.standings_repo import StandingsRepository
from src.repositories.team_game_repo import TeamGameRepository


class StatsRetrievalService:
    """Service for retrieving NFL statistics with pagination and sorting support."""

    def __init__(self, session: Session):
        self.session = session
        self.team_offense_repo = TeamOffenseRepository(session)
        self.passing_stats_repo = PassingStatsRepository(session)
        self.rushing_stats_repo = RushingStatsRepository(session)
        self.receiving_stats_repo = ReceivingStatsRepository(session)
        self.standings_repo = StandingsRepository(session)
        self.team_game_repo = TeamGameRepository

    def get_all_teams(
        self,
        season: int,
        *,
        offset: int = 0,
        limit: int = 50,
        sort_by: str = "pf",
        order: str = "desc"
    ) -> dict:
        """
        Get all teams for a given season with pagination.

        Args:
            season: The season year
            offset: Number of records to skip (default: 0)
            limit: Maximum number of records to return (default: 50, max: 200)
            sort_by: Field to sort by (default: "pf" for points for)
            order: Sort order "asc" or "desc" (default: "desc")

        Returns:
            Dictionary with 'data' list and 'total' count
        """
        # Enforce max limit
        limit = min(limit, 200)

        teams = self.team_offense_repo.find_by_season(
            season=season,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            order=order
        )

        total = self.team_offense_repo.count_by_season(season)

        return {
            "data": teams,
            "total": total,
            "offset": offset,
            "limit": limit
        }

    def get_team_stats(self, team: str, season: int) -> Optional[dict]:
        """
        Get stats for a specific team in a given season.

        Args:
            team: Team abbreviation or name
            season: The season year

        Returns:
            Team stats dictionary or None if not found
        """
        team_stats = self.team_offense_repo.find_by_team_and_season(team, season)

        if team_stats is None:
            return None

        # Convert to dict (would normally use a DTO here)
        return {
            "id": team_stats.id,
            "season": team_stats.season,
            "team": team_stats.tm,
            "games": team_stats.g,
            "points_for": team_stats.pf,
            "total_yards": team_stats.yds,
            "plays": team_stats.ply,
            "yards_per_play": float(team_stats.ypp) if team_stats.ypp else None,
            "turnovers": team_stats.turnovers,
            "fumbles_lost": team_stats.fl,
            "first_downs": team_stats.firstd_total,
            "passing": {
                "completions": team_stats.cmp,
                "attempts": team_stats.att_pass,
                "yards": team_stats.yds_pass,
                "touchdowns": team_stats.td_pass,
                "interceptions": team_stats.ints,
                "net_yards_per_attempt": float(team_stats.nypa) if team_stats.nypa else None,
                "first_downs": team_stats.firstd_pass,
            },
            "rushing": {
                "attempts": team_stats.att_rush,
                "yards": team_stats.yds_rush,
                "touchdowns": team_stats.td_rush,
                "yards_per_attempt": float(team_stats.ypa) if team_stats.ypa else None,
                "first_downs": team_stats.firstd_rush,
            },
            "penalties": {
                "count": team_stats.pen,
                "yards": team_stats.yds_pen,
                "first_downs": team_stats.firstpy,
            },
            "scoring_pct": float(team_stats.sc_pct) if team_stats.sc_pct else None,
            "turnover_pct": float(team_stats.to_pct) if team_stats.to_pct else None,
        }

    def get_player_stats(self, player_name: str, season: int) -> dict:
        """
        Get stats for a specific player in a given season.

        Args:
            player_name: Player name (case-insensitive partial match)
            season: The season year

        Returns:
            Dictionary with player stats from all categories
        """
        passing = self.passing_stats_repo.find_by_player(player_name, season)
        rushing = self.rushing_stats_repo.search_players(player_name, season)
        receiving = self.receiving_stats_repo.search_players(player_name, season)

        return {
            "player_name": player_name,
            "season": season,
            "passing": passing,
            "rushing": rushing,
            "receiving": receiving,
        }

    def get_standings(
        self,
        season: int,
        *,
        offset: int = 0,
        limit: int = 50,
        sort_by: str = "win_pct",
        order: str = "desc"
    ) -> dict:
        """
        Get standings for a given season with pagination.

        Args:
            season: The season year
            offset: Number of records to skip (default: 0)
            limit: Maximum number of records to return (default: 50, max: 200)
            sort_by: Field to sort by (default: "win_pct")
            order: Sort order "asc" or "desc" (default: "desc")

        Returns:
            Dictionary with 'data' list and 'total' count
        """
        # Enforce max limit
        limit = min(limit, 200)

        standings = self.standings_repo.find_by_season(
            season=season,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            order=order
        )

        total = self.standings_repo.count_by_season(season)

        return {
            "data": standings,
            "total": total,
            "offset": offset,
            "limit": limit
        }

    def get_games(
        self,
        season: int,
        week: Optional[int] = None,
        *,
        offset: int = 0,
        limit: int = 50,
        sort_by: str = "week",
        order: str = "asc"
    ) -> dict:
        """
        Get games for a season, optionally filtered by week.

        Args:
            season: The season year
            week: Optional week number to filter by
            offset: Number of records to skip (default: 0)
            limit: Maximum number of records to return (default: 50, max: 200)
            sort_by: Field to sort by (default: "week")
            order: Sort order "asc" or "desc" (default: "asc")

        Returns:
            Dictionary with 'data' list and 'total' count
        """
        # Enforce max limit
        limit = min(limit, 200)

        games = self.team_game_repo.find_by_season_and_week(
            db=self.session,
            season=season,
            week=week,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            order=order
        )

        total = self.team_game_repo.count_by_season(self.session, season, week)

        return {
            "data": games,
            "total": total,
            "offset": offset,
            "limit": limit,
            "week": week
        }

    def search_players(
        self,
        query: str,
        season: Optional[int] = None,
        position: Optional[str] = None,
        *,
        offset: int = 0,
        limit: int = 50
    ) -> dict:
        """
        Search for players across all stat categories.

        Args:
            query: Player name search query (case-insensitive partial match)
            season: Optional season filter
            position: Optional position filter
            offset: Number of records to skip (default: 0)
            limit: Maximum number of records to return (default: 50, max: 200)

        Returns:
            Dictionary with results from all stat categories
        """
        # Enforce max limit
        limit = min(limit, 200)

        passing = self.passing_stats_repo.search_players(
            query=query,
            season=season,
            limit=limit,
            offset=offset
        )

        rushing = self.rushing_stats_repo.search_players(
            query=query,
            season=season,
            position=position,
            limit=limit,
            offset=offset
        )

        receiving = self.receiving_stats_repo.search_players(
            query=query,
            season=season,
            position=position,
            limit=limit,
            offset=offset
        )

        return {
            "query": query,
            "season": season,
            "position": position,
            "passing": passing,
            "rushing": rushing,
            "receiving": receiving,
        }
