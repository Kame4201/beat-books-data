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
from src.dtos.defense_stats_dto import DefenseStatsCreate
from src.entities.defense_stats import DefenseStats
from src.repositories.defense_stats_repo import DefenseStatsRepository

logger = logging.getLogger(__name__)

PFR_URL_TEMPLATE = "https://www.pro-football-reference.com/years/{season}/defense.htm"
PFR_TABLE_ID = "defense"

COLUMN_MAP = {
    "player": "player_name",
    "age": "age",
    "team": "tm",
    "pos": "pos",
    "g": "g",
    "gs": "gs",
    "def_int": "ints",
    "def_int_yds": "int_yds",
    "def_int_td": "int_td",
    "def_int_long": "int_lng",
    "pass_defended": "pd",
    "fumbles_forced": "ff",
    "fumbles": "fmb",
    "fumbles_rec": "fr",
    "fumbles_rec_yds": "fr_yds",
    "fumbles_rec_td": "fr_td",
    "sacks": "sk",
    "tackles_combined": "comb",
    "tackles_solo": "solo",
    "tackles_assists": "ast",
    "tackles_loss": "tfl",
    "qb_hits": "qb_hits",
    "safety_md": "sfty",
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
        repo = DefenseStatsRepository(db)

        saved = []
        for row in parsed:
            dto = DefenseStatsCreate(**row)
            obj = DefenseStats(**dto.model_dump())
            saved_obj = repo.create(obj, commit=False)
            saved.append(saved_obj)

        db.commit()
        return saved

    finally:
        if own_session:
            db.close()
