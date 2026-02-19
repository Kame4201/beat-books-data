import logging

from sqlalchemy.orm import Session

from src.core.database import SessionLocal
from src.core.pfr_scraper import (
    build_pfr_url,
    fetch_html,
    find_table,
    parse_table_rows,
    clean_value,
    to_int,
    to_decimal,
)
from src.entities.standings import Standings
from src.repositories.standings_repo import StandingsRepository
from src.dtos.standings_dto import StandingsCreate

logger = logging.getLogger(__name__)

COLUMN_MAP = {
    "team": ("tm", clean_value),
    "wins": ("w", to_int),
    "losses": ("l", to_int),
    "ties": ("t", to_int),
    "win_loss_perc": ("win_pct", to_decimal),
    "points": ("pf", to_int),
    "points_opp": ("pa", to_int),
    "points_diff": ("pd", to_int),
    "mov": ("mov", to_decimal),
    "sos_total": ("sos", to_decimal),
    "srs_total": ("srs", to_decimal),
    "srs_offense": ("osrs", to_decimal),
    "srs_defense": ("dsrs", to_decimal),
}


def parse_rows(rows: list[dict], season: int) -> list[dict]:
    parsed = []
    for row in rows:
        tm = clean_value(row.get("team"))
        if not tm:
            continue
        rec: dict = {"season": season}
        for pfr_key, (field, converter) in COLUMN_MAP.items():
            rec[field] = converter(row.get(pfr_key))
        parsed.append(rec)
    return parsed


async def scrape_and_store(season: int):
    db: Session = SessionLocal()
    try:
        url = build_pfr_url(season)
        logger.info("Fetching standings (AFC + NFC) from %s", url)
        html = fetch_html(url)

        all_rows: list[dict] = []
        for conf in ("AFC", "NFC"):
            table = find_table(html, conf)
            all_rows.extend(parse_table_rows(table))

        parsed = parse_rows(all_rows, season)

        repo = StandingsRepository(db)
        saved = []
        for row in parsed:
            dto = StandingsCreate(**row)
            obj = Standings(**dto.model_dump())
            saved_obj = repo.upsert(
                obj, unique_fields={"tm": dto.tm, "season": dto.season}, commit=False
            )
            saved.append(saved_obj)

        db.commit()
        return {"status": "success", "rows_saved": len(saved), "season": season}
    finally:
        db.close()
