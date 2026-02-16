"""
Excel-based URL scraper service for Pro-Football-Reference data.

This service reads URLs from an Excel file and scrapes stat tables from each URL,
then stores them in the database with metadata using the repository layer.
"""

import pandas as pd
import time
import logging
from io import StringIO
from bs4 import BeautifulSoup, Comment
from datetime import datetime
from typing import List, Dict, Any
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth

from src.core.database import SessionLocal
from src.core.config import settings
from src.core.scraper_utils import strip_url_hash, get_random_user_agent, get_random_proxy, retry_with_backoff
from src.repositories.scraped_data_repo import ScrapedDataRepository
from src.dtos.scraped_data_dto import ScrapedDataMetadataCreate

logger = logging.getLogger(__name__)


def read_excel_urls(excel_path: str) -> pd.DataFrame:
    """
    Read URLs and metadata from Excel file.

    Args:
        excel_path: Path to Excel file

    Returns:
        DataFrame with columns: url (required), season, entity_type, table_type (optional)

    Raises:
        ValueError: If 'url' column is missing
        FileNotFoundError: If Excel file doesn't exist
    """
    # Read all sheets and concatenate them
    excel_file = pd.ExcelFile(excel_path)
    all_dfs = []

    for sheet_name in excel_file.sheet_names:
        df = pd.read_excel(excel_path, sheet_name=sheet_name)
        all_dfs.append(df)

    # Combine all sheets
    combined_df = pd.concat(all_dfs, ignore_index=True)

    # Validate required column
    if 'url' not in combined_df.columns:
        raise ValueError("Excel file must contain 'url' column")

    # Remove rows with empty URLs
    combined_df = combined_df[combined_df['url'].notna()]

    return combined_df


def extract_tables_from_url(url: str) -> List[Dict[str, Any]]:
    """
    Fetch HTML from URL using Selenium and extract all stat tables.

    Uses headless Chrome to bypass Pro-Football-Reference bot detection.
    Includes retry logic, user-agent rotation, and structured logging.

    Args:
        url: Pro-Football-Reference URL to scrape

    Returns:
        List of dictionaries containing table data and metadata
        Each dict has keys: table_id, table_name, dataframe, source
    """
    # Strip hash fragments to avoid 403 errors
    clean_url = strip_url_hash(url)
    if clean_url != url:
        logger.info(f"Stripped hash fragment from URL: {url} -> {clean_url}")
        url = clean_url

    # Add delay to be respectful to the server and avoid getting blocked
    time.sleep(settings.SCRAPE_DELAY_SECONDS)

    # Use Selenium in visible mode to bypass Cloudflare bot detection
    # (Cloudflare blocks headless browsers but allows visible Chrome)
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-minimized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # Set random user-agent from pool
    user_agent = get_random_user_agent()
    options.add_argument(f"user-agent={user_agent}")
    logger.debug(f"Using user-agent: {user_agent[:50]}...")

    # Configure proxy if enabled
    proxy = get_random_proxy()
    if proxy:
        options.add_argument(f"--proxy-server={proxy}")
        logger.debug(f"Using proxy: {proxy}")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options,
    )

    # Set page load timeout
    driver.set_page_load_timeout(settings.SCRAPE_REQUEST_TIMEOUT)

    # Hide webdriver flag
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    try:
        driver.get(url)
        time.sleep(10)  # Wait for Cloudflare challenge to auto-resolve

        # Check if still on Cloudflare challenge
        if "Just a moment" in driver.title:
            logger.info("Waiting for Cloudflare challenge...")
            time.sleep(15)

        page_source = driver.page_source
        logger.info(f"Page loaded - Title: {driver.title}, Length: {len(page_source)} chars")
    finally:
        driver.quit()

    soup = BeautifulSoup(page_source, 'lxml')

    extracted_tables = []

    # Method 1: Extract visible tables (only those with an id attribute)
    visible_tables = soup.find_all('table')
    for table in visible_tables:
        table_id = table.get('id')
        if not table_id:
            continue  # Skip layout tables without IDs
        table_caption = table.find('caption')
        table_name = table_caption.get_text(strip=True) if table_caption else table_id

        try:
            # Convert HTML table to DataFrame
            df = pd.read_html(StringIO(str(table)))[0]

            # Flatten MultiIndex columns if present
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = ['_'.join(str(c).strip() for c in col if str(c) != 'nan' and not str(c).startswith('Unnamed'))
                             or col[0] for col in df.columns.values]

            extracted_tables.append({
                'table_id': table_id,
                'table_name': table_name,
                'dataframe': df,
                'source': 'visible'
            })
        except Exception as e:
            print(f"Warning: Could not parse visible table {table_id}: {e}")
            continue

    # Method 2: Extract tables from HTML comments (PFR often hides tables in comments)
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))
    for comment in comments:
        if 'table' in comment:
            try:
                comment_soup = BeautifulSoup(comment, 'lxml')
                tables = comment_soup.find_all('table')

                for table in tables:
                    table_id = table.get('id', 'unknown_comment')
                    table_caption = table.find('caption')
                    table_name = table_caption.get_text(strip=True) if table_caption else table_id

                    try:
                        df = pd.read_html(StringIO(str(table)))[0]

                        # Flatten MultiIndex columns
                        if isinstance(df.columns, pd.MultiIndex):
                            df.columns = ['_'.join(str(c).strip() for c in col if str(c) != 'nan' and not str(c).startswith('Unnamed'))
                                         or col[0] for col in df.columns.values]

                        extracted_tables.append({
                            'table_id': table_id,
                            'table_name': table_name,
                            'dataframe': df,
                            'source': 'comment'
                        })
                    except Exception as e:
                        print(f"Warning: Could not parse commented table {table_id}: {e}")
                        continue
            except Exception as e:
                print(f"Warning: Could not parse comment: {e}")
                continue

    return extracted_tables


