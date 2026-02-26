"""
DTOs for receiving stats operations.
"""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ReceivingStatsCreate(BaseModel):
    """DTO for creating receiving stats records."""

    season: int = Field(..., ge=1920, le=2100, description="Season year")

    rk: int | None = Field(None, ge=0, description="Rank")
    player_name: str = Field(
        ..., min_length=1, max_length=128, description="Player name"
    )
    age: int | None = Field(None, ge=0, description="Player age")
    tm: str = Field(..., min_length=1, max_length=64, description="Team name")
    pos: str | None = Field(None, max_length=16, description="Position")

    g: int | None = Field(None, ge=0, description="Games played")
    gs: int | None = Field(None, ge=0, description="Games started")

    tgt: int | None = Field(None, ge=0, description="Targets")
    rec: int | None = Field(None, ge=0, description="Receptions")
    yds: int | None = Field(None, ge=0, description="Receiving yards")
    ypr: Decimal | None = Field(None, ge=0, description="Yards per reception")
    td: int | None = Field(None, ge=0, description="Touchdowns")
    first_downs: int | None = Field(None, ge=0, description="First downs")
    succ_pct: Decimal | None = Field(
        None, ge=0, le=100, description="Success percentage"
    )
    lng: int | None = Field(None, ge=0, description="Longest reception")
    rpg: Decimal | None = Field(None, ge=0, description="Receptions per game")
    ypg: Decimal | None = Field(None, ge=0, description="Yards per game")
    catch_pct: Decimal | None = Field(
        None, ge=0, le=100, description="Catch percentage"
    )
    ypt: Decimal | None = Field(None, ge=0, description="Yards per target")
    fmb: int | None = Field(None, ge=0, description="Fumbles")


class ReceivingStatsResponse(ReceivingStatsCreate):
    """DTO for receiving stats response."""

    id: int = Field(..., description="Record ID")

    model_config = ConfigDict(from_attributes=True)
