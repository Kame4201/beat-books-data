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
from src.entities.passing_stats import PassingStats
from src.repositories.passing_stats_repo import PassingStatsRepository
from src.dtos.passing_stats_dto import PassingStatsCreate

logger = logging.getLogger(__name__)

COLUMN_MAP = {
    "ranker": ("rk", to_int),
    "player": ("player_name", clean_player_name),
    "age": ("age", to_int),
    "team": ("tm", clean_value),
    "pos": ("pos", clean_value),
    "g": ("g", to_int),
    "gs": ("gs", to_int),
    "qb_rec": ("qb_rec", clean_value),
    "pass_cmp": ("cmp", to_int),
    "pass_att": ("att", to_int),
    "pass_cmp_perc": ("cmp_pct", to_decimal),
    "pass_yds": ("yds", to_int),
    "pass_td": ("td", to_int),
    "pass_td_perc": ("td_pct", to_decimal),
    "pass_int": ("ints", to_int),
    "pass_int_perc": ("int_pct", to_decimal),
    "pass_first_down": ("first_downs", to_int),
    "pass_success_rate": ("succ_pct", to_decimal),
    "pass_long": ("lng", to_int),
    "pass_yds_per_att": ("ypa", to_decimal),
    "pass_adj_yds_per_att": ("ay_pa", to_decimal),
    "pass_yds_per_cmp": ("ypc", to_decimal),
    "pass_yds_per_g": ("ypg", to_decimal),
    "pass_rating": ("rate", to_decimal),
    "qbr": ("qbr", to_decimal),
    "pass_sacked": ("sk", to_int),
    "pass_sacked_yds": ("yds_sack", to_int),
    "pass_sacked_perc": ("sk_pct", to_decimal),
    "pass_net_yds_per_att": ("ny_pa", to_decimal),
    "pass_adj_net_yds_per_att": ("any_pa", to_decimal),
    "comebacks": ("four_qc", to_int),
    "gwd": ("gwd", to_int),
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
        rows = fetch_and_parse_table(season, "passing", "passing.htm")
        parsed = parse_rows(rows, season)

        repo = PassingStatsRepository(db)
        saved = []
        for row in parsed:
            dto = PassingStatsCreate(**row)
            obj = PassingStats(**dto.model_dump())
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
