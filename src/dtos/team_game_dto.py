# schemas/team_game_schema.py
from pydantic import BaseModel
from datetime import date
from typing import Optional


class TeamGameCreate(BaseModel):
    team_abbr: str
    season: int
    week: int

    day: Optional[str]
    game_date: Optional[date]
    game_time: Optional[str]

    winner: Optional[str]
    loser: Optional[str]

    pts_w: Optional[int]
    pts_l: Optional[int]
    yds_w: Optional[int]
    to_w: Optional[int]
    yds_l: Optional[int]
    to_l: Optional[int]
