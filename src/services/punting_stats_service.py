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
from src.entities.punting_stats import PuntingStats
from src.repositories.punting_stats_repo import PuntingStatsRepository
from src.dtos.punting_stats_dto import PuntingStatsCreate

logger = logging.getLogger(__name__)

COLUMN_MAP = {
    "ranker": ("rk", to_int),
    "player": ("player_name", clean_player_name),
    "age": ("age", to_int),
    "team": ("tm", clean_value),
    "pos": ("pos", clean_value),
    "g": ("g", to_int),
    "gs": ("gs", to_int),
    "punt": ("pnt", to_int),
    "punt_yds": ("yds", to_int),
    "punt_yds_per_punt": ("ypp", to_decimal),
    "punt_ret_yds": ("ret_yds", to_int),
    "punt_net_yds": ("net_yds", to_int),
    "punt_net_yds_per_punt": ("ny_pa", to_decimal),
    "punt_long": ("lng", to_int),
    "punt_touchback": ("tb", to_int),
    "punt_touchback_perc": ("tb_pct", to_decimal),
    "punt_inside_20": ("pnt20", to_int),
    "punt_inside_20_perc": ("in20_pct", to_decimal),
    "punt_blocked": ("blck", to_int),
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
        rows = fetch_and_parse_table(season, "punting", "punting.htm")
        parsed = parse_rows(rows, season)

        repo = PuntingStatsRepository(db)
        saved = []
        for row in parsed:
            dto = PuntingStatsCreate(**row)
            obj = PuntingStats(**dto.model_dump())
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
