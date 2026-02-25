import time
import base64
import logging
import pandas as pd
import numpy as np
from io import StringIO
from datetime import datetime
from selenium.webdriver.common.by import By
from src.dtos.team_game_dto import TeamGameCreate
from src.repositories.team_game_repo import TeamGameRepository
from src.core.database import SessionLocal
from src.core.config import settings
from src.core.scraper_utils import (
    strip_url_hash,
    create_chrome_driver,
    retry_with_backoff,
)

logger = logging.getLogger(__name__)


def flatten_pfr_columns(df: pd.DataFrame):
    """Flatten MultiIndex columns from PFR exports cleanly."""
    new_cols = []

    for col in df.columns:
        if isinstance(col, tuple):
            lvl0, lvl1 = col

            # Prefer lvl1 if it is meaningful
            if isinstance(lvl1, str) and lvl1 and not lvl1.startswith("Unnamed"):
                new_cols.append(lvl1.strip())
                continue

            # Else use lvl0 if meaningful
            if isinstance(lvl0, str) and lvl0 and not lvl0.startswith("Unnamed"):
                new_cols.append(lvl0.strip())
                continue

            # Fallback: return whichever is non-empty
            new_cols.append(lvl1.strip() if lvl1 else lvl0.strip())
        else:
            new_cols.append(col)

    df.columns = new_cols
    return df


def clean_value(v):
    """Convert pandas/numpy types -> pure Python, handle NaN."""
    if isinstance(v, pd.Series):
        if len(v) == 0:
            return None
        v = v.iloc[0]

    # NAN → None
    try:
        if pd.isna(v):
            return None
    except (TypeError, ValueError):
        pass

    # numpy → python
    if isinstance(v, (np.generic,)):
        return v.item()

    return v


def parse_xlsx_to_games(excel_bytes: bytes, team: str):
    # Convert bytes → string
    html_str = excel_bytes.decode("utf-8")

    # Use StringIO to avoid FutureWarning
    tables = pd.read_html(StringIO(html_str))

    df = tables[0]  # first table is schedule
    logger.debug("DataFrame head:\n%s", df.head())
    # Flatten MultiIndex columns
    if isinstance(df.columns, pd.MultiIndex):
        df = flatten_pfr_columns(df)

    logger.debug("Cleaned columns: %s", df.columns.tolist())

    games = []
    for _, row in df.iterrows():
        raw_week = row.get("Week", row.get("Week_", None))
        if raw_week is None or pd.isna(raw_week):
            week_val = None
        else:
            try:
                week_val = int(raw_week)
            except (TypeError, ValueError):
                week_val = None

        game = {
            "team": team.upper(),
            "week": week_val,
            "day": row.get("Day", row.get("Day_", None)),
            "date": row.get("Date", row.get("Date_", None)),
            "time": row.get("Unnamed: 3_level_1"),
            "result": row.get("Unnamed: 5_level_1"),
            "opponent": row.get("Opp", row.get("Opp_", None)),
            "location": "",  # '@' marks away if needed
            "team_score": row.get("Tm", row.get("Tm_", None)),
            "opp_score": row.get("Opp.1", row.get("Opp.1_", None)),
            "tot_yards_for": row.get("TotYd", row.get("TotYd_", None)),
            "tot_yards_against": row.get("TotYd.1", row.get("TotYd.1_", None)),
            "pass_yards": row.get("PassY", row.get("PassY_", None)),
            "rush_yards": row.get("RushY", row.get("RushY_", None)),
            "turnovers": row.get("TO", row.get("TO_", None)),
        }
        cleaned_game = {k: clean_value(v) for k, v in game.items()}
        games.append(cleaned_game)

    return games


def extract_excel_bytes_from_dlink(driver):
    """
    After clicking 'Get as Excel Workbook', PFR injects <a id="dlink">
    containing base64 Excel data. Extract the bytes.
    """

    dlink = driver.find_element(By.ID, "dlink")
    href = dlink.get_attribute("href")

    if not href or not href.startswith("data:"):
        raise Exception("dlink href did not populate — PFR JS may not have executed.")

    header, b64data = href.split(",", 1)
    logger.debug("DLINK header: %s", header)
    excel_bytes = base64.b64decode(b64data)

    return excel_bytes


