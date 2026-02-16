"""
Entity for tracking batch scrape jobs.
This tracks the status and progress of batch scraping operations.
"""
from __future__ import annotations

from sqlalchemy import Column, Integer, String, DateTime, JSON
from datetime import datetime
from src.entities.base import Base


class ScrapeJob(Base):
    """
    Tracks batch scrape job metadata and progress.

    A scrape job represents a batch of URLs to be scraped,
    with tracking of progress, failures, and completion status.
    """
    __tablename__ = 'scrape_jobs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    status = Column(
        String(20),
        nullable=False,
        default='pending',
        index=True
    )  # pending, running, complete, failed

    total_urls = Column(Integer, nullable=False, default=0)
    processed = Column(Integer, nullable=False, default=0)
    failed = Column(Integer, nullable=False, default=0)

    errors = Column(JSON, nullable=True)  # Store error details as JSON

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
