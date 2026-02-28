"""DTO for team game log operations."""

from datetime import date

from pydantic import BaseModel


class TeamGameCreate(BaseModel):
    team_abbr: str
    season: int
    week: int

    day: str | None = None
    game_date: date | None = None
    game_time: str | None = None

    winner: str | None = None
    loser: str | None = None

    pts_w: int | None = None
    pts_l: int | None = None
    yds_w: int | None = None
    to_w: int | None = None
    yds_l: int | None = None
    to_l: int | None = None
