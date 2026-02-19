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
from src.entities.rushing_stats import RushingStats
from src.repositories.rushing_stats_repo import RushingStatsRepository
from src.dtos.rushing_stats_dto import RushingStatsCreate

logger = logging.getLogger(__name__)

COLUMN_MAP = {
    "ranker": ("rk", to_int),
    "player": ("player_name", clean_player_name),
    "age": ("age", to_int),
    "team": ("tm", clean_value),
    "pos": ("pos", clean_value),
    "g": ("g", to_int),
    "gs": ("gs", to_int),
    "rush_att": ("att", to_int),
    "rush_yds": ("yds", to_int),
    "rush_td": ("td", to_int),
    "rush_first_down": ("first_downs", to_int),
    "rush_success_rate": ("succ_pct", to_decimal),
    "rush_long": ("lng", to_int),
    "rush_yds_per_att": ("ypa", to_decimal),
    "rush_yds_per_g": ("ypg", to_decimal),
    "rush_att_per_g": ("apg", to_decimal),
    "fumbles": ("fmb", to_int),
    "awards": ("awards", clean_value),
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
        rows = fetch_and_parse_table(season, "rushing", "rushing.htm")
        parsed = parse_rows(rows, season)

        repo = RushingStatsRepository(db)
        saved = []
        for row in parsed:
            dto = RushingStatsCreate(**row)
            obj = RushingStats(**dto.model_dump())
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
