"""Pydantic DTOs for odds data validation."""

from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional
from decimal import Decimal


class OddsCreate(BaseModel):
    """DTO for creating new odds records."""

    season: int = Field(..., ge=1920, le=2100, description="NFL season year")
    week: int = Field(
        ..., ge=1, le=22, description="Week number (1-18 regular, 19-22 playoffs)"
    )
    game_date: date = Field(..., description="Date of the game")

    home_team: str = Field(..., max_length=64, description="Home team abbreviation")
    away_team: str = Field(..., max_length=64, description="Away team abbreviation")
    sportsbook: str = Field(
        ..., max_length=64, description="Sportsbook name (e.g., DraftKings, FanDuel)"
    )

    spread_home: Optional[Decimal] = Field(
        None, description="Point spread for home team (e.g., -7.5)"
    )
    spread_away: Optional[Decimal] = Field(
        None, description="Point spread for away team (e.g., +7.5)"
    )

    moneyline_home: Optional[int] = Field(
        None, description="Moneyline odds for home team (e.g., -150)"
    )
    moneyline_away: Optional[int] = Field(
        None, description="Moneyline odds for away team (e.g., +130)"
    )

    over_under: Optional[Decimal] = Field(
        None, description="Total points over/under line"
    )

    timestamp: datetime = Field(..., description="When this line was recorded")
    is_opening: bool = Field(False, description="Whether this is the opening line")
    is_closing: bool = Field(False, description="Whether this is the closing line")

    class Config:
        json_schema_extra = {
            "example": {
                "season": 2024,
                "week": 1,
                "game_date": "2024-09-08",
                "home_team": "KC",
                "away_team": "BAL",
                "sportsbook": "DraftKings",
                "spread_home": -3.0,
                "spread_away": 3.0,
                "moneyline_home": -150,
                "moneyline_away": 130,
                "over_under": 47.5,
                "timestamp": "2024-09-07T10:00:00",
                "is_opening": False,
                "is_closing": True,
            }
        }


class OddsResponse(BaseModel):
    """DTO for odds API responses."""

    id: int
    season: int
    week: int
    game_date: date

    home_team: str
    away_team: str
    sportsbook: str

    spread_home: Optional[Decimal]
    spread_away: Optional[Decimal]

    moneyline_home: Optional[int]
    moneyline_away: Optional[int]

    over_under: Optional[Decimal]

    timestamp: datetime
    is_opening: bool
    is_closing: bool

    class Config:
        from_attributes = True


class OddsQuery(BaseModel):
    """DTO for querying odds data."""

    season: Optional[int] = None
    week: Optional[int] = None
    team: Optional[str] = None
    sportsbook: Optional[str] = None
    is_closing: Optional[bool] = None
