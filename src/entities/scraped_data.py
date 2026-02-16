"""
Entity for tracking scraped data metadata.
This tracks what URLs have been scraped and when.
"""

from __future__ import annotations

from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from src.entities.base import Base


class ScrapedData(Base):
    """
    Tracks metadata about scraped URLs and tables.

    The actual scraped data is stored in dynamically created tables
    with the pattern: scraped_{table_id}

    This table tracks what was scraped, when, and with what metadata.
    """

    __tablename__ = "scraped_data_metadata"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_url = Column(Text, nullable=False, index=True)
    table_id = Column(String(255), nullable=False, index=True)
    table_name = Column(String(255), nullable=True)
    scraped_at = Column(DateTime, nullable=False, default=datetime.now)

    # Optional metadata from Excel
    season = Column(Integer, nullable=True)
    entity_type = Column(String(100), nullable=True)
    table_type = Column(String(100), nullable=True)

    # Stats
    rows_scraped = Column(Integer, nullable=True)
    source_type = Column(String(50), nullable=True)  # 'visible' or 'comment'
