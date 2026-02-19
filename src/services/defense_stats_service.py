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
from src.entities.defense_stats import DefenseStats
from src.repositories.defense_stats_repo import DefenseStatsRepository
from src.dtos.defense_stats_dto import DefenseStatsCreate

logger = logging.getLogger(__name__)

COLUMN_MAP = {
    "ranker": ("rk", to_int),
    "player": ("player_name", clean_player_name),
    "age": ("age", to_int),
    "team": ("tm", clean_value),
    "pos": ("pos", clean_value),
    "g": ("g", to_int),
    "gs": ("gs", to_int),
    "def_int": ("ints", to_int),
    "def_int_yds": ("int_yds", to_int),
    "def_int_td": ("int_td", to_int),
    "def_int_long": ("int_lng", to_int),
    "pass_defended": ("pd", to_int),
    "fumbles_forced": ("ff", to_int),
    "fumbles": ("fmb", to_int),
    "fumbles_rec": ("fr", to_int),
    "fumbles_rec_yds": ("fr_yds", to_int),
    "fumbles_rec_td": ("fr_td", to_int),
    "sacks": ("sk", to_decimal),
    "tackles_combined": ("comb", to_int),
    "tackles_solo": ("solo", to_int),
    "tackles_assists": ("ast", to_int),
    "tackles_loss": ("tfl", to_int),
    "qb_hits": ("qb_hits", to_int),
    "safety_md": ("sfty", to_int),
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
        rows = fetch_and_parse_table(season, "defense", "defense.htm")
        parsed = parse_rows(rows, season)

        repo = DefenseStatsRepository(db)
        saved = []
        for row in parsed:
            dto = DefenseStatsCreate(**row)
            obj = DefenseStats(**dto.model_dump())
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
