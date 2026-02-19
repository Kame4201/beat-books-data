"""Shared PFR (Pro-Football-Reference) scraping module.

All stat services reuse these helpers for fetch + parse logic.
"""

import time
import logging
from typing import Optional

import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup, Comment, Tag

from src.core.config import settings
from src.core.scraper_utils import get_random_user_agent

logger = logging.getLogger(__name__)

PFR_BASE = "https://www.pro-football-reference.com"


def clean_value(v):
    """Convert empty strings to None, pandas/numpy types to Python natives."""
    if v is None or v == "":
        return None
    try:
        if pd.isna(v):
            return None
    except (TypeError, ValueError):
        pass
    if isinstance(v, np.generic):
        return v.item()
    return v


def to_int(v) -> Optional[int]:
    """Convert string to int, return None for non-numeric values."""
    v = clean_value(v)
    if v is None:
        return None
    try:
        s = str(v).replace(",", "").replace("*", "").replace("+", "").strip()
        if not s:
            return None
        return int(float(s))
    except (ValueError, TypeError):
        return None


def to_decimal(v) -> Optional[float]:
    """Convert string to float (Pydantic coerces to Decimal), return None for non-numeric."""
    v = clean_value(v)
    if v is None:
        return None
    try:
        s = (
            str(v)
            .replace(",", "")
            .replace("*", "")
            .replace("+", "")
            .replace("%", "")
            .strip()
        )
        if not s:
            return None
        return float(s)
    except (ValueError, TypeError):
        return None


def clean_player_name(name) -> Optional[str]:
    """Remove PFR player-name suffixes (*, +) indicating Pro Bowl / All-Pro."""
    if name is None:
        return None
    return name.replace("*", "").replace("+", "").strip() or None


def build_pfr_url(season: int, path: str = "") -> str:
    """Construct a PFR URL for a season page."""
    if path:
        return f"{PFR_BASE}/years/{season}/{path}"
    return f"{PFR_BASE}/years/{season}/"


def fetch_html(url: str) -> str:
    """GET with random user-agent, respects SCRAPE_DELAY_SECONDS."""
    time.sleep(settings.SCRAPE_DELAY_SECONDS)
    headers = {"User-Agent": get_random_user_agent()}
    res = requests.get(url, headers=headers, timeout=settings.SCRAPE_REQUEST_TIMEOUT)
    res.raise_for_status()
    return res.text


def find_table(html: str, table_id: str) -> Tag:
    """Find ``<table id="...">`` in *html*, checking HTML comments if not found."""
    soup = BeautifulSoup(html, "lxml")
    table = soup.find("table", id=table_id)

    if table is None:
        comments = soup.find_all(string=lambda x: isinstance(x, Comment))
        for c in comments:
            if table_id in c:
                table = BeautifulSoup(c, "lxml").find("table", id=table_id)
                if table is not None:
                    break

    if table is None:
        raise ValueError(f"Could not find table with id='{table_id}'")

    assert isinstance(table, Tag)
    return table


def parse_table_rows(table: Tag) -> list[dict]:
    """Extract rows as list of dicts keyed by ``data-stat`` attribute values."""
    rows: list[dict] = []
    for tr in table.find_all("tr"):
        if "class" in tr.attrs and "thead" in tr["class"]:
            continue

        cells = tr.find_all(["th", "td"])
        if not cells:
            continue

        row: dict = {}
        for cell in cells:
            stat = cell.get("data-stat")
            if stat:
                row[stat] = cell.get_text(strip=True)

        if not row or all(v == "" for v in row.values()):
            continue

        rows.append(row)
    return rows


def fetch_and_parse_table(
    season: int, table_id: str, page_path: str = ""
) -> list[dict]:
    """Top-level convenience: fetch page, find table, parse rows."""
    url = build_pfr_url(season, page_path)
    logger.info("Fetching PFR table '%s' from %s", table_id, url)
    html = fetch_html(url)
    table = find_table(html, table_id)
    rows = parse_table_rows(table)
    logger.info("Parsed %d rows from table '%s'", len(rows), table_id)
    return rows
