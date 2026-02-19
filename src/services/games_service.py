import logging
from datetime import date

from sqlalchemy.orm import Session

from src.core.database import SessionLocal
from src.core.pfr_scraper import (
    fetch_and_parse_table,
    clean_value,
    to_int,
)
from src.entities.games import Games
from src.repositories.games_repo import GamesRepository
from src.dtos.games_dto import GamesCreate

logger = logging.getLogger(__name__)


def _parse_date(raw: str):
    """Parse PFR date string (e.g. '2024-09-05') into a date object."""
    raw = clean_value(raw)
    if not raw:
        return None
    try:
        return date.fromisoformat(raw)
    except ValueError:
        return None


def parse_rows(rows: list[dict], season: int) -> list[dict]:
    parsed = []
    for row in rows:
        week = to_int(row.get("week_num"))
        winner = clean_value(row.get("winner"))
        loser = clean_value(row.get("loser"))
        if not winner or not loser:
            continue

        rec = {
            "season": season,
            "week": week,
            "game_day": clean_value(row.get("game_day_of_week")),
            "game_date": _parse_date(row.get("game_date", "")),
            "kickoff_time": clean_value(row.get("gametime")),
            "winner": winner,
            "loser": loser,
            "boxscore": clean_value(row.get("boxscore_word")),
            "pts_w": to_int(row.get("pts_win")),
            "pts_l": to_int(row.get("pts_lose")),
            "yds_w": to_int(row.get("yards_win")),
            "to_w": to_int(row.get("to_win")),
            "yds_l": to_int(row.get("yards_lose")),
            "to_l": to_int(row.get("to_lose")),
        }
        parsed.append(rec)
    return parsed


async def scrape_and_store(season: int):
    db: Session = SessionLocal()
    try:
        rows = fetch_and_parse_table(season, "games", "games.htm")
        parsed = parse_rows(rows, season)

        repo = GamesRepository(db)
        saved = []
        for row in parsed:
            dto = GamesCreate(**row)
            obj = Games(**dto.model_dump())
            saved_obj = repo.upsert(
                obj,
                unique_fields={
                    "season": dto.season,
                    "week": dto.week,
                    "winner": dto.winner,
                    "loser": dto.loser,
                },
                commit=False,
            )
            saved.append(saved_obj)

        db.commit()
        return {"status": "success", "rows_saved": len(saved), "season": season}
    finally:
        db.close()
