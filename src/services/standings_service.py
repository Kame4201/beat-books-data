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
from src.dtos.standings_dto import StandingsCreate
from src.entities.standings import Standings
from src.repositories.standings_repo import StandingsRepository

logger = logging.getLogger(__name__)

PFR_URL_TEMPLATE = "https://www.pro-football-reference.com/years/{season}/"
PFR_TABLE_IDS = ["AFC", "NFC"]

COLUMN_MAP = {
    "team": "tm",
    "wins": "w",
    "losses": "l",
    "ties": "t",
    "win_loss_perc": "win_pct",
    "points": "pf",
    "points_opp": "pa",
    "points_diff": "pd",
    "mov": "mov",
    "sos_total": "sos",
    "srs_total": "srs",
    "srs_offense": "osrs",
    "srs_defense": "dsrs",
}


def _parse_table(table: Tag, season: int) -> list[dict]:
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

        # Clean team name - remove special characters like * (playoff indicator)
        if "tm" in row and row["tm"]:
            row["tm"] = row["tm"].rstrip("*+")

        row["season"] = season
        rows.append(row)

    return rows


def get_dataframe(season: int) -> list[dict]:
    url = PFR_URL_TEMPLATE.format(season=season)
    page_source = retry_with_backoff(fetch_page_with_selenium, url, url=url)

    all_rows = []
    for table_id in PFR_TABLE_IDS:
        table = find_pfr_table(page_source, table_id)
        if table is None:
            logger.warning(f"Could not find {table_id} table for season {season}")
            continue
        assert isinstance(table, Tag)
        all_rows.extend(_parse_table(table, season))

    if not all_rows:
        raise Exception(f"Could not find any standings tables for season {season}")

    return all_rows


async def scrape_and_store(season: int, db: Session | None = None):
    from src.core.database import SessionLocal

    own_session = db is None
    if own_session:
        db = SessionLocal()

    try:
        parsed = await asyncio.to_thread(get_dataframe, season)
        repo = StandingsRepository(db)

        saved = []
        for row in parsed:
            dto = StandingsCreate(**row)
            obj = Standings(**dto.model_dump())
            saved_obj = repo.create(obj, commit=False)
            saved.append(saved_obj)

        db.commit()
        return saved

    finally:
        if own_session:
            db.close()
