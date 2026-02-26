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
from src.dtos.games_dto import GamesCreate
from src.entities.games import Games
from src.repositories.games_repo import GamesRepository

logger = logging.getLogger(__name__)

PFR_URL_TEMPLATE = "https://www.pro-football-reference.com/years/{season}/games.htm"
PFR_TABLE_ID = "games"

COLUMN_MAP = {
    "week_num": "week",
    "game_day_of_week": "game_day",
    "boxscore_word": "boxscore",
    "pts_win": "pts_w",
    "pts_lose": "pts_l",
    "yards_win": "yds_w",
    "to_win": "to_w",
    "yards_lose": "yds_l",
    "to_lose": "to_l",
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

        # Skip separator/header rows within the table
        week_cell = tr.find("th", {"data-stat": "week_num"})
        if not week_cell or not week_cell.text.strip():
            continue

        week_text = week_cell.text.strip()
        # Skip non-numeric weeks (like "Week" header repeats)
        try:
            int(week_text)
        except ValueError:
            continue

        row = {"week": clean_value(week_text)}

        # Extract winner/loser from special cells
        winner_cell = tr.find("td", {"data-stat": "winner"})
        loser_cell = tr.find("td", {"data-stat": "loser"})
        game_date_cell = tr.find("td", {"data-stat": "game_date"})
        game_time_cell = tr.find("td", {"data-stat": "gametime"})

        if winner_cell:
            row["winner"] = clean_value(winner_cell.text.strip())
        if loser_cell:
            row["loser"] = clean_value(loser_cell.text.strip())
        if game_date_cell:
            row["game_date"] = clean_value(game_date_cell.text.strip())
        if game_time_cell:
            row["kickoff_time"] = clean_value(game_time_cell.text.strip())

        for cell in cells:
            data_stat = cell.get("data-stat")
            if data_stat and data_stat in COLUMN_MAP:
                row[COLUMN_MAP[data_stat]] = clean_value(cell.text.strip())

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
        repo = GamesRepository(db)

        saved = []
        for row in parsed:
            dto = GamesCreate(**row)
            obj = Games(**dto.model_dump())
            saved_obj = repo.create(obj, commit=False)
            saved.append(saved_obj)

        db.commit()
        return saved

    finally:
        if own_session:
            db.close()