def map_scraped_to_model(scraped: dict, season: int) -> TeamGameCreate:
    # ---- DATE PARSING ----
    date_val = None
    raw_date = scraped.get("date")

    if raw_date:
        try:
            date_val = datetime.strptime(f"{raw_date} {season}", "%B %d %Y").date()
        except (TypeError, ValueError):
            date_val = None

    team = scraped["team"]
    opp = scraped.get("opponent")
    result = scraped.get("result")

    # ---- WINNER / LOSER LOGIC ----
    if result == "W":
        winner = team
        loser = opp
        pts_w = scraped.get("team_score")
        pts_l = scraped.get("opp_score")
        yds_w = scraped.get("tot_yards_for")
        yds_l = scraped.get("tot_yards_against")
        to_w = scraped.get("turnovers")
        to_l = None

    elif result == "L":
        winner = opp
        loser = team
        pts_w = scraped.get("opp_score")
        pts_l = scraped.get("team_score")
        yds_w = scraped.get("tot_yards_against")
        yds_l = scraped.get("tot_yards_for")
        to_w = None
        to_l = scraped.get("turnovers")

    else:
        # Not a real game (bye week, canceled, missing result)
        winner = loser = None
        pts_w = pts_l = yds_w = yds_l = to_w = to_l = None

    # ---- RETURN DTO ----
    return TeamGameCreate(
        team_abbr=team,
        season=season,
        week=scraped.get("week") or 0,
        day=scraped.get("day"),
        game_date=date_val,
        game_time=scraped.get("time"),
        winner=winner,
        loser=loser,
        pts_w=pts_w,
        pts_l=pts_l,
        yds_w=yds_w,
        to_w=to_w,
        yds_l=yds_l,
        to_l=to_l,
    )


async def download_team_gamelog(team: str, year: int):
    url = f"https://www.pro-football-reference.com/teams/{team.lower()}/{year}.htm"

    # Strip hash fragments to avoid 403 errors
    clean_url = strip_url_hash(url)
    if clean_url != url:
        logger.info(f"Stripped hash fragment from URL: {url} -> {clean_url}")
        url = clean_url

    driver = create_chrome_driver(headless=True)

    driver.get(url)
    time.sleep(settings.SCRAPE_PAGE_LOAD_WAIT)

    # Scroll to the Schedule section
    section = driver.find_element(
        By.XPATH, "//h2[contains(text(), 'Schedule')]/parent::div"
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", section)
    time.sleep(settings.SCRAPE_PAGE_LOAD_WAIT)

    # Click "Share & more"
    share = section.find_element(
        By.XPATH, ".//li[contains(@class, 'hasmore')]/span[contains(text(),'Share')]"
    )
    share.click()
    time.sleep(settings.SCRAPE_CLICK_DELAY)

    # Click "Get as Excel Workbook"
    excel_btn = section.find_element(
        By.XPATH, ".//button[contains(text(),'Get as Excel Workbook')]"
    )
    excel_btn.click()
    time.sleep(settings.SCRAPE_PAGE_LOAD_WAIT)

    # Extract Excel bytes from injected <a id="dlink">
    excel_bytes = extract_excel_bytes_from_dlink(driver)
    logger.debug("First 200 bytes of Excel data: %s", excel_bytes[:200])

    driver.quit()

    # Parse direct bytes into Python objects
    return parse_xlsx_to_games(excel_bytes, team)


async def scrape_and_store(team: str, year: int):
    db = SessionLocal()

    url = f"https://www.pro-football-reference.com/teams/{team.lower()}/{year}.htm"

    try:
        # Use retry logic with exponential backoff
        scraped_games = await retry_with_backoff(
            download_team_gamelog, team, year, url=url
        )
        repo = TeamGameRepository(db)
        saved = []

        for game in scraped_games:
            model_obj = map_scraped_to_model(game, year)
            saved_obj = repo.create_or_skip(model_obj)
            saved.append(saved_obj)

        logger.info(
            f"Successfully scraped and stored {len(saved)} games for {team} {year}"
        )
        return saved

    finally:
        db.close()
