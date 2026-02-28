"""
DTOs for team kicking operations.
"""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class KickingCreate(BaseModel):
    """DTO for creating team kicking records."""

    season: int = Field(..., ge=1920, le=2100, description="Season year")

    rk: int | None = Field(None, ge=0, description="Rank")
    tm: str = Field(..., min_length=1, max_length=64, description="Team name")
    g: int | None = Field(None, ge=0, description="Games played")

    fga_0_19: int | None = Field(None, ge=0, description="FG attempts 0-19 yards")
    fgm_0_19: int | None = Field(None, ge=0, description="FG made 0-19 yards")
    fga_20_29: int | None = Field(None, ge=0, description="FG attempts 20-29 yards")
    fgm_20_29: int | None = Field(None, ge=0, description="FG made 20-29 yards")
    fga_30_39: int | None = Field(None, ge=0, description="FG attempts 30-39 yards")
    fgm_30_39: int | None = Field(None, ge=0, description="FG made 30-39 yards")
    fga_40_49: int | None = Field(None, ge=0, description="FG attempts 40-49 yards")
    fgm_40_49: int | None = Field(None, ge=0, description="FG made 40-49 yards")
    fga_50_plus: int | None = Field(None, ge=0, description="FG attempts 50+ yards")
    fgm_50_plus: int | None = Field(None, ge=0, description="FG made 50+ yards")

    fga: int | None = Field(None, ge=0, description="Total FG attempts")
    fgm: int | None = Field(None, ge=0, description="Total FG made")

    lng: int | None = Field(None, ge=0, description="Longest field goal")
    fg_pct: Decimal | None = Field(None, ge=0, le=100, description="FG percentage")
    xpa: int | None = Field(None, ge=0, description="Extra point attempts")
    xpm: int | None = Field(None, ge=0, description="Extra points made")
    xp_pct: Decimal | None = Field(
        None, ge=0, le=100, description="Extra point percentage"
    )

    ko: int | None = Field(None, ge=0, description="Kickoffs")
    ko_yds: int | None = Field(None, ge=0, description="Kickoff yards")
    tb: int | None = Field(None, ge=0, description="Touchbacks")
    tb_pct: Decimal | None = Field(
        None, ge=0, le=100, description="Touchback percentage"
    )
    ko_avg: Decimal | None = Field(None, ge=0, description="Kickoff average")


class KickingResponse(KickingCreate):
    """DTO for team kicking response."""

    id: int = Field(..., description="Record ID")

    model_config = ConfigDict(from_attributes=True)
