"""
DTOs for team punting operations.
"""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PuntingCreate(BaseModel):
    """DTO for creating team punting records."""

    season: int = Field(..., ge=1920, le=2100, description="Season year")

    rk: int | None = Field(None, ge=0, description="Rank")
    tm: str = Field(..., min_length=1, max_length=64, description="Team name")
    g: int | None = Field(None, ge=0, description="Games played")

    pnt: int | None = Field(None, ge=0, description="Punts")
    yds: int | None = Field(None, ge=0, description="Punt yards")
    ypp: Decimal | None = Field(None, ge=0, description="Yards per punt")
    retyds: int | None = Field(None, ge=0, description="Return yards allowed")
    net: int | None = Field(None, ge=0, description="Net yards")
    nyp: Decimal | None = Field(None, ge=0, description="Net yards per punt")
    lng: int | None = Field(None, ge=0, description="Longest punt")
    tb: int | None = Field(None, ge=0, description="Touchbacks")
    tb_pct: Decimal | None = Field(
        None, ge=0, le=100, description="Touchback percentage"
    )
    in20: int | None = Field(None, ge=0, description="Punts inside 20")
    in20_pct: Decimal | None = Field(
        None, ge=0, le=100, description="Inside 20 percentage"
    )
    blck: int | None = Field(None, ge=0, description="Blocked punts")


class PuntingResponse(PuntingCreate):
    """DTO for team punting response."""

    id: int = Field(..., description="Record ID")

    model_config = ConfigDict(from_attributes=True)
