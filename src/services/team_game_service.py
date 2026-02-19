"""Scrape per-team gamelogs from PFR (replaces old Selenium-based scrape_service)."""

import logging
from datetime import date

from src.core.database import SessionLocal
from src.core.pfr_scraper import (
    PFR_BASE,
    fetch_html,
    find_table,
    parse_table_rows,
    clean_value,
    to_int,
)
from src.repositories.team_game_repo import TeamGameRepository
from src.dtos.team_game_dto import TeamGameCreate

logger = logging.getLogger(__name__)


def _parse_date(raw: str):
    raw = clean_value(raw)
    if not raw:
        return None
    try:
        return date.fromisoformat(raw)
    except ValueError:
        return None


def _parse_result(result_str: str, team: str, opp: str):
    """Parse a game_result like 'W 31-10' into winner/loser/pts."""
    result_str = clean_value(result_str)
    if not result_str:
        return None, None, None, None

    parts = result_str.split()
    outcome = parts[0] if parts else ""
    scores = parts[1] if len(parts) >= 2 else ""

    team_pts, opp_pts = None, None
    if "-" in scores:
        score_parts = scores.split("-")
        team_pts = to_int(score_parts[0])
        opp_pts = to_int(score_parts[1])

    if outcome == "W":
        return team, opp, team_pts, opp_pts
    elif outcome == "L":
        return opp, team, opp_pts, team_pts
    else:
        return team, opp, team_pts, opp_pts


def parse_rows(rows: list[dict], team: str, season: int) -> list[dict]:
    parsed = []
    team_upper = team.upper()

    for row in rows:
        week = to_int(row.get("week_num"))
        if week is None:
            continue

        opp = clean_value(row.get("opp") or row.get("opp_id") or "")
        game_result = row.get("game_result", "")

        winner, loser, pts_w, pts_l = _parse_result(game_result, team_upper, opp)

        # Determine yards/turnovers based on outcome
        team_yds = to_int(row.get("yards_off") or row.get("yards_offense"))
        team_to = to_int(row.get("turnovers") or row.get("to_off"))
        opp_yds = to_int(row.get("opp_yards_off") or row.get("opp_yards_offense"))
        opp_to = to_int(row.get("opp_turnovers") or row.get("opp_to"))

        if winner == team_upper:
            yds_w, yds_l = team_yds, opp_yds
            to_w, to_l = team_to, opp_to
        else:
            yds_w, yds_l = opp_yds, team_yds
            to_w, to_l = opp_to, team_to

        rec = {
            "team_abbr": team_upper,
            "season": season,
            "week": week,
            "day": clean_value(row.get("game_day_of_week")),
            "game_date": _parse_date(row.get("game_date", "")),
            "game_time": clean_value(row.get("gametime")),
            "winner": winner,
            "loser": loser,
            "pts_w": pts_w,
            "pts_l": pts_l,
            "yds_w": yds_w,
            "to_w": to_w,
            "yds_l": yds_l,
            "to_l": to_l,
        }
        parsed.append(rec)
    return parsed


async def scrape_and_store(team: str, season: int):
    db = SessionLocal()
    try:
        url = f"{PFR_BASE}/teams/{team.lower()}/{season}.htm"
        logger.info("Fetching team gamelog from %s", url)
        html = fetch_html(url)

        table = find_table(html, f"gamelog{season}")
        rows = parse_table_rows(table)
        parsed = parse_rows(rows, team, season)

        saved, skipped = 0, 0
        for row in parsed:
            dto = TeamGameCreate(**row)
            result = TeamGameRepository.create_or_skip(db, dto)
            if result:
                saved += 1
            else:
                skipped += 1

        return {
            "status": "success",
            "team": team,
            "season": season,
            "rows_saved": saved,
            "rows_skipped": skipped,
        }
    finally:
        db.close()
