import asyncio
import logging

from bs4 import Tag
from sqlalchemy.orm import Session

from src.core.scraper_utils import (
    clean_value,
    fetch_page_with_selenium,
    find_pfr_table,
    retry_with_backoff,
)
from src.entities.passing_stats import PassingStats
from src.repositories.passing_stats_repo import PassingStatsRepository
from src.dtos.passing_stats_dto import PassingStatsCreate

logger = logging.getLogger(__name__)

PFR_URL_TEMPLATE = "https://www.pro-football-reference.com/years/{season}/passing.htm"
PFR_TABLE_ID = "passing"

COLUMN_MAP = {
    "player": "player_name",
    "age": "age",
    "team": "tm",
    "pos": "pos",
    "g": "g",
    "gs": "gs",
    "qb_rec": "qb_rec",
    "pass_cmp": "cmp",
    "pass_att": "att",
    "pass_cmp_perc": "cmp_pct",
    "pass_yds": "yds",
    "pass_td": "td",
    "pass_td_perc": "td_pct",
    "pass_int": "ints",
    "pass_int_perc": "int_pct",
    "pass_first_down": "first_downs",
    "pass_success_rate": "succ_pct",
    "pass_long": "lng",
    "pass_yds_per_att": "ypa",
    "pass_adj_yds_per_att": "ay_pa",
    "pass_yds_per_cmp": "ypc",
    "pass_yds_per_g": "ypg",
    "pass_rating": "rate",
    "qbr": "qbr",
    "pass_sacked": "sk",
    "pass_sacked_yds": "yds_sack",
    "pass_sacked_perc": "sk_pct",
    "pass_net_yds_per_att": "ny_pa",
    "pass_adj_net_yds_per_att": "any_pa",
    "comebacks": "four_qc",
    "gwd": "gwd",
}


def get_dataframe(season: int) -> list[dict]:
    url = PFR_URL_TEMPLATE.format(season=season)
    page_source = retry_with_backoff(fetch_page_with_selenium, url, url=url)
    table = find_pfr_table(page_source, PFR_TABLE_ID)

    if table is None:
        raise Exception(f"Could not find {PFR_TABLE_ID} table")

    assert isinstance(table, Tag)

    rows = []
    for tr in table.find_all("tr"):
        if "class" in tr.attrs and "thead" in tr["class"]:
            continue

        cells = tr.find_all("td")
        if not cells:
            continue

        player_cell = tr.find("td", {"data-stat": "player"})
        if not player_cell or not player_cell.text.strip():
            continue

        row = {}
        for cell in cells:
            data_stat = cell.get("data-stat")
            if data_stat and data_stat in COLUMN_MAP:
                row[COLUMN_MAP[data_stat]] = clean_value(cell.text.strip())

        # Strip Pro Bowl (*) and All-Pro (+) markers from player names
        if "player_name" in row and row["player_name"]:
            row["player_name"] = row["player_name"].rstrip("*+")

        rk_cell = tr.find("th", {"data-stat": "ranker"})
        if rk_cell and rk_cell.text.strip():
            row["rk"] = clean_value(rk_cell.text.strip())

        row["season"] = season
        rows.append(row)

    return rows


async def scrape_and_store(season: int, db: Session | None = None):
    from src.core.database import SessionLocal

    own_session = db is None
    if own_session:
        db = SessionLocal()

    try:
        parsed = await asyncio.to_thread(get_dataframe, season)
        repo = PassingStatsRepository(db)

        saved = []
        for row in parsed:
            dto = PassingStatsCreate(**row)
            obj = PassingStats(**dto.model_dump())
            saved_obj = repo.create(obj, commit=False)
            saved.append(saved_obj)

        db.commit()
        return saved

    finally:
        if own_session:
            db.close()