def add_metadata_columns(df: pd.DataFrame, url: str, metadata: Dict[str, Any]) -> pd.DataFrame:
    """
    Add metadata columns to DataFrame.

    Args:
        df: DataFrame to add metadata to
        url: Source URL
        metadata: Additional metadata from Excel row

    Returns:
        DataFrame with added metadata columns
    """
    df = df.copy()

    # Add standard metadata
    df['source_url'] = url
    df['scraped_at'] = datetime.now()

    # Add optional metadata from Excel
    if 'season' in metadata and pd.notna(metadata['season']):
        df['season'] = metadata['season']

    if 'entity_type' in metadata and pd.notna(metadata['entity_type']):
        df['entity_type'] = metadata['entity_type']

    if 'table_type' in metadata and pd.notna(metadata['table_type']):
        df['table_type'] = metadata['table_type']

    return df


# Database operations have been moved to the repository layer
# See src/repositories/scraped_data_repo.py for:
# - create_dynamic_table()
# - upsert_dataframe()
# - delete_by_source_url()
# - insert_dataframe_rows()


async def scrape_from_excel(excel_path: str) -> Dict[str, Any]:
    """
    Main function to scrape URLs from Excel file and store in database.

    Uses the repository layer for all database operations following proper
    architectural patterns with entities, DTOs, and repositories.

    Args:
        excel_path: Path to Excel file containing URLs

    Returns:
        Dictionary with summary of scraping results:
        - urls_processed: Number of URLs attempted
        - urls_success: Number of URLs successfully scraped
        - urls_failed: Number of URLs that failed
        - tables_extracted: Total number of tables extracted
        - rows_inserted: Total number of rows inserted
        - errors: List of error messages
    """
    db = SessionLocal()
    repo = ScrapedDataRepository(db)

    results = {
        'urls_processed': 0,
        'urls_success': 0,
        'urls_failed': 0,
        'tables_extracted': 0,
        'rows_inserted': 0,
        'errors': []
    }

    try:
        # Ensure metadata tracking table exists
        repo.create_metadata_table_if_not_exists()

        # Read URLs from Excel
        urls_df = read_excel_urls(excel_path)
        results['urls_processed'] = len(urls_df)

        # Process each URL
        for idx, row in urls_df.iterrows():
            url = row['url']

            # Extract metadata from Excel row
            metadata = {
                'season': row.get('season'),
                'entity_type': row.get('entity_type'),
                'table_type': row.get('table_type')
            }

            try:
                # Extract tables from URL with retry logic
                tables = retry_with_backoff(
                    extract_tables_from_url,
                    url,
                    url=url
                )
                results['tables_extracted'] += len(tables)

                # Process each table
                for table_info in tables:
                    df = table_info['dataframe']
                    table_id = table_info['table_id']
                    table_name = table_info['table_name']
                    source_type = table_info['source']

                    # Add metadata columns to DataFrame
                    df = add_metadata_columns(df, url, metadata)

                    # Create dynamic table name
                    dynamic_table_name = f"scraped_{table_id}"

                    # Use repository to create table if needed
                    repo.create_dynamic_table(dynamic_table_name, df)

                    # Use repository to upsert data (idempotent)
                    rows = repo.upsert_dataframe(dynamic_table_name, df)
                    results['rows_inserted'] += rows

                    # Track metadata in scraped_data_metadata table using DTO
                    metadata_dto = ScrapedDataMetadataCreate(
                        source_url=url,
                        table_id=table_id,
                        table_name=table_name,
                        scraped_at=datetime.now(),
                        season=metadata.get('season'),
                        entity_type=metadata.get('entity_type'),
                        table_type=metadata.get('table_type'),
                        rows_scraped=rows,
                        source_type=source_type
                    )
                    repo.track_scraped_data(metadata_dto)

                results['urls_success'] += 1

            except Exception as e:
                error_msg = f"Failed to process {url}: {str(e)}"
                results['errors'].append(error_msg)
                results['urls_failed'] += 1
                print(error_msg)
                continue

        return results

    except Exception as e:
        results['errors'].append(f"Fatal error: {str(e)}")
        return results

    finally:
        db.close()
