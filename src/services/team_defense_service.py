import logging

from sqlalchemy.orm import Session

from src.core.database import SessionLocal
from src.core.pfr_scraper import fetch_and_parse_table, clean_value, to_int, to_decimal
from src.entities.team_defense import TeamDefense
from src.repositories.team_defense_repo import TeamDefenseRepository
from src.dtos.team_defense_dto import TeamDefenseCreate

logger = logging.getLogger(__name__)

COLUMN_MAP = {
    "ranker": ("rk", to_int),
    "team": ("tm", clean_value),
    "g": ("g", to_int),
    "points": ("pa", to_int),
    "total_yds": ("yds", to_int),
    "plays": ("ply", to_int),
    "yds_per_play": ("ypp", to_decimal),
    "turnovers": ("turnovers", to_int),
    "fumbles_lost": ("fl", to_int),
    "first_down": ("firstd_total", to_int),
    "pass_cmp": ("cmp", to_int),
    "pass_att": ("att_pass", to_int),
    "pass_yds": ("yds_pass", to_int),
    "pass_td": ("td_pass", to_int),
    "pass_int": ("ints", to_int),
    "pass_net_yds_per_att": ("nypa", to_decimal),
    "pass_fd": ("firstd_pass", to_int),
    "rush_att": ("att_rush", to_int),
    "rush_yds": ("yds_rush", to_int),
    "rush_td": ("td_rush", to_int),
    "rush_yds_per_att": ("ypa", to_decimal),
    "rush_fd": ("firstd_rush", to_int),
    "penalties": ("pen", to_int),
    "penalties_yds": ("yds_pen", to_int),
    "pen_fd": ("firstpy", to_int),
    "score_pct": ("sc_pct", to_decimal),
    "turnover_pct": ("to_pct", to_decimal),
    "exp_pts_def": ("depa", to_decimal),
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
        rows = fetch_and_parse_table(season, "opp_stats")
        parsed = parse_rows(rows, season)

        repo = TeamDefenseRepository(db)
        saved = []
        for row in parsed:
            dto = TeamDefenseCreate(**row)
            obj = TeamDefense(**dto.model_dump())
            saved_obj = repo.upsert(
                obj, unique_fields={"tm": dto.tm, "season": dto.season}, commit=False
            )
            saved.append(saved_obj)

        db.commit()
        return {"status": "success", "rows_saved": len(saved), "season": season}
    finally:
        db.close()
