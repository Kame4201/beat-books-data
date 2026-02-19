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
from src.entities.receiving_stats import ReceivingStats
from src.repositories.receiving_stats_repo import ReceivingStatsRepository
from src.dtos.receiving_stats_dto import ReceivingStatsCreate

logger = logging.getLogger(__name__)

COLUMN_MAP = {
    "ranker": ("rk", to_int),
    "player": ("player_name", clean_player_name),
    "age": ("age", to_int),
    "team": ("tm", clean_value),
    "pos": ("pos", clean_value),
    "g": ("g", to_int),
    "gs": ("gs", to_int),
    "targets": ("tgt", to_int),
    "rec": ("rec", to_int),
    "rec_yds": ("yds", to_int),
    "rec_yds_per_rec": ("ypr", to_decimal),
    "rec_td": ("td", to_int),
    "rec_first_down": ("first_downs", to_int),
    "rec_success_rate": ("succ_pct", to_decimal),
    "rec_long": ("lng", to_int),
    "rec_per_g": ("rpg", to_decimal),
    "rec_yds_per_g": ("ypg", to_decimal),
    "catch_pct": ("catch_pct", to_decimal),
    "rec_yds_per_tgt": ("ypt", to_decimal),
    "fumbles": ("fmb", to_int),
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
        rows = fetch_and_parse_table(season, "receiving", "receiving.htm")
        parsed = parse_rows(rows, season)

        repo = ReceivingStatsRepository(db)
        saved = []
        for row in parsed:
            dto = ReceivingStatsCreate(**row)
            obj = ReceivingStats(**dto.model_dump())
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
