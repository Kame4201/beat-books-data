"""
Service for scraping and managing injury reports.
"""

import time
from typing import List, Optional
from datetime import date
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from src.core.config import settings
from src.core.database import SessionLocal
from src.repositories.injury_report_repo import InjuryReportRepository
from src.dtos.injury_report_dto import InjuryReportCreate
from src.entities.injury_report import InjuryReport


class InjuryReportService:
    """
    Service for scraping and storing injury reports.

    Scrapes weekly injury designations from Pro-Football-Reference.
    """

    def __init__(self, db_session: Optional[SessionLocal] = None):
        """
        Initialize the service.

        Args:
            db_session: Optional database session (will create new if not provided)
        """
        self.db = db_session or SessionLocal()
        self.repo = InjuryReportRepository(self.db)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.db:
            self.db.close()

    def scrape_weekly_injuries_pfr(
        self, season: int, week: int
    ) -> List[InjuryReportCreate]:
        """
        Scrape injury reports for a specific week from Pro-Football-Reference.

        Args:
            season: NFL season year
            week: Week number

        Returns:
            List of InjuryReportCreate DTOs
        """
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options,
        )

        injury_reports = []

        try:
            # Pro-Football-Reference injury report URL format
            url = f"https://www.pro-football-reference.com/years/{season}/week_{week}_injuries.htm"
            driver.get(url)

            # Rate-limit scraping using centralized config
            time.sleep(settings.SCRAPE_DELAY_SECONDS)

            # Get page source and parse with BeautifulSoup
            soup = BeautifulSoup(driver.page_source, "html.parser")

            # Find the injury table (typically id="injuries")
            injury_table = soup.find("table", {"id": "injuries"})

            if not injury_table:
                print(f"No injury table found for {season} week {week}")
                return injury_reports

            # Parse table rows
            tbody = injury_table.find("tbody")
            if not tbody:
                return injury_reports

            rows = tbody.find_all("tr")

            for row in rows:
                # Skip header rows
                if row.get("class") and "thead" in row.get("class"):
                    continue

                cells = row.find_all(["td", "th"])
                if len(cells) < 5:
                    continue

                try:
                    # Extract data from cells
                    # Typical columns: Player, Team, Position, Injury, Game Status
                    player_name = cells[0].get_text(strip=True)
                    team = cells[1].get_text(strip=True)
                    position = cells[2].get_text(strip=True) if len(cells) > 2 else None
                    injury_type = (
                        cells[3].get_text(strip=True) if len(cells) > 3 else None
                    )
                    designation = (
                        cells[4].get_text(strip=True) if len(cells) > 4 else None
                    )

                    if player_name and team and designation:
                        injury_report = InjuryReportCreate(
                            season=season,
                            week=week,
                            player_name=player_name,
                            team=team,
                            position=position,
                            designation=designation,
                            injury_type=injury_type,
                            report_date=date.today(),
                        )
                        injury_reports.append(injury_report)

                except Exception as e:
                    print(f"Error parsing injury row: {e}")
                    continue

        except Exception as e:
            print(f"Error scraping injuries from PFR: {e}")
            raise

        finally:
            driver.quit()

        return injury_reports

    def scrape_and_store(self, season: int, week: int) -> List[InjuryReport]:
        """
        Scrape injury reports and store them in the database.

        This method is idempotent - it will delete existing reports for the week
        before inserting new ones.

        Args:
            season: NFL season year
            week: Week number

        Returns:
            List of created InjuryReport entities
        """
        # Scrape injury data
        injury_dtos = self.scrape_weekly_injuries_pfr(season, week)

        if not injury_dtos:
            print(f"No injury reports found for {season} week {week}")
            return []

        # Upsert into database (delete old, insert new)
        created_reports = self.repo.upsert_week_reports(season, week, injury_dtos)

        print(f"Stored {len(created_reports)} injury reports for {season} week {week}")
        return created_reports

    def get_week_injuries(self, season: int, week: int) -> List[InjuryReport]:
        """
        Get all injury reports for a specific week.

        Args:
            season: NFL season year
            week: Week number

        Returns:
            List of InjuryReport entities
        """
        return self.repo.get_by_week(season, week)

    def get_team_injuries(
        self, season: int, week: int, team: str
    ) -> List[InjuryReport]:
        """
        Get injury reports for a specific team and week.

        Args:
            season: NFL season year
            week: Week number
            team: Team abbreviation

        Returns:
            List of InjuryReport entities
        """
        return self.repo.get_by_team(season, week, team)
