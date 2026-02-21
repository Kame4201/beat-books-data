"""
Unit tests for scraper utility functions.

Tests retry logic, URL processing, user-agent rotation, and error handling.
"""

import pytest
import time
from unittest.mock import patch, MagicMock
from src.core.scraper_utils import (
    strip_url_hash,
    get_random_user_agent,
    get_random_proxy,
    retry_with_backoff,
)
from src.core.config import settings


class TestStripUrlHash:
    """Tests for URL hash fragment stripping."""

    def test_strip_hash_from_url(self):
        """Test that hash fragments are removed from URLs."""
        url = (
            "https://www.pro-football-reference.com/years/2023/index.htm#all_team_stats"
        )
        expected = "https://www.pro-football-reference.com/years/2023/index.htm"
        assert strip_url_hash(url) == expected

    def test_strip_hash_with_query_params(self):
        """Test that hash removal preserves query parameters."""
        url = "https://example.com/page?param=value#section"
        expected = "https://example.com/page?param=value"
        assert strip_url_hash(url) == expected

    def test_url_without_hash_unchanged(self):
        """Test that URLs without hash fragments are unchanged."""
        url = "https://www.pro-football-reference.com/teams/mia/2023.htm"
        assert strip_url_hash(url) == url

    def test_url_with_empty_hash(self):
        """Test that URLs with empty hash (#) have it removed."""
        url = "https://example.com/page#"
        expected = "https://example.com/page"
        assert strip_url_hash(url) == expected

    def test_complex_url_with_hash(self):
        """Test complex URL with path, params, query, and fragment."""
        url = "https://example.com/path/to/page;params?query=1&other=2#fragment"
        expected = "https://example.com/path/to/page;params?query=1&other=2"
        assert strip_url_hash(url) == expected


class TestUserAgentRotation:
    """Tests for user-agent rotation."""

    def test_get_random_user_agent_returns_string(self):
        """Test that get_random_user_agent returns a string."""
        ua = get_random_user_agent()
        assert isinstance(ua, str)
        assert len(ua) > 0

    def test_get_random_user_agent_from_pool(self):
        """Test that returned user-agent is from configured pool."""
        ua = get_random_user_agent()
        assert ua in settings.SCRAPE_USER_AGENTS

    def test_user_agent_pool_has_multiple_entries(self):
        """Test that user-agent pool has at least 10 entries as required."""
        assert len(settings.SCRAPE_USER_AGENTS) >= 10

    def test_user_agents_are_browser_like(self):
        """Test that all user-agents look like real browser strings."""
        for ua in settings.SCRAPE_USER_AGENTS:
            assert "Mozilla" in ua
            assert any(
                browser in ua for browser in ["Chrome", "Firefox", "Safari", "Edge"]
            )


class TestProxyRotation:
    """Tests for proxy rotation."""

    def test_get_random_proxy_when_disabled(self):
        """Test that get_random_proxy returns None when proxy rotation is disabled."""
        with patch.object(settings, "SCRAPE_USE_PROXY", False):
            assert get_random_proxy() is None

    def test_get_random_proxy_when_enabled_but_empty_list(self):
        """Test that get_random_proxy returns None when proxy list is empty."""
        with patch.object(settings, "SCRAPE_USE_PROXY", True):
            with patch.object(settings, "SCRAPE_PROXY_LIST", []):
                assert get_random_proxy() is None

    def test_get_random_proxy_when_enabled_with_proxies(self):
        """Test that get_random_proxy returns a proxy when enabled."""
        test_proxies = ["http://proxy1:8080", "http://proxy2:8080"]
        with patch.object(settings, "SCRAPE_USE_PROXY", True):
            with patch.object(settings, "SCRAPE_PROXY_LIST", test_proxies):
                proxy = get_random_proxy()
                assert proxy in test_proxies


