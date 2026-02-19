"""Team-aggregate return stats from PFR returns.htm page."""

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
from src.entities.returns import TeamReturns
from src.repositories.returns_repo import ReturnsRepository
from src.dtos.returns_dto import TeamReturnsCreate

logger = logging.getLogger(__name__)

COLUMN_MAP = {
    "ranker": ("rk", to_int),
    "team": ("tm", clean_value),
    "g": ("g", to_int),
    "punt_ret": ("ret_punt", to_int),
    "punt_ret_yds": ("yds_punt", to_int),
    "punt_ret_td": ("td_punt", to_int),
    "punt_ret_long": ("lng_punt", to_int),
    "punt_ret_yds_per_ret": ("ypr_punt", to_decimal),
    "kick_ret": ("ret_kick", to_int),
    "kick_ret_yds": ("yds_kick", to_int),
    "kick_ret_td": ("td_kick", to_int),
    "kick_ret_long": ("lng_kick", to_int),
    "kick_ret_yds_per_ret": ("ypr_kick", to_decimal),
    "all_purpose_yds": ("apyd", to_int),
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
        url = build_pfr_url(season, "returns.htm")
        logger.info("Fetching team return stats from %s", url)
        html = fetch_html(url)

        for table_id in ("team_returns", "team_stats"):
            try:
                table = find_table(html, table_id)
                break
            except ValueError:
                continue
        else:
            raise ValueError(
                "Could not find team returns table on returns.htm. "
                "Tried: team_returns, team_stats"
            )

        rows = parse_table_rows(table)
        parsed = parse_rows(rows, season)

        repo = ReturnsRepository(db)
        saved = []
        for row in parsed:
            dto = TeamReturnsCreate(**row)
            obj = TeamReturns(**dto.model_dump())
            saved_obj = repo.upsert(
                obj, unique_fields={"tm": dto.tm, "season": dto.season}, commit=False
            )
            saved.append(saved_obj)

        db.commit()
        return {"status": "success", "rows_saved": len(saved), "season": season}
    finally:
        db.close()
