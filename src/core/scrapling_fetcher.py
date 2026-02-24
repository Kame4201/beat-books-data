"""
Scrapling-based page fetcher.

Drop-in alternative to fetch_page_with_selenium().
Returns raw HTML string with the same contract so downstream
BeautifulSoup parsing is unaffected.

Activated only when SCRAPE_BACKEND=scrapling.
"""

import logging
import random
import time
from typing import Literal, Optional, cast

from src.core.config import settings

logger = logging.getLogger(__name__)

Impersonate = Literal[
    "chrome",
    "edge",
    "safari",
    "firefox",
    "chrome_android",
    "safari_ios",
]


def _coerce_impersonate(value: str | None) -> Optional[Impersonate]:
    if not value:
        return None
    v = value.strip().lower()
    if v in {
        "chrome",
        "edge",
        "safari",
        "firefox",
        "chrome_android",
        "safari_ios",
    }:
        return cast(Impersonate, v)
    return None


logger = logging.getLogger(__name__)


def _get_proxy() -> Optional[str]:
    """Return a proxy URL if proxy rotation is enabled, else None."""
    if not settings.SCRAPE_USE_PROXY or not settings.SCRAPE_PROXY_LIST:
        return None

    return random.choice(settings.SCRAPE_PROXY_LIST)


def fetch_page_with_scrapling(url: str) -> str:
    """
    Fetch a page using Scrapling and return the raw HTML string.

    Mirrors the contract of fetch_page_with_selenium():
      - Applies SCRAPE_DELAY_SECONDS rate-limit sleep
      - Strips URL hash fragments
      - Returns page source as str

    Args:
        url: URL to fetch

    Returns:
        Page source HTML string

    Raises:
        ImportError: If scrapling is not installed
        RuntimeError: If the fetch returns an empty/error response
    """
    from scrapling.fetchers import Fetcher, StealthyFetcher
    from src.core.scraper_utils import strip_url_hash

    clean_url = strip_url_hash(url)
    if clean_url != url:
        logger.info("Stripped hash fragment from URL: %s -> %s", url, clean_url)
        url = clean_url

    time.sleep(settings.SCRAPE_DELAY_SECONDS)

    proxy = _get_proxy()
    fetcher_type = settings.SCRAPLING_FETCHER_TYPE

    logger.info(
        "Scrapling fetch starting",
        extra={
            "url": url,
            "fetcher_type": fetcher_type,
            "impersonate": settings.SCRAPLING_IMPERSONATE,
            "proxy": bool(proxy),
        },
    )

    if fetcher_type == "stealthy":
        response = StealthyFetcher.fetch(
            url,
            headless=True,
            timeout=settings.SCRAPLING_TIMEOUT,
            proxy={"server": proxy} if proxy else None,
        )
    else:
        imp = _coerce_impersonate(settings.SCRAPLING_IMPERSONATE)

        if imp is not None:
            response = Fetcher.get(
                url,
                timeout=settings.SCRAPLING_TIMEOUT,
                stealthy_headers=True,
                impersonate=imp,
                proxy=proxy,
            )
        else:
            response = Fetcher.get(
                url,
                timeout=settings.SCRAPLING_TIMEOUT,
                stealthy_headers=True,
                proxy=proxy,
            )

    page_source: str = response.html_content
    if not page_source:
        raise RuntimeError(f"Scrapling returned empty response for {url}")

    status = getattr(response, "status", None)
    logger.info(
        "Scrapling fetch complete",
        extra={
            "url": url,
            "status": status,
            "length": len(page_source),
            "fetcher_type": fetcher_type,
        },
    )

    return page_source
