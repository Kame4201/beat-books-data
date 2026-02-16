import pandas as pd
import numpy as np

from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.entities.team_offense import TeamOffense
from src.repositories.team_offense_repo import TeamOffenseRepository
from src.dtos.team_offense_dto import TeamOffenseCreate


def clean_value(v):
    try:
        if pd.isna(v):
            return None
    except (TypeError, ValueError):
        pass

    if isinstance(v, np.generic):
        return v.item()

    return v


def get_team_offense_dataframe(season: int):
    import requests
    from bs4 import BeautifulSoup, Comment

    url = f"https://www.pro-football-reference.com/years/{season}/"
    res = requests.get(url)
    res.raise_for_status()

    soup = BeautifulSoup(res.text, "lxml")

    table = soup.find("table", id="team_stats")

    if table is None:
        comments = soup.find_all(string=lambda x: isinstance(x, Comment))
        for c in comments:
            if "team_stats" in c:
                table = BeautifulSoup(c, "lxml").find("table", id="team_stats")
                break

    if table is None:
        raise Exception("Could not find team_stats table")
    from bs4 import Tag
      assert isinstance(table, Tag)

    rows = []

    for tr in table.find_all("tr"):
        # skip header rows
        if "class" in tr.attrs and "thead" in tr["class"]:
            continue

        cells = tr.find_all("td")
        if not cells:
            continue

        tm = tr.find("td", {"data-stat": "team"})
        if not tm or not tm.text.strip():
            continue  # skip blank rows

        row = [c.text.strip() for c in cells]
        rows.append(row)

    headers = [th.get_text(strip=True) for th in table.find_all("th")][1:len(rows[0])+1]

    df = pd.DataFrame(rows, columns=headers)

    return df


def parse_team_offense(df: pd.DataFrame, season: int):
    offenses = []

    for _, row in df.iterrows():
        rec = {
            "season": season,
            "rk": clean_value(row.get("Rk")),
            "tm": clean_value(row.get("Tm")),
            "g": clean_value(row.get("G")),
            "pf": clean_value(row.get("PF")),
            "yds": clean_value(row.get("Yds")),
            "ply": clean_value(row.get("Ply")),
            "ypp": clean_value(row.get("Y/P")),
            "turnovers": clean_value(row.get("TO")),
            "fl": clean_value(row.get("FL")),
            "firstd_total": clean_value(row.get("1stD")),
            "cmp": clean_value(row.get("Cmp")),
            "att_pass": clean_value(row.get("Att")),
            "yds_pass": clean_value(row.get("Yds.1")),
            "td_pass": clean_value(row.get("TD")),
            "ints": clean_value(row.get("Int")),
            "nypa": clean_value(row.get("NY/A")),
            "firstd_pass": clean_value(row.get("1stD.1")),
            "att_rush": clean_value(row.get("Att.1")),
            "yds_rush": clean_value(row.get("Yds.2")),
            "td_rush": clean_value(row.get("TD.1")),
            "ypa": clean_value(row.get("Y/A")),
            "firstd_rush": clean_value(row.get("1stD.2")),
            "pen": clean_value(row.get("Pen")),
            "yds_pen": clean_value(row.get("Yds.3")),
            "firstpy": clean_value(row.get("1stPy")),
            "sc_pct": clean_value(row.get("Sc%")),
            "to_pct": clean_value(row.get("TO%")),
            "opea": clean_value(row.get("O/Pl")),
        }

        offenses.append(rec)

    return offenses


async def scrape_and_store_team_offense(season: int):

    db: Session = SessionLocal()

    try:
        df = get_team_offense_dataframe(season)
        parsed = parse_team_offense(df, season)

        repo = TeamOffenseRepository(db)

        saved = []
        for row in parsed:
            # Validate input with DTO
            dto = TeamOffenseCreate(**row)
            # Convert DTO to entity
            obj = TeamOffense(**dto.model_dump())
            saved_obj = repo.create(obj, commit=False)
            saved.append(saved_obj)

        db.commit()

        return saved

    finally:
        db.close()