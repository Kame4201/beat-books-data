# Development Guide -- beat-books-data

This document covers everything needed to develop, test, and extend the beat-books-data service.

## Prerequisites

- **Python 3.11+** (tested on 3.11 and 3.12)
- **PostgreSQL** (production uses Neon.tech; local dev can use Docker or SQLite for tests)
- **Google Chrome** (required for Selenium-based scrapers)
- **ChromeDriver** (auto-managed by `webdriver-manager`)

## Setting Up the Dev Environment

### 1. Clone the repository

```bash
git clone https://github.com/<org>/beat-books-data.git
cd beat-books-data
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
pip install pytest pytest-asyncio pytest-cov  # dev/test deps
```

### 4. Configure environment variables

Copy the example env file and fill in your values:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```dotenv
# Database (required) -- get this from Neon.tech or use a local Postgres
DATABASE_URL=postgresql://user:password@host:5432/beatthebooks

# Scraping
SCRAPE_DELAY_SECONDS=60        # Delay between scrape requests (be respectful)
SCRAPE_REQUEST_TIMEOUT=30      # Page load timeout in seconds
SCRAPE_MAX_RETRIES=3           # Max retry attempts per URL

# Odds API (Phase 2 -- optional)
ODDS_API_KEY=
ODDS_API_BASE_URL=https://api.the-odds-api.com

# App
LOG_LEVEL=INFO                 # DEBUG for verbose output
API_HOST=0.0.0.0
API_PORT=8001
```

## Running the App Locally

```bash
uvicorn src.main:app --reload --port 8001
```

The API will be available at `http://localhost:8001`. Visit `http://localhost:8001/docs` for the interactive Swagger UI.

### Available Endpoints

| Method | Path                    | Description                            |
|--------|-------------------------|----------------------------------------|
| GET    | `/`                     | Health check                           |
| GET    | `/scrape/{team}/{year}` | Scrape game log for a team + season    |
| GET    | `/scrape/{year}`        | Scrape team offense stats for a season |
| POST   | `/scrape/excel`         | Scrape URLs from an Excel file         |

## Running Tests

### All tests

```bash
pytest
```

### Unit tests only

```bash
pytest tests/test_unit/ -v
```

### With coverage report

```bash
pytest --cov=src --cov-report=html
# Open htmlcov/index.html in a browser to view the report
```

### Specific test files

```bash
# Service tests
pytest tests/test_unit/test_services/test_team_offense_service.py -v

# Repository tests
pytest tests/test_unit/test_repositories/test_base_repo.py -v

# DTO validation tests
pytest tests/test_unit/test_dtos.py -v
```

### Test architecture

- **Unit tests** (`tests/test_unit/`): Use in-memory SQLite and mocks. No network or production DB access.
- **Integration tests**: Marked with `@pytest.mark.integration`. Require a running database.
- **Fixtures** are defined in `tests/conftest.py` (shared) and per-test-file as needed.

## Database Migrations (Alembic)

All schema changes MUST go through Alembic migrations. Never run raw `ALTER TABLE` statements.

### Check current migration status

```bash
alembic current
```

### Apply all pending migrations

```bash
alembic upgrade head
```

### Create a new migration (auto-detect changes from entities)

```bash
alembic revision --autogenerate -m "add column foo to team_offense"
```

### Create an empty migration (for manual SQL)

```bash
alembic revision -m "backfill historical data"
```

### Roll back one migration

```bash
alembic downgrade -1
```

### View migration history

```bash
alembic history
```

### Important notes

- The entity models in `src/entities/` are the single source of truth for the schema.
- After modifying any entity, always run `alembic revision --autogenerate` to generate the migration.
- Review auto-generated migrations before applying -- they may need manual adjustments.
- This repo OWNS the database schema. Other repos (beat-books-model, beat-books-api) have READ-ONLY access.

## How to Add a New Scraper

Follow the **Entity -> DTO -> Repository -> Service -> Endpoint** pattern:

### 1. Create the Entity (`src/entities/`)

Define the SQLAlchemy ORM model that maps to the database table:

```python
# src/entities/my_new_stats.py
from sqlalchemy import Integer, String, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base

class MyNewStats(Base):
    __tablename__ = "my_new_stats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    season: Mapped[int] = mapped_column(Integer)
    tm: Mapped[str] = mapped_column(String(64))
    # ... add columns
```

### 2. Create the DTO (`src/dtos/`)

Define Pydantic models for input validation and output serialization:

