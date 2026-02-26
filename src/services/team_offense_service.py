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
from src.dtos.team_offense_dto import TeamOffenseCreate
from src.entities.team_offense import TeamOffense
from src.repositories.team_offense_repo import TeamOffenseRepository

logger = logging.getLogger(__name__)

PFR_URL_TEMPLATE = "https://www.pro-football-reference.com/years/{season}/"
PFR_TABLE_ID = "team_stats"

COLUMN_MAP = {
    "team": "tm",
    "g": "g",
    "points": "pf",
    "total_yards": "yds",
    "plays_offense": "ply",
    "yds_per_play_offense": "ypp",
    "turnovers": "turnovers",
    "fumbles_lost": "fl",
    "first_down": "firstd_total",
    "pass_cmp": "cmp",
    "pass_att": "att_pass",
    "pass_yds": "yds_pass",
    "pass_td": "td_pass",
    "pass_int": "ints",
    "pass_net_yds_per_att": "nypa",
    "pass_fd": "firstd_pass",
    "rush_att": "att_rush",
    "rush_yds": "yds_rush",
    "rush_td": "td_rush",
    "rush_yds_per_att": "ypa",
    "rush_fd": "firstd_rush",
    "penalties": "pen",
    "penalties_yds": "yds_pen",
    "pen_fd": "firstpy",
    "score_pct": "sc_pct",
    "turnover_pct": "to_pct",
    "exp_pts_tot": "opea",
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

        tm_cell = tr.find("td", {"data-stat": "team"})
        if not tm_cell or not tm_cell.text.strip():
            continue

        row = {}
        for cell in cells:
            data_stat = cell.get("data-stat")
            if data_stat and data_stat in COLUMN_MAP:
                row[COLUMN_MAP[data_stat]] = clean_value(cell.text.strip())

        row["season"] = season
        rows.append(row)

    return rows


async def scrape_and_store_team_offense(season: int, db: Session | None = None):
    from src.core.database import SessionLocal

    own_session = db is None
    if own_session:
        db = SessionLocal()

    try:
        parsed = await asyncio.to_thread(get_dataframe, season)
        repo = TeamOffenseRepository(db)

        saved = []
        for row in parsed:
            dto = TeamOffenseCreate(**row)
            obj = TeamOffense(**dto.model_dump())
            saved_obj = repo.create(obj, commit=False)
            saved.append(saved_obj)

        db.commit()
        return saved

    finally:
        if own_session:
            db.close()
