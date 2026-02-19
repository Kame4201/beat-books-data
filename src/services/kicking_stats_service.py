import logging

from sqlalchemy.orm import Session

from src.core.database import SessionLocal
from src.core.pfr_scraper import (
    fetch_and_parse_table,
    clean_value,
    clean_player_name,
    to_int,
    to_decimal,
)
from src.entities.kicking_stats import KickingStats
from src.repositories.kicking_stats_repo import KickingStatsRepository
from src.dtos.kicking_stats_dto import KickingStatsCreate

logger = logging.getLogger(__name__)

COLUMN_MAP = {
    "ranker": ("rk", to_int),
    "player": ("player_name", clean_player_name),
    "age": ("age", to_int),
    "team": ("tm", clean_value),
    "pos": ("pos", clean_value),
    "g": ("g", to_int),
    "gs": ("gs", to_int),
    "fga1": ("fga_0_19", to_int),
    "fgm1": ("fgm_0_19", to_int),
    "fga2": ("fga_20_29", to_int),
    "fgm2": ("fgm_20_29", to_int),
    "fga3": ("fga_30_39", to_int),
    "fgm3": ("fgm_30_39", to_int),
    "fga4": ("fga_40_49", to_int),
    "fgm4": ("fgm_40_49", to_int),
    "fga5": ("fga_50_plus", to_int),
    "fgm5": ("fgm_50_plus", to_int),
    "fga": ("fga", to_int),
    "fgm": ("fgm", to_int),
    "fg_long": ("lng", to_int),
    "fg_perc": ("fg_pct", to_decimal),
    "xpa": ("xpa", to_int),
    "xpm": ("xpm", to_int),
    "xp_perc": ("xp_pct", to_decimal),
    "kickoffs": ("ko", to_int),
    "kickoff_yds": ("ko_yds", to_int),
    "touchbacks": ("tb", to_int),
    "tb_perc": ("tb_pct", to_decimal),
    "kickoff_avg": ("ko_avg", to_decimal),
}


def parse_rows(rows: list[dict], season: int) -> list[dict]:
    parsed = []
    for row in rows:
        name = clean_player_name(row.get("player"))
        tm = clean_value(row.get("team"))
        if not name or not tm:
            continue
        rec: dict = {"season": season}
        for pfr_key, (field, converter) in COLUMN_MAP.items():
            rec[field] = converter(row.get(pfr_key))
        parsed.append(rec)
    return parsed


async def scrape_and_store(season: int):
    db: Session = SessionLocal()
    try:
        rows = fetch_and_parse_table(season, "kicking", "kicking.htm")
        parsed = parse_rows(rows, season)

        repo = KickingStatsRepository(db)
        saved = []
        for row in parsed:
            dto = KickingStatsCreate(**row)
            obj = KickingStats(**dto.model_dump())
            saved_obj = repo.upsert(
                obj,
                unique_fields={
                    "player_name": dto.player_name,
                    "season": dto.season,
                    "tm": dto.tm,
                },
                commit=False,
            )
            saved.append(saved_obj)

        db.commit()
        return {"status": "success", "rows_saved": len(saved), "season": season}
    finally:
        db.close()
