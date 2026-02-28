"""
Entity for tracking batch scrape jobs.
This tracks the status and progress of batch scraping operations.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.entities.base import Base


class ScrapeJob(Base):
    """
    Tracks batch scrape job metadata and progress.

    A scrape job represents a batch of URLs to be scraped,
    with tracking of progress, failures, and completion status.
    """

    __tablename__ = "scrape_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending", index=True
    )  # pending, running, complete, failed

    total_urls: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    processed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    errors: Mapped[list | None] = mapped_column(
        JSON, nullable=True
    )  # Store error details as JSON

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
