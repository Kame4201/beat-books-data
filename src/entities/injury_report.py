"""
Entity for tracking weekly injury reports.
"""

from __future__ import annotations

from sqlalchemy import Column, Integer, String, Date
from src.entities.base import Base


class InjuryReport(Base):
    """
    Tracks weekly injury designations for NFL players.

    Data typically scraped from Pro-Football-Reference or ESPN.
    Includes injury status (Questionable/Doubtful/Out) and injury type.
    """

    __tablename__ = "injury_reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    season = Column(Integer, nullable=False, index=True)
    week = Column(Integer, nullable=False, index=True)
    player_name = Column(String(255), nullable=False, index=True)
    team = Column(String(10), nullable=False, index=True)
    position = Column(String(10), nullable=True)
    designation = Column(String(50), nullable=False)  # Questionable/Doubtful/Out/IR
    injury_type = Column(String(100), nullable=True)  # ankle, knee, hamstring, etc.
    report_date = Column(Date, nullable=True)  # when the report was issued
