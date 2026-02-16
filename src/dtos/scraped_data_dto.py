"""
DTOs for scraped data operations.
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ScrapedDataMetadataCreate(BaseModel):
    """DTO for creating scraped data metadata records."""

    source_url: str
    table_id: str
    table_name: Optional[str] = None
    scraped_at: datetime
    season: Optional[int] = None
    entity_type: Optional[str] = None
    table_type: Optional[str] = None
    rows_scraped: Optional[int] = None
    source_type: Optional[str] = None


class TableInfo(BaseModel):
    """DTO for table information extracted from URLs."""

    table_id: str
    table_name: str
    source: str  # 'visible' or 'comment'
