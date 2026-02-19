import logging

from bs4 import Tag
from sqlalchemy.orm import Session

from src.core.database import SessionLocal
from src.core.scraper_utils import (
    clean_value,
    fetch_page_with_selenium,
    find_pfr_table,
    retry_with_backoff,
)
from src.entities.punting_stats import PuntingStats
from src.repositories.punting_stats_repo import PuntingStatsRepository
from src.dtos.punting_stats_dto import PuntingStatsCreate

logger = logging.getLogger(__name__)

PFR_URL_TEMPLATE = "https://www.pro-football-reference.com/years/{season}/punting.htm"
PFR_TABLE_ID = "punting"

COLUMN_MAP = {
    "player": "player_name",
    "age": "age",
    "team": "tm",
    "pos": "pos",
    "g": "g",
    "gs": "gs",
    "punt": "pnt",
    "punt_yds": "yds",
    "punt_yds_per_punt": "ypp",
    "punt_return_yds": "ret_yds",
    "punt_net_yds": "net_yds",
    "punt_net_yds_per_punt": "ny_pa",
    "punt_long": "lng",
    "punt_touchback": "tb",
    "punt_touchback_perc": "tb_pct",
    "punt_inside_20": "pnt20",
    "punt_inside_20_perc": "in20_pct",
    "punt_blocked": "blck",
    "awards": "awards",
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

        if "player_name" in row and row["player_name"]:
            row["player_name"] = row["player_name"].rstrip("*+")

        rk_cell = tr.find("th", {"data-stat": "ranker"})
        if rk_cell and rk_cell.text.strip():
            row["rk"] = clean_value(rk_cell.text.strip())

        row["season"] = season
        rows.append(row)

    return rows


async def scrape_and_store(season: int):
    db: Session = SessionLocal()

    try:
        parsed = get_dataframe(season)
        repo = PuntingStatsRepository(db)

        saved = []
        for row in parsed:
            dto = PuntingStatsCreate(**row)
            obj = PuntingStats(**dto.model_dump())
            saved_obj = repo.create(obj, commit=False)
            saved.append(saved_obj)

        db.commit()
        return saved

    finally:
        db.close()
