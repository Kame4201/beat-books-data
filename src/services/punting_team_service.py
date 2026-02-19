"""Team-aggregate punting stats from PFR punting.htm page."""

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
from src.entities.punting import Punting
from src.repositories.punting_repo import PuntingRepository
from src.dtos.punting_dto import PuntingCreate

logger = logging.getLogger(__name__)

COLUMN_MAP = {
    "ranker": ("rk", to_int),
    "team": ("tm", clean_value),
    "g": ("g", to_int),
    "punt": ("pnt", to_int),
    "punt_yds": ("yds", to_int),
    "punt_yds_per_punt": ("ypp", to_decimal),
    "punt_ret_yds": ("retyds", to_int),
    "punt_net_yds": ("net", to_int),
    "punt_net_yds_per_punt": ("nyp", to_decimal),
    "punt_long": ("lng", to_int),
    "punt_touchback": ("tb", to_int),
    "punt_touchback_perc": ("tb_pct", to_decimal),
    "punt_inside_20": ("in20", to_int),
    "punt_inside_20_perc": ("in20_pct", to_decimal),
    "punt_blocked": ("blck", to_int),
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
        url = build_pfr_url(season, "punting.htm")
        logger.info("Fetching team punting stats from %s", url)
        html = fetch_html(url)

        for table_id in ("team_punting", "team_stats"):
            try:
                table = find_table(html, table_id)
                break
            except ValueError:
                continue
        else:
            raise ValueError(
                "Could not find team punting table on punting.htm. "
                "Tried: team_punting, team_stats"
            )

        rows = parse_table_rows(table)
        parsed = parse_rows(rows, season)

        repo = PuntingRepository(db)
        saved = []
        for row in parsed:
            dto = PuntingCreate(**row)
            obj = Punting(**dto.model_dump())
            saved_obj = repo.upsert(
                obj, unique_fields={"tm": dto.tm, "season": dto.season}, commit=False
            )
            saved.append(saved_obj)

        db.commit()
        return {"status": "success", "rows_saved": len(saved), "season": season}
    finally:
        db.close()
