"""Tests for scrapling backend selection in fetch_page()."""

import sys
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture(autouse=True)
def _clear_cached_modules():
    """Remove cached scrapling_fetcher so patches take effect on re-import."""
    mods_to_remove = [
        k for k in sys.modules if "scrapling" in k
    ]
    for m in mods_to_remove:
        del sys.modules[m]
    yield
    mods_to_remove = [
        k for k in sys.modules if "scrapling" in k
    ]
    for m in mods_to_remove:
        del sys.modules[m]


def test_fetch_page_uses_scrapling_when_configured():
    """fetch_page() delegates to scrapling when SCRAPE_BACKEND=scrapling."""
    mock_stealthy = MagicMock()
    mock_response = MagicMock()
    mock_response.html_content = "<html><body>test</body></html>"
    mock_response.status = 200
    mock_stealthy.fetch.return_value = mock_response

    mock_fetchers = MagicMock()
    mock_fetchers.StealthyFetcher = mock_stealthy
    sys.modules["scrapling"] = MagicMock()
    sys.modules["scrapling.fetchers"] = mock_fetchers

    with patch("src.core.config.settings") as mock_settings:
        mock_settings.SCRAPE_BACKEND = "scrapling"
        mock_settings.SCRAPE_DELAY_SECONDS = 0
        mock_settings.SCRAPE_USE_PROXY = False
        mock_settings.SCRAPE_PROXY_LIST = []
        mock_settings.SCRAPLING_FETCHER_TYPE = "stealthy"
        mock_settings.SCRAPLING_TIMEOUT = 30
        mock_settings.SCRAPLING_IMPERSONATE = "chrome"

        from src.core.scrapling_fetcher import fetch_page_with_scrapling

        result = fetch_page_with_scrapling("https://example.com/test")

        assert result == "<html><body>test</body></html>"
        mock_stealthy.fetch.assert_called_once()


def test_fetch_page_uses_fetcher_type():
    """fetch_page_with_scrapling() uses Fetcher when type=fetcher."""
    mock_fetcher_cls = MagicMock()
    mock_response = MagicMock()
    mock_response.html_content = "<html>fetcher</html>"
    mock_response.status = 200
    mock_fetcher_cls.get.return_value = mock_response

    mock_fetchers = MagicMock()
    mock_fetchers.Fetcher = mock_fetcher_cls
    sys.modules["scrapling"] = MagicMock()
    sys.modules["scrapling.fetchers"] = mock_fetchers

    with patch("src.core.config.settings") as mock_settings:
        mock_settings.SCRAPE_BACKEND = "scrapling"
        mock_settings.SCRAPE_DELAY_SECONDS = 0
        mock_settings.SCRAPE_USE_PROXY = False
        mock_settings.SCRAPE_PROXY_LIST = []
        mock_settings.SCRAPLING_FETCHER_TYPE = "fetcher"
        mock_settings.SCRAPLING_TIMEOUT = 30
        mock_settings.SCRAPLING_IMPERSONATE = "chrome"

        from src.core.scrapling_fetcher import fetch_page_with_scrapling

        result = fetch_page_with_scrapling("https://example.com/test")

        assert result == "<html>fetcher</html>"
        mock_fetcher_cls.get.assert_called_once()


def test_fetch_page_raises_on_unknown_backend():
    """fetch_page() raises ValueError for unknown backend."""
    with patch(
        "src.core.scraper_utils.settings"
    ) as mock_settings:
        mock_settings.SCRAPE_BACKEND = "unknown"

        from src.core.scraper_utils import fetch_page

        with pytest.raises(ValueError, match="Unknown SCRAPE_BACKEND"):
            fetch_page("https://example.com")
