"""
Test the Excel scraper service.

These are integration tests that require network access and
optionally a database connection. They are skipped in CI by default.
"""

import pytest
import pandas as pd
from src.services.excel_scraper_service import (
    read_excel_urls,
    extract_tables_from_url,
    add_metadata_columns,
    scrape_from_excel,
)


@pytest.mark.integration
def test_excel_reader(tmp_path):
    """Test reading URLs from Excel file."""
    # Create a test Excel file
    test_data = {
        "url": ["https://example.com/stats"],
        "season": [2024],
        "entity_type": ["league"],
        "table_type": ["team_stats"],
    }
    test_file = tmp_path / "test_urls.xlsx"
    pd.DataFrame(test_data).to_excel(test_file, index=False)

    df = read_excel_urls(str(test_file))
    assert len(df) == 1
    assert df.iloc[0]["url"] == "https://example.com/stats"
    assert df.iloc[0]["season"] == 2024


@pytest.mark.integration
def test_table_extraction():
    """Test extracting tables from a URL (requires network)."""
    test_url = "https://www.pro-football-reference.com/years/2024/"
    tables = extract_tables_from_url(test_url)
    assert isinstance(tables, list)
    if len(tables) > 0:
        assert "table_id" in tables[0]
        assert "dataframe" in tables[0]


@pytest.mark.integration
def test_full_scrape(tmp_path):
    """Test the full scraping pipeline (requires network + DB)."""
    test_data = {
        "url": ["https://www.pro-football-reference.com/years/2024/"],
        "season": [2024],
        "entity_type": ["league"],
        "table_type": ["team_stats"],
    }
    test_file = tmp_path / "test_minimal.xlsx"
    pd.DataFrame(test_data).to_excel(test_file, index=False)

    # This test requires a running database, skip if not available
    pytest.skip("Requires database connection")