```python
# src/dtos/my_new_stats_dto.py
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class MyNewStatsCreate(BaseModel):
    season: int = Field(..., ge=1920, le=2100)
    tm: str = Field(..., min_length=1, max_length=64)
    # ... add fields with validation

class MyNewStatsResponse(MyNewStatsCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)
```

### 3. Create the Repository (`src/repositories/`)

Extend BaseRepository for data access:

```python
# src/repositories/my_new_stats_repo.py
from sqlalchemy.orm import Session
from src.entities.my_new_stats import MyNewStats
from src.repositories.base_repo import BaseRepository

class MyNewStatsRepository(BaseRepository[MyNewStats]):
    def __init__(self, session: Session) -> None:
        super().__init__(session=session, model=MyNewStats)
```

### 4. Create the Service (`src/services/`)

Implement scraping and business logic (NO SQL here):

```python
# src/services/my_new_stats_service.py
import logging
from src.core.database import SessionLocal
from src.repositories.my_new_stats_repo import MyNewStatsRepository
from src.dtos.my_new_stats_dto import MyNewStatsCreate
from src.entities.my_new_stats import MyNewStats

logger = logging.getLogger(__name__)

async def scrape_and_store(season: int):
    db = SessionLocal()
    try:
        # 1. Fetch data (requests, Selenium, etc.)
        # 2. Parse into dicts
        # 3. Validate with DTO
        # 4. Convert to entity
        # 5. Save via repository
        logger.info("Scraping my_new_stats for season %d", season)
        ...
    finally:
        db.close()
```

### 5. Create the Endpoint (`src/main.py`)

Register the FastAPI route:

```python
@app.get("/scrape/my-new-stats/{year}")
async def scrape_my_new_stats(year: int):
    data = await my_new_stats_service.scrape_and_store(year)
    return data
```

### 6. Generate the Migration

```bash
alembic revision --autogenerate -m "add my_new_stats table"
alembic upgrade head
```

### 7. Add Tests

Create tests in `tests/test_unit/test_services/` and `tests/test_unit/test_repositories/`.

## Technology Stack

| Technology         | Purpose                                                                 |
|--------------------|-------------------------------------------------------------------------|
| **FastAPI**        | Async web framework for the REST API. Auto-generates OpenAPI docs.      |
| **SQLAlchemy**     | ORM for database models and queries. Mapped column syntax (2.0 style).  |
| **Alembic**        | Database migration tool. Tracks schema versions, auto-detects changes.  |
| **PostgreSQL**     | Production database, hosted on Neon.tech with connection pooling.       |
| **Pydantic**       | Data validation via DTOs. Ensures scraped data meets constraints.       |
| **Selenium**       | Browser automation for scraping JS-rendered pages on PFR.               |
| **BeautifulSoup**  | HTML parsing for extracting tables and data from scraped pages.         |
| **pandas**         | DataFrame manipulation for cleaning and transforming scraped data.      |
| **Requests**       | Simple HTTP client for non-JS pages (e.g., team offense stats).        |
| **pydantic-settings** | Environment variable management via `.env` files.                   |
| **webdriver-manager** | Automatic ChromeDriver version management.                          |
| **pytest**         | Test framework with fixtures, markers, and plugins.                     |

## Project Architecture

```
src/
├── core/              # Shared infrastructure
│   ├── config.py      # Centralized settings (env vars)
│   ├── database.py    # SQLAlchemy engine + session factory
│   └── scraper_utils.py  # Retry logic, user-agent rotation, proxy support
├── entities/          # SQLAlchemy ORM models (source of truth for DB schema)
├── dtos/              # Pydantic validation models (input/output boundaries)
├── repositories/      # Data access layer (ALL SQL lives here)
├── services/          # Business logic + scraping (NO SQL here)
└── main.py            # FastAPI app + route definitions
```

### Key architectural rules

- **Services** contain business logic and scraping. They NEVER contain raw SQL.
- **Repositories** contain all database queries. They NEVER contain business logic.
- **DTOs** validate all external data before it reaches the database.
- **Entities** are the single source of truth for the database schema.

## Troubleshooting

### 403 errors from Pro-Football-Reference

PFR blocks requests containing URL hash fragments (e.g., `#all_team_stats`). The `strip_url_hash()` utility in `scraper_utils.py` handles this automatically.

### Scraping rate limits

The `SCRAPE_DELAY_SECONDS` setting controls the delay between requests. The default is 60 seconds. Reduce for development, but keep it at 60+ for production to avoid getting blocked.

### ChromeDriver version mismatch

The `webdriver-manager` package auto-downloads the correct ChromeDriver version. If you encounter issues, try:

```bash
pip install --upgrade webdriver-manager
```
