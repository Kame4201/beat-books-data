"""
Repository for injury report data access.
"""

from __future__ import annotations

from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from src.entities.injury_report import InjuryReport
from src.repositories.base_repo import BaseRepository
from src.dtos.injury_report_dto import InjuryReportCreate


class InjuryReportRepository(BaseRepository[InjuryReport]):
    """
    Repository for injury report operations.

    Handles all database operations for injury reports.
    """

    def __init__(self, session: Session) -> None:
        super().__init__(session=session, model=InjuryReport)

    def create_from_dto(self, dto: InjuryReportCreate) -> InjuryReport:
        """
        Create an injury report from a DTO.

        Args:
            dto: InjuryReportCreate DTO

        Returns:
            Created InjuryReport entity
        """
        entity = InjuryReport(
            season=dto.season,
            week=dto.week,
            player_name=dto.player_name,
            team=dto.team,
            position=dto.position,
            designation=dto.designation,
            injury_type=dto.injury_type,
            report_date=dto.report_date,
        )
        return self.create(entity, commit=True)

    def get_by_week(self, season: int, week: int) -> List[InjuryReport]:
        """
        Get all injury reports for a specific season and week.

        Args:
            season: NFL season year
            week: Week number

        Returns:
            List of InjuryReport entities
        """
        stmt = (
            select(InjuryReport)
            .where(and_(InjuryReport.season == season, InjuryReport.week == week))
            .order_by(InjuryReport.team, InjuryReport.player_name)
        )
        return list(self.session.execute(stmt).scalars().all())

    def get_by_team(self, season: int, week: int, team: str) -> List[InjuryReport]:
        """
        Get injury reports for a specific team, season, and week.

        Args:
            season: NFL season year
            week: Week number
            team: Team abbreviation

        Returns:
            List of InjuryReport entities
        """
        stmt = (
            select(InjuryReport)
            .where(
                and_(
                    InjuryReport.season == season,
                    InjuryReport.week == week,
                    InjuryReport.team == team,
                )
            )
            .order_by(InjuryReport.player_name)
        )
        return list(self.session.execute(stmt).scalars().all())

    def get_by_player(self, season: int, player_name: str) -> List[InjuryReport]:
        """
        Get all injury reports for a specific player in a season.

        Args:
            season: NFL season year
            player_name: Player's full name

        Returns:
            List of InjuryReport entities
        """
        stmt = (
            select(InjuryReport)
            .where(
                and_(
                    InjuryReport.season == season,
                    InjuryReport.player_name == player_name,
                )
            )
            .order_by(InjuryReport.week)
        )
        return list(self.session.execute(stmt).scalars().all())

    def delete_by_week(self, season: int, week: int) -> int:
        """
        Delete all injury reports for a specific week (for idempotent re-scraping).

        Args:
            season: NFL season year
            week: Week number

        Returns:
            Number of rows deleted
        """
        reports = self.get_by_week(season, week)
        count = len(reports)
        for report in reports:
            self.delete(report, commit=False)
        self.session.commit()
        return count

    def upsert_week_reports(
        self, season: int, week: int, dtos: List[InjuryReportCreate]
    ) -> List[InjuryReport]:
        """
        Delete existing reports for a week and insert new ones (idempotent upsert).

        Args:
            season: NFL season year
            week: Week number
            dtos: List of InjuryReportCreate DTOs

        Returns:
            List of created InjuryReport entities
        """
        # Delete existing reports for this week
        self.delete_by_week(season, week)

        # Insert new reports
        created = []
        for dto in dtos:
            entity = self.create_from_dto(dto)
            created.append(entity)

        return created
