"""
DTOs for passing stats operations.
"""
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field


class PassingStatsCreate(BaseModel):
    """DTO for creating passing stats records."""
    season: int = Field(..., ge=1920, le=2100, description="Season year")

    rk: Optional[int] = Field(None, ge=0, description="Rank")
    player_name: str = Field(..., min_length=1, max_length=128, description="Player name")
    age: Optional[int] = Field(None, ge=0, description="Player age")
    tm: str = Field(..., min_length=1, max_length=64, description="Team name")
    pos: Optional[str] = Field(None, max_length=16, description="Position")

    g: Optional[int] = Field(None, ge=0, description="Games played")
    gs: Optional[int] = Field(None, ge=0, description="Games started")
    qb_rec: Optional[str] = Field(None, max_length=16, description="QB record")

    cmp: Optional[int] = Field(None, ge=0, description="Completions")
    att: Optional[int] = Field(None, ge=0, description="Attempts")
    cmp_pct: Optional[Decimal] = Field(None, ge=0, le=100, description="Completion percentage")
    yds: Optional[int] = Field(None, ge=0, description="Passing yards")
    td: Optional[int] = Field(None, ge=0, description="Touchdowns")
    td_pct: Optional[Decimal] = Field(None, ge=0, le=100, description="Touchdown percentage")
    ints: Optional[int] = Field(None, ge=0, description="Interceptions")
    int_pct: Optional[Decimal] = Field(None, ge=0, le=100, description="Interception percentage")
    first_downs: Optional[int] = Field(None, ge=0, description="First downs")
    succ_pct: Optional[Decimal] = Field(None, ge=0, le=100, description="Success percentage")
    lng: Optional[int] = Field(None, ge=0, description="Longest pass")
    ypa: Optional[Decimal] = Field(None, ge=0, description="Yards per attempt")
    ay_pa: Optional[Decimal] = Field(None, description="Adjusted yards per attempt")
    ypc: Optional[Decimal] = Field(None, ge=0, description="Yards per completion")
    ypg: Optional[Decimal] = Field(None, ge=0, description="Yards per game")
    rate: Optional[Decimal] = Field(None, ge=0, description="Passer rating")
    qbr: Optional[Decimal] = Field(None, ge=0, description="QB rating")
    sk: Optional[int] = Field(None, ge=0, description="Sacks")
    yds_sack: Optional[int] = Field(None, ge=0, description="Sack yards")
    sk_pct: Optional[Decimal] = Field(None, ge=0, le=100, description="Sack percentage")
    ny_pa: Optional[Decimal] = Field(None, description="Net yards per attempt")
    any_pa: Optional[Decimal] = Field(None, description="Adjusted net yards per attempt")
    four_qc: Optional[int] = Field(None, ge=0, description="Fourth quarter comebacks")
    gwd: Optional[int] = Field(None, ge=0, description="Game winning drives")


class PassingStatsResponse(PassingStatsCreate):
    """DTO for passing stats response."""
    id: int = Field(..., description="Record ID")

    class Config:
        from_attributes = True