class TestRetryWithBackoff:
    """Tests for retry logic with exponential backoff."""

    def test_successful_execution_on_first_try(self):
        """Test that function executes successfully without retries."""
        mock_func = MagicMock(return_value="success")

        result = retry_with_backoff(mock_func, "arg1", url="http://test.com")

        assert result == "success"
        assert mock_func.call_count == 1

    def test_retry_after_single_failure(self):
        """Test that function retries after a single failure."""
        mock_func = MagicMock(side_effect=[Exception("First fail"), "success"])

        with patch("time.sleep"):  # Mock sleep to speed up test
            result = retry_with_backoff(
                mock_func, max_retries=2, retry_delays=[1], url="http://test.com"
            )

        assert result == "success"
        assert mock_func.call_count == 2

    def test_retry_with_exponential_backoff(self):
        """Test that retry uses exponential backoff delays."""
        mock_func = MagicMock(
            side_effect=[Exception("Fail 1"), Exception("Fail 2"), "success"]
        )

        sleep_times = []

        def capture_sleep(seconds):
            sleep_times.append(seconds)

        with patch("time.sleep", side_effect=capture_sleep):
            result = retry_with_backoff(
                mock_func,
                max_retries=3,
                retry_delays=[30, 60, 120],
                url="http://test.com",
            )

        assert result == "success"
        assert mock_func.call_count == 3
        assert sleep_times == [30, 60]  # Two sleeps between 3 attempts

    def test_all_retries_exhausted(self):
        """Test that exception is raised when all retries are exhausted."""
        mock_func = MagicMock(side_effect=Exception("Always fails"))

        with patch("time.sleep"):
            with pytest.raises(Exception, match="Always fails"):
                retry_with_backoff(
                    mock_func,
                    max_retries=3,
                    retry_delays=[1, 2, 4],
                    url="http://test.com",
                )

        assert mock_func.call_count == 3

    def test_uses_default_settings_when_not_specified(self):
        """Test that function uses default settings from config."""
        mock_func = MagicMock(side_effect=[Exception("Fail"), "success"])

        with patch("time.sleep"):
            result = retry_with_backoff(mock_func, url="http://test.com")

        assert result == "success"
        # Should use settings.SCRAPE_MAX_RETRIES (default 3)
        assert mock_func.call_count == 2

    def test_retry_with_custom_max_retries(self):
        """Test that custom max_retries parameter is respected."""
        mock_func = MagicMock(side_effect=Exception("Always fails"))

        with patch("time.sleep"):
            with pytest.raises(Exception):
                retry_with_backoff(
                    mock_func, max_retries=5, retry_delays=[1], url="http://test.com"
                )

        assert mock_func.call_count == 5

    def test_retry_logs_structured_data(self, caplog):
        """Test that retry logic logs structured data for each attempt."""
        import logging

        caplog.set_level(logging.INFO)

        mock_func = MagicMock(side_effect=[Exception("Fail"), "success"])

        with patch("time.sleep"):
            retry_with_backoff(
                mock_func, max_retries=2, retry_delays=[1], url="http://test.com"
            )

        # Check that appropriate log messages were created
        log_messages = [record.message for record in caplog.records]
        assert any("Scrape attempt" in msg for msg in log_messages)
        assert any("Scrape succeeded" in msg for msg in log_messages)

    def test_retry_passes_args_and_kwargs(self):
        """Test that retry_with_backoff correctly passes arguments to function."""
        mock_func = MagicMock(return_value="success")

        result = retry_with_backoff(
            mock_func,
            "arg1",
            "arg2",
            kwarg1="value1",
            kwarg2="value2",
            url="http://test.com",
        )

        assert result == "success"
        mock_func.assert_called_once_with(
            "arg1", "arg2", kwarg1="value1", kwarg2="value2"
        )

    def test_403_error_handling(self):
        """Test that 403 errors are properly logged and retried."""

        class Http403Error(Exception):
            pass

        mock_func = MagicMock(side_effect=[Http403Error("403 Forbidden"), "success"])

        with patch("time.sleep"):
            result = retry_with_backoff(
                mock_func,
                max_retries=2,
                retry_delays=[30],
                url="http://test.com#all_team_stats",
            )

        assert result == "success"
        assert mock_func.call_count == 2


class TestConfigurationSettings:
    """Tests for scraping configuration settings."""

    def test_scrape_delay_seconds_configured(self):
        """Test that SCRAPE_DELAY_SECONDS is properly configured."""
        assert hasattr(settings, "SCRAPE_DELAY_SECONDS")
        assert settings.SCRAPE_DELAY_SECONDS > 0

    def test_scrape_request_timeout_configured(self):
        """Test that SCRAPE_REQUEST_TIMEOUT is properly configured."""
        assert hasattr(settings, "SCRAPE_REQUEST_TIMEOUT")
        assert settings.SCRAPE_REQUEST_TIMEOUT > 0

    def test_scrape_max_retries_configured(self):
        """Test that SCRAPE_MAX_RETRIES is properly configured."""
        assert hasattr(settings, "SCRAPE_MAX_RETRIES")
        assert settings.SCRAPE_MAX_RETRIES >= 3

    def test_scrape_retry_delays_configured(self):
        """Test that SCRAPE_RETRY_DELAYS is properly configured."""
        assert hasattr(settings, "SCRAPE_RETRY_DELAYS")
        assert len(settings.SCRAPE_RETRY_DELAYS) >= 3
        # Test exponential backoff: [30, 60, 120]
        assert settings.SCRAPE_RETRY_DELAYS == [30, 60, 120]

    def test_scrape_user_agents_configured(self):
        """Test that SCRAPE_USER_AGENTS pool is properly configured."""
        assert hasattr(settings, "SCRAPE_USER_AGENTS")
        assert len(settings.SCRAPE_USER_AGENTS) >= 10

    def test_proxy_settings_configured(self):
        """Test that proxy settings are properly configured."""
        assert hasattr(settings, "SCRAPE_USE_PROXY")
        assert hasattr(settings, "SCRAPE_PROXY_LIST")
        assert isinstance(settings.SCRAPE_USE_PROXY, bool)
        assert isinstance(settings.SCRAPE_PROXY_LIST, list)
