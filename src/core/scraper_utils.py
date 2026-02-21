"""
Utility functions for web scraping with retry logic, user-agent rotation, and error handling.
"""

import time
import random
import logging
from typing import Callable, Any, Optional, List

import pandas as pd
import numpy as np
from bs4 import BeautifulSoup, Comment, Tag
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth  # noqa: F401
from urllib.parse import urlparse, urlunparse

from src.core.config import settings

logger = logging.getLogger(__name__)


def strip_url_hash(url: str) -> str:
    """
    Strip hash fragments from URL to avoid 403 errors from Pro-Football-Reference.

    Example:
        https://example.com/page#all_team_stats -> https://example.com/page

    Args:
        url: URL that may contain hash fragment

    Returns:
        URL without hash fragment
    """
    parsed = urlparse(url)
    # Reconstruct URL without fragment
    return urlunparse(
        (
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            parsed.query,
            "",  # Remove fragment
        )
    )


def get_random_user_agent() -> str:
    """
    Return a random user-agent from the configured pool.

    Returns:
        Random user-agent string
    """
    return random.choice(settings.SCRAPE_USER_AGENTS)


def get_random_proxy() -> Optional[str]:
    """
    Return a random proxy from the configured pool if proxy rotation is enabled.

    Returns:
        Random proxy URL or None if proxy rotation is disabled or no proxies configured
    """
    if not settings.SCRAPE_USE_PROXY or not settings.SCRAPE_PROXY_LIST:
        return None
    return random.choice(settings.SCRAPE_PROXY_LIST)


def clean_value(v):
    """
    Convert pandas/numpy types to pure Python and handle NaN values.

    Args:
        v: Value to clean (may be pandas/numpy type)

    Returns:
        Pure Python value, or None if NaN/NA
    """
    try:
        if pd.isna(v):
            return None
    except (TypeError, ValueError):
        pass

    if isinstance(v, np.generic):
        return v.item()

    return v


def fetch_page_with_selenium(url: str) -> str:
    """
    Fetch a page using Selenium stealth to bypass Cloudflare/bot detection.

    Includes: headless Chrome, anti-automation flags, random user-agent,
    optional proxy, Cloudflare wait, selenium_stealth integration,
    rate limiting via SCRAPE_DELAY_SECONDS.

    Args:
        url: URL to fetch

    Returns:
        Page source HTML string
    """
    clean_url = strip_url_hash(url)
    if clean_url != url:
        logger.info(f"Stripped hash fragment from URL: {url} -> {clean_url}")
        url = clean_url

    time.sleep(settings.SCRAPE_DELAY_SECONDS)

    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-minimized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    user_agent = get_random_user_agent()
    options.add_argument(f"user-agent={user_agent}")
    logger.debug(f"Using user-agent: {user_agent[:50]}...")

    proxy = get_random_proxy()
    if proxy:
        options.add_argument(f"--proxy-server={proxy}")
        logger.debug(f"Using proxy: {proxy}")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options,
    )

    driver.set_page_load_timeout(settings.SCRAPE_REQUEST_TIMEOUT)

    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )

    try:
        driver.get(url)
        time.sleep(10)  # Wait for Cloudflare challenge to auto-resolve

        if "Just a moment" in driver.title:
            logger.info("Waiting for Cloudflare challenge...")
            time.sleep(15)

        page_source = driver.page_source
        logger.info(
            f"Page loaded - Title: {driver.title}, Length: {len(page_source)} chars"
        )
        return page_source
    finally:
        driver.quit()


def find_pfr_table(page_source: str, table_id: str) -> Optional[Tag]:
    """
    Find a table by ID in PFR HTML, checking visible DOM first then HTML comments.

    Pro-Football-Reference hides some tables inside HTML comments;
    this function checks both locations.

    Args:
        page_source: Raw HTML page source
        table_id: The ID attribute of the target table

    Returns:
        BeautifulSoup Tag for the table, or None if not found
    """
    soup = BeautifulSoup(page_source, "lxml")

    # Check visible DOM first
    table = soup.find("table", id=table_id)
    if table is not None and isinstance(table, Tag):
        return table

    # Check HTML comments (PFR hides tables in comments)
    comments = soup.find_all(string=lambda x: isinstance(x, Comment))
    for c in comments:
        if table_id in c:
            comment_soup = BeautifulSoup(c, "lxml")
            table = comment_soup.find("table", id=table_id)
            if table is not None and isinstance(table, Tag):
                return table

    return None


def retry_with_backoff(
    func: Callable,
    *args,
    max_retries: Optional[int] = None,
    retry_delays: Optional[List[int]] = None,
    url: Optional[str] = None,
    **kwargs,
) -> Any:
    """
    Execute a function with exponential backoff retry logic.

    Logs structured data for each attempt including URL, status, duration, and success/failure.

    Args:
        func: Function to execute
        *args: Positional arguments for func
        max_retries: Maximum number of retry attempts (defaults to settings.SCRAPE_MAX_RETRIES)
        retry_delays: List of delays in seconds between retries (defaults to settings.SCRAPE_RETRY_DELAYS)
        url: URL being scraped (for logging purposes)
        **kwargs: Keyword arguments for func

    Returns:
        Result of successful function execution

    Raises:
        Exception: Last exception if all retries failed
    """
    if max_retries is None:
        max_retries = settings.SCRAPE_MAX_RETRIES

    if retry_delays is None:
        retry_delays = settings.SCRAPE_RETRY_DELAYS

    last_exception = None

    for attempt in range(max_retries):
        start_time = time.time()

        try:
            logger.info(
                "Scrape attempt",
                extra={
                    "url": url,
                    "attempt": attempt + 1,
                    "max_retries": max_retries,
                },
            )

            result = func(*args, **kwargs)

            duration = time.time() - start_time
            logger.info(
                "Scrape succeeded",
                extra={
                    "url": url,
                    "attempt": attempt + 1,
                    "duration_seconds": round(duration, 2),
                    "status": "success",
                },
            )

            return result

        except Exception as e:
            last_exception = e
            duration = time.time() - start_time

            logger.warning(
                f"Scrape attempt {attempt + 1}/{max_retries} failed: {str(e)}",
                extra={
                    "url": url,
                    "attempt": attempt + 1,
                    "max_retries": max_retries,
                    "duration_seconds": round(duration, 2),
                    "status": "failure",
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
            )

            # If this wasn't the last attempt, wait before retrying
            if attempt < max_retries - 1:
                # Use configured delay if available, otherwise use default exponential backoff
                if attempt < len(retry_delays):
                    delay = retry_delays[attempt]
                else:
                    # Fallback: exponential backoff if we run out of configured delays
                    delay = retry_delays[-1] * (2 ** (attempt - len(retry_delays) + 1))

                logger.info(
                    f"Retrying in {delay} seconds...",
                    extra={
                        "url": url,
                        "retry_delay_seconds": delay,
                        "next_attempt": attempt + 2,
                    },
                )
                time.sleep(delay)

    # All retries exhausted
    logger.error(
        f"All {max_retries} scrape attempts failed",
        extra={
            "url": url,
            "status": "failed",
            "final_error": str(last_exception),
            "final_error_type": type(last_exception).__name__,
        },
    )

    if last_exception is not None:
        raise last_exception
    raise RuntimeError(f"All {max_retries} scrape attempts failed")
