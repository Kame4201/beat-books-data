"""DTO for team game log operations."""

from pydantic import BaseModel
from datetime import date
from typing import Optional


class TeamGameCreate(BaseModel):
    team_abbr: str
    season: int
    week: int

    day: Optional[str] = None
    game_date: Optional[date] = None
    game_time: Optional[str] = None

    winner: Optional[str] = None
    loser: Optional[str] = None

    pts_w: Optional[int] = None
    pts_l: Optional[int] = None
    yds_w: Optional[int] = None
    to_w: Optional[int] = None
    yds_l: Optional[int] = None
    to_l: Optional[int] = None
