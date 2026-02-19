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
from src.entities.scoring_stats import ScoringStats
from src.repositories.scoring_stats_repo import ScoringStatsRepository
from src.dtos.scoring_stats_dto import ScoringStatsCreate

logger = logging.getLogger(__name__)

PFR_URL_TEMPLATE = "https://www.pro-football-reference.com/years/{season}/scoring.htm"
PFR_TABLE_ID = "scoring"

COLUMN_MAP = {
    "player": "player_name",
    "age": "age",
    "team": "tm",
    "pos": "pos",
    "g": "g",
    "gs": "gs",
    "rush_td": "rush_td",
    "rec_td": "rec_td",
    "punt_ret_td": "pr_td",
    "kick_ret_td": "kr_td",
    "fumbles_rec_td": "fr_td",
    "def_int_td": "int_td",
    "scoring_oth_td": "oth_td",
    "all_td": "all_td",
    "two_pt_md": "two_pm",
    "def_two_pt_md": "d2p",
    "xpm": "xpm",
    "xpa": "xpa",
    "fgm": "fgm",
    "fga": "fga",
    "safety_md": "sfty",
    "scoring": "pts",
    "pts_per_g": "pts_pg",
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
        repo = ScoringStatsRepository(db)

        saved = []
        for row in parsed:
            dto = ScoringStatsCreate(**row)
            obj = ScoringStats(**dto.model_dump())
            saved_obj = repo.create(obj, commit=False)
            saved.append(saved_obj)

        db.commit()
        return saved

    finally:
        db.close()
