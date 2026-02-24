from pydantic_settings import BaseSettings
from typing import List, Literal


class Settings(BaseSettings):
    """Centralized configuration for beat-books-data service.

    Required variables will cause a clear ValidationError at startup
    if missing. See .env.example for the full variable list.
    """

    # Database (required — app won't start without it)
    DATABASE_URL: str
    # Scraping — backend selection
    SCRAPE_BACKEND: Literal["selenium", "scrapling"] = "selenium"

    # Scraping — shared
    SCRAPE_DELAY_SECONDS: int = 60
    SCRAPE_REQUEST_TIMEOUT: int = 30  # seconds
    SCRAPE_MAX_RETRIES: int = 3
    SCRAPE_RETRY_DELAYS: List[int] = [
        30,
        60,
        120,
    ]  # exponential backoff delays in seconds

    # User-Agent rotation pool (10+ browser-like user agents)
    SCRAPE_USER_AGENTS: List[str] = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    ]

<<<<<<< claude/issue-8-20260216-0000
=======
    # Scrapling-specific (only used when SCRAPE_BACKEND=scrapling)
    SCRAPLING_FETCHER_TYPE: Literal["fetcher", "stealthy"] = "fetcher"
    SCRAPLING_TIMEOUT: int = 30
    SCRAPLING_IMPERSONATE: str = "chrome"

>>>>>>> main
    # Proxy rotation (optional)
    SCRAPE_USE_PROXY: bool = False
    SCRAPE_PROXY_LIST: List[str] = (
        []
    )  # Format: ["http://proxy1:port", "http://proxy2:port"]

<<<<<<< claude/issue-8-20260216-0000
    # Weather API (OpenWeatherMap)
    OPENWEATHER_API_KEY: str = ""

=======
>>>>>>> main
    # Odds API (Phase 2)
    ODDS_API_KEY: str = ""
    ODDS_API_BASE_URL: str = "https://api.the-odds-api.com"

    # App
    ENV: Literal["local", "dev", "stage", "main"] = "local"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    API_HOST: str = "0.0.0.0"  # nosec B104
    API_PORT: int = 8001

    @property
    def is_production(self) -> bool:
        return self.ENV == "main"

    model_config = {"env_file": ".env"}


settings = Settings()  # type: ignore[call-arg]  # populated by env/.env at runtime
