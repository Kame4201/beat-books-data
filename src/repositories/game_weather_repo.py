"""
Repository for game weather data access.
"""

from __future__ import annotations

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from src.entities.game_weather import GameWeather
from src.repositories.base_repo import BaseRepository
from src.dtos.game_weather_dto import GameWeatherCreate


class GameWeatherRepository(BaseRepository[GameWeather]):
    """
    Repository for game weather operations.

    Handles all database operations for game weather data.
    """

    def __init__(self, session: Session) -> None:
        super().__init__(session=session, model=GameWeather)

    def create_from_dto(self, dto: GameWeatherCreate) -> GameWeather:
        """
        Create a game weather record from a DTO.

        Args:
            dto: GameWeatherCreate DTO

        Returns:
            Created GameWeather entity
        """
        entity = GameWeather(
            season=dto.season,
            week=dto.week,
            home_team=dto.home_team,
            stadium=dto.stadium,
            is_dome=dto.is_dome,
            temperature=dto.temperature,
            wind_speed=dto.wind_speed,
            precipitation=dto.precipitation,
            humidity=dto.humidity,
            weather_condition=dto.weather_condition,
            game_time=dto.game_time,
            fetched_at=dto.fetched_at,
        )
        return self.create(entity, commit=True)

    def get_by_week(self, season: int, week: int) -> List[GameWeather]:
        """
        Get all game weather records for a specific season and week.

        Args:
            season: NFL season year
            week: Week number

        Returns:
            List of GameWeather entities
        """
        stmt = (
            select(GameWeather)
            .where(and_(GameWeather.season == season, GameWeather.week == week))
            .order_by(GameWeather.home_team)
        )
        return list(self.session.execute(stmt).scalars().all())

    def get_by_game(
        self, season: int, week: int, home_team: str
    ) -> Optional[GameWeather]:
        """
        Get weather data for a specific game.

        Args:
            season: NFL season year
            week: Week number
            home_team: Home team abbreviation

        Returns:
            GameWeather entity or None
        """
        stmt = select(GameWeather).where(
            and_(
                GameWeather.season == season,
                GameWeather.week == week,
                GameWeather.home_team == home_team,
            )
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def get_outdoor_games(self, season: int, week: int) -> List[GameWeather]:
        """
        Get weather data for outdoor stadium games only.

        Args:
            season: NFL season year
            week: Week number

        Returns:
            List of GameWeather entities for outdoor games
        """
        stmt = (
            select(GameWeather)
            .where(
                and_(
                    GameWeather.season == season,
                    GameWeather.week == week,
                    ~GameWeather.is_dome,
                )
            )
            .order_by(GameWeather.home_team)
        )
        return list(self.session.execute(stmt).scalars().all())

    def delete_by_game(self, season: int, week: int, home_team: str) -> bool:
        """
        Delete weather data for a specific game.

        Args:
            season: NFL season year
            week: Week number
            home_team: Home team abbreviation

        Returns:
            True if deleted, False if not found
        """
        existing = self.get_by_game(season, week, home_team)
        if existing:
            self.delete(existing, commit=True)
            return True
        return False

    def upsert_game_weather(self, dto: GameWeatherCreate) -> GameWeather:
        """
        Insert or update weather data for a game (idempotent).

        Args:
            dto: GameWeatherCreate DTO

        Returns:
            Created or updated GameWeather entity
        """
        # Delete existing weather data for this game
        self.delete_by_game(dto.season, dto.week, dto.home_team)

        # Insert new weather data
        return self.create_from_dto(dto)
