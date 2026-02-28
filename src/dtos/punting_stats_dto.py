"""
DTOs for punting stats operations.
"""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PuntingStatsCreate(BaseModel):
    """DTO for creating punting stats records."""

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

    pnt: int | None = Field(None, ge=0, description="Punts")
    yds: int | None = Field(None, ge=0, description="Punt yards")
    ypp: Decimal | None = Field(None, ge=0, description="Yards per punt")
    ret_yds: int | None = Field(None, ge=0, description="Return yards allowed")
    net_yds: int | None = Field(None, ge=0, description="Net yards")
    ny_pa: Decimal | None = Field(None, ge=0, description="Net yards per punt")
    lng: int | None = Field(None, ge=0, description="Longest punt")
    tb: int | None = Field(None, ge=0, description="Touchbacks")
    tb_pct: Decimal | None = Field(
        None, ge=0, le=100, description="Touchback percentage"
    )
    pnt20: int | None = Field(None, ge=0, description="Punts inside 20")
    in20_pct: Decimal | None = Field(
        None, ge=0, le=100, description="Inside 20 percentage"
    )
    blck: int | None = Field(None, ge=0, description="Blocked punts")
    awards: str | None = Field(None, max_length=128, description="Awards")


class PuntingStatsResponse(PuntingStatsCreate):
    """DTO for punting stats response."""

    id: int = Field(..., description="Record ID")

    model_config = ConfigDict(from_attributes=True)
