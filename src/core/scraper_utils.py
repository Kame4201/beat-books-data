"""
Utility functions for web scraping with retry logic, user-agent rotation, and error handling.
"""

import time
import random
import logging
from typing import Callable, Any, Optional, List
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
    return urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        parsed.query,
        ''  # Remove fragment
    ))


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


def retry_with_backoff(
    func: Callable,
    *args,
    max_retries: Optional[int] = None,
    retry_delays: Optional[List[int]] = None,
    url: Optional[str] = None,
    **kwargs
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
                }
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
                }
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
                }
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
                    }
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
        }
    )

    raise last_exception
