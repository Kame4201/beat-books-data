"""
DTOs for standings operations.
"""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class StandingsCreate(BaseModel):
    """DTO for creating standings records."""

    season: int = Field(..., ge=1920, le=2100, description="Season year")

    tm: str = Field(..., min_length=1, max_length=64, description="Team name")
    w: int | None = Field(None, ge=0, description="Wins")
    l: int | None = Field(None, ge=0, description="Losses")  # noqa: E741
    t: int | None = Field(None, ge=0, description="Ties")
    win_pct: Decimal | None = Field(None, ge=0, le=1, description="Win percentage")
    pf: int | None = Field(None, ge=0, description="Points for")
    pa: int | None = Field(None, ge=0, description="Points against")
    pd: int | None = Field(None, description="Point differential")
    mov: Decimal | None = Field(None, description="Margin of victory")
    sos: Decimal | None = Field(None, description="Strength of schedule")
    srs: Decimal | None = Field(None, description="Simple rating system")
    osrs: Decimal | None = Field(None, description="Offensive SRS")
    dsrs: Decimal | None = Field(None, description="Defensive SRS")


class StandingsResponse(StandingsCreate):
    """DTO for standings response."""

    id: int = Field(..., description="Record ID")

    model_config = ConfigDict(from_attributes=True)
