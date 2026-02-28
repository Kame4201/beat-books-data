"""Pydantic DTOs for odds data validation."""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


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

    spread_home: Decimal | None = Field(
        None, description="Point spread for home team (e.g., -7.5)"
    )
    spread_away: Decimal | None = Field(
        None, description="Point spread for away team (e.g., +7.5)"
    )

    moneyline_home: int | None = Field(
        None, description="Moneyline odds for home team (e.g., -150)"
    )
    moneyline_away: int | None = Field(
        None, description="Moneyline odds for away team (e.g., +130)"
    )

    over_under: Decimal | None = Field(None, description="Total points over/under line")

    timestamp: datetime = Field(..., description="When this line was recorded")
    is_opening: bool = Field(False, description="Whether this is the opening line")
    is_closing: bool = Field(False, description="Whether this is the closing line")

    model_config = ConfigDict(
        json_schema_extra={
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
    )


class OddsResponse(BaseModel):
    """DTO for odds API responses."""

    id: int
    season: int
    week: int
    game_date: date

    home_team: str
    away_team: str
    sportsbook: str

    spread_home: Decimal | None
    spread_away: Decimal | None

    moneyline_home: int | None
    moneyline_away: int | None

    over_under: Decimal | None

    timestamp: datetime
    is_opening: bool
    is_closing: bool

    model_config = ConfigDict(from_attributes=True)


class OddsQuery(BaseModel):
    """DTO for querying odds data."""

    season: int | None = None
    week: int | None = None
    team: str | None = None
    sportsbook: str | None = None
    is_closing: bool | None = None
