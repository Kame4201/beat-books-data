"""
DTOs for team kicking operations.
"""
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field


class KickingCreate(BaseModel):
    """DTO for creating team kicking records."""
    season: int = Field(..., ge=1920, le=2100, description="Season year")

    rk: Optional[int] = Field(None, ge=0, description="Rank")
    tm: str = Field(..., min_length=1, max_length=64, description="Team name")
    g: Optional[int] = Field(None, ge=0, description="Games played")

    fga_0_19: Optional[int] = Field(None, ge=0, description="FG attempts 0-19 yards")
    fgm_0_19: Optional[int] = Field(None, ge=0, description="FG made 0-19 yards")
    fga_20_29: Optional[int] = Field(None, ge=0, description="FG attempts 20-29 yards")
    fgm_20_29: Optional[int] = Field(None, ge=0, description="FG made 20-29 yards")
    fga_30_39: Optional[int] = Field(None, ge=0, description="FG attempts 30-39 yards")
    fgm_30_39: Optional[int] = Field(None, ge=0, description="FG made 30-39 yards")
    fga_40_49: Optional[int] = Field(None, ge=0, description="FG attempts 40-49 yards")
    fgm_40_49: Optional[int] = Field(None, ge=0, description="FG made 40-49 yards")
    fga_50_plus: Optional[int] = Field(None, ge=0, description="FG attempts 50+ yards")
    fgm_50_plus: Optional[int] = Field(None, ge=0, description="FG made 50+ yards")

    fga: Optional[int] = Field(None, ge=0, description="Total FG attempts")
    fgm: Optional[int] = Field(None, ge=0, description="Total FG made")

    lng: Optional[int] = Field(None, ge=0, description="Longest field goal")
    fg_pct: Optional[Decimal] = Field(None, ge=0, le=100, description="FG percentage")
    xpa: Optional[int] = Field(None, ge=0, description="Extra point attempts")
    xpm: Optional[int] = Field(None, ge=0, description="Extra points made")
    xp_pct: Optional[Decimal] = Field(None, ge=0, le=100, description="Extra point percentage")

    ko: Optional[int] = Field(None, ge=0, description="Kickoffs")
    ko_yds: Optional[int] = Field(None, ge=0, description="Kickoff yards")
    tb: Optional[int] = Field(None, ge=0, description="Touchbacks")
    tb_pct: Optional[Decimal] = Field(None, ge=0, le=100, description="Touchback percentage")
    ko_avg: Optional[Decimal] = Field(None, ge=0, description="Kickoff average")


class KickingResponse(KickingCreate):
    """DTO for team kicking response."""
    id: int = Field(..., description="Record ID")

    class Config:
        from_attributes = True
