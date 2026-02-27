import asyncio
import logging

from bs4 import Tag
from sqlalchemy.orm import Session

from src.core.scraper_utils import (
    clean_value,
    fetch_page,
    find_pfr_table,
    retry_with_backoff,
)
from src.dtos.rushing_stats_dto import RushingStatsCreate
from src.entities.rushing_stats import RushingStats
from src.repositories.rushing_stats_repo import RushingStatsRepository

logger = logging.getLogger(__name__)

PFR_URL_TEMPLATE = "https://www.pro-football-reference.com/years/{season}/rushing.htm"
PFR_TABLE_ID = "rushing"

COLUMN_MAP = {
    "player": "player_name",
    "age": "age",
    "team": "tm",
    "pos": "pos",
    "g": "g",
    "gs": "gs",
    "rush_att": "att",
    "rush_yds": "yds",
    "rush_td": "td",
    "rush_first_down": "first_downs",
    "rush_success_rate": "succ_pct",
    "rush_long": "lng",
    "rush_yds_per_att": "ypa",
    "rush_yds_per_g": "ypg",
    "rush_att_per_g": "apg",
    "fumbles": "fmb",
    "awards": "awards",
}


def get_dataframe(season: int) -> list[dict]:
    url = PFR_URL_TEMPLATE.format(season=season)
    page_source = retry_with_backoff(fetch_page, url, url=url)
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
        repo = RushingStatsRepository(db)

        saved = []
        for row in parsed:
            dto = RushingStatsCreate(**row)
            obj = RushingStats(**dto.model_dump())
            saved_obj = repo.create(obj, commit=False)
            saved.append(saved_obj)

        db.commit()
        return saved

    finally:
        if own_session:
            db.close()
