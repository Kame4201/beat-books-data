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
from src.entities.scoring_stats import ScoringStats
from src.repositories.scoring_stats_repo import ScoringStatsRepository
from src.dtos.scoring_stats_dto import ScoringStatsCreate

logger = logging.getLogger(__name__)

COLUMN_MAP = {
    "ranker": ("rk", to_int),
    "player": ("player_name", clean_player_name),
    "age": ("age", to_int),
    "team": ("tm", clean_value),
    "pos": ("pos", clean_value),
    "g": ("g", to_int),
    "gs": ("gs", to_int),
    "rush_td": ("rush_td", to_int),
    "rec_td": ("rec_td", to_int),
    "punt_ret_td": ("pr_td", to_int),
    "kick_ret_td": ("kr_td", to_int),
    "fumbles_rec_td": ("fr_td", to_int),
    "def_int_td": ("int_td", to_int),
    "other_td": ("oth_td", to_int),
    "all_td": ("all_td", to_int),
    "two_pt_md": ("two_pm", to_int),
    "def_two_pt_md": ("d2p", to_int),
    "xpm": ("xpm", to_int),
    "xpa": ("xpa", to_int),
    "fgm": ("fgm", to_int),
    "fga": ("fga", to_int),
    "safety_md": ("sfty", to_int),
    "points": ("pts", to_int),
    "pts_per_g": ("pts_pg", to_decimal),
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
        rows = fetch_and_parse_table(season, "scoring", "scoring.htm")
        parsed = parse_rows(rows, season)

        repo = ScoringStatsRepository(db)
        saved = []
        for row in parsed:
            dto = ScoringStatsCreate(**row)
            obj = ScoringStats(**dto.model_dump())
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
