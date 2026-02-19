"""Team-aggregate kicking stats from PFR kicking.htm page."""

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
from src.entities.kicking import Kicking
from src.repositories.kicking_repo import KickingRepository
from src.dtos.kicking_dto import KickingCreate

logger = logging.getLogger(__name__)

COLUMN_MAP = {
    "ranker": ("rk", to_int),
    "team": ("tm", clean_value),
    "g": ("g", to_int),
    "fga1": ("fga_0_19", to_int),
    "fgm1": ("fgm_0_19", to_int),
    "fga2": ("fga_20_29", to_int),
    "fgm2": ("fgm_20_29", to_int),
    "fga3": ("fga_30_39", to_int),
    "fgm3": ("fgm_30_39", to_int),
    "fga4": ("fga_40_49", to_int),
    "fgm4": ("fgm_40_49", to_int),
    "fga5": ("fga_50_plus", to_int),
    "fgm5": ("fgm_50_plus", to_int),
    "fga": ("fga", to_int),
    "fgm": ("fgm", to_int),
    "fg_long": ("lng", to_int),
    "fg_perc": ("fg_pct", to_decimal),
    "xpa": ("xpa", to_int),
    "xpm": ("xpm", to_int),
    "xp_perc": ("xp_pct", to_decimal),
    "kickoffs": ("ko", to_int),
    "kickoff_yds": ("ko_yds", to_int),
    "touchbacks": ("tb", to_int),
    "tb_perc": ("tb_pct", to_decimal),
    "kickoff_avg": ("ko_avg", to_decimal),
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
        url = build_pfr_url(season, "kicking.htm")
        logger.info("Fetching team kicking stats from %s", url)
        html = fetch_html(url)

        # Try team-level table first, fall back to team_stats
        for table_id in ("team_kicking", "team_stats"):
            try:
                table = find_table(html, table_id)
                break
            except ValueError:
                continue
        else:
            raise ValueError(
                "Could not find team kicking table on kicking.htm. "
                "Tried: team_kicking, team_stats"
            )

        rows = parse_table_rows(table)
        parsed = parse_rows(rows, season)

        repo = KickingRepository(db)
        saved = []
        for row in parsed:
            dto = KickingCreate(**row)
            obj = Kicking(**dto.model_dump())
            saved_obj = repo.upsert(
                obj, unique_fields={"tm": dto.tm, "season": dto.season}, commit=False
            )
            saved.append(saved_obj)

        db.commit()
        return {"status": "success", "rows_saved": len(saved), "season": season}
    finally:
        db.close()
