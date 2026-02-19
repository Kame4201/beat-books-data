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
from src.entities.return_stats import ReturnStats
from src.repositories.return_stats_repo import ReturnStatsRepository
from src.dtos.return_stats_dto import ReturnStatsCreate

logger = logging.getLogger(__name__)

COLUMN_MAP = {
    "ranker": ("rk", to_int),
    "player": ("player_name", clean_player_name),
    "age": ("age", to_int),
    "team": ("tm", clean_value),
    "pos": ("pos", clean_value),
    "g": ("g", to_int),
    "gs": ("gs", to_int),
    "punt_ret": ("pr", to_int),
    "punt_ret_yds": ("pr_yds", to_int),
    "punt_ret_td": ("pr_td", to_int),
    "punt_ret_long": ("pr_lng", to_int),
    "punt_ret_yds_per_ret": ("pr_ypr", to_decimal),
    "kick_ret": ("kr", to_int),
    "kick_ret_yds": ("kr_yds", to_int),
    "kick_ret_td": ("kr_td", to_int),
    "kick_ret_long": ("kr_lng", to_int),
    "kick_ret_yds_per_ret": ("kr_ypr", to_decimal),
    "all_purpose_yds": ("apyd", to_int),
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
        rows = fetch_and_parse_table(season, "returns", "returns.htm")
        parsed = parse_rows(rows, season)

        repo = ReturnStatsRepository(db)
        saved = []
        for row in parsed:
            dto = ReturnStatsCreate(**row)
            obj = ReturnStats(**dto.model_dump())
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
