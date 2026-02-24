# beat-books-data

NFL data ingestion, storage, and retrieval service for the BeatTheBooks platform.

## What This Does

- **Scrapes** NFL statistics from Pro-Football-Reference (Selenium + BeautifulSoup)
- **Stores** data in PostgreSQL (Neon.tech) via SQLAlchemy
- **Serves** data retrieval API for other BeatTheBooks services
- **Owns** the database schema and all migrations

## Tech Stack

- Python 3.11+
- FastAPI
- SQLAlchemy + Alembic
- PostgreSQL (Neon.tech)
- Selenium + BeautifulSoup + Pandas (default fetch backend)
- Scrapling (optional fetch backend)

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your DATABASE_URL

# Run the service
uvicorn src.main:app --reload --port 8001
```

## Scrape Backend Selection

The fetch layer supports two backends, controlled by the `SCRAPE_BACKEND` env var.
**Selenium is the default.** No change is needed to preserve existing behavior.

| Value | Backend | When to use |
|-------|---------|-------------|
| `selenium` | Headless Chrome via Selenium | Default. Production-proven. Required for `scrape_service.py` (JS interaction). |
| `scrapling` | Scrapling (curl-cffi or Camoufox) | Lighter weight, no browser process. Opt-in only. |

```bash
# Use Selenium (default — no change needed)
SCRAPE_BACKEND=selenium

# Switch to Scrapling
SCRAPE_BACKEND=scrapling
SCRAPLING_FETCHER_TYPE=fetcher      # "fetcher" (HTTP) or "stealthy" (Camoufox browser)
SCRAPLING_TIMEOUT=30
SCRAPLING_IMPERSONATE=chrome
```

### Rollback

To revert to Selenium at any time, set `SCRAPE_BACKEND=selenium` (or remove the variable entirely). No code changes or redeployment of different code is required — the Scrapling code path is never loaded unless explicitly selected.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/scrape/{team}/{year}` | Scrape single team stats |
| GET | `/scrape/{year}` | Scrape team offense stats |
| POST | `/scrape/excel` | Batch scrape from Excel URLs |

## Database

14+ tables covering team and player statistics, games, and standings. See `Tables.sql` for the full schema.

## Related Repos

- [beat-books-model](https://github.com/Kame4201/beat-books-model) — ML predictions & strategy
- [beat-books-api](https://github.com/Kame4201/beat-books-api) — API gateway
- [beat-books-infra](https://github.com/Kame4201/beat-books-infra) — CI/CD, docs, Docker
