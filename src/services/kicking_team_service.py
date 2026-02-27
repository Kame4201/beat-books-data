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
from src.dtos.kicking_dto import KickingCreate
from src.entities.kicking import Kicking
from src.repositories.kicking_repo import KickingRepository

logger = logging.getLogger(__name__)

PFR_URL_TEMPLATE = "https://www.pro-football-reference.com/years/{season}/kicking.htm"
PFR_TABLE_ID = "kicking"

COLUMN_MAP = {
    "team": "tm",
    "g": "g",
    "fga1": "fga_0_19",
    "fgm1": "fgm_0_19",
    "fga2": "fga_20_29",
    "fgm2": "fgm_20_29",
    "fga3": "fga_30_39",
    "fgm3": "fgm_30_39",
    "fga4": "fga_40_49",
    "fgm4": "fgm_40_49",
    "fga5": "fga_50_plus",
    "fgm5": "fgm_50_plus",
    "fga": "fga",
    "fgm": "fgm",
    "fg_long": "lng",
    "fg_perc": "fg_pct",
    "xpa": "xpa",
    "xpm": "xpm",
    "xp_perc": "xp_pct",
    "kickoffs": "ko",
    "kickoffs_yds": "ko_yds",
    "kickoffs_touchback": "tb",
    "kickoffs_touchback_perc": "tb_pct",
    "kickoffs_avg_yds": "ko_avg",
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

        # Team-level table: keyed by team
        tm_cell = tr.find("td", {"data-stat": "team"})
        if not tm_cell or not tm_cell.text.strip():
            continue

        row = {}
        for cell in cells:
            data_stat = cell.get("data-stat")
            if data_stat and data_stat in COLUMN_MAP:
                row[COLUMN_MAP[data_stat]] = clean_value(cell.text.strip())

        # Extract rank from th if present
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
        repo = KickingRepository(db)

        saved = []
        for row in parsed:
            dto = KickingCreate(**row)
            obj = Kicking(**dto.model_dump())
            saved_obj = repo.create(obj, commit=False)
            saved.append(saved_obj)

        db.commit()
        return saved

    finally:
        if own_session:
            db.close()
