"""
Repository for handling scrape job operations.

This repository manages CRUD operations for ScrapeJob entities.
All SQL lives here -- services must call these methods rather than
executing queries directly.

Concurrency note: increment_processed() and increment_failed() use
ORM-level read-then-write, which is safe for the current sequential
BatchScrapeService execution model. If concurrent workers are added
in the future, these should be converted to atomic SQL UPDATE
statements (e.g., UPDATE ... SET processed = processed + 1) to
avoid lost-update race conditions.
"""
from __future__ import annotations

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select, update

from src.entities.scrape_job import ScrapeJob
from src.repositories.base_repo import BaseRepository


class ScrapeJobRepository(BaseRepository[ScrapeJob]):
    """
    Repository for scrape job operations.

    Extends BaseRepository with specialized methods for
    job tracking and status updates.
    """

    def __init__(self, session: Session) -> None:
        super().__init__(session=session, model=ScrapeJob)

    def create_job(self, total_urls: int) -> ScrapeJob:
        """
        Create a new scrape job with pending status.

        Args:
            total_urls: Total number of URLs in this job

        Returns:
            Created ScrapeJob entity
        """
        job = ScrapeJob(
            status='pending',
            total_urls=total_urls,
            processed=0,
            failed=0,
            errors=None
        )
        return self.create(job, commit=True)

    def update_job_status(
        self,
        job_id: int,
        status: str,
        commit: bool = True
    ) -> Optional[ScrapeJob]:
        """
        Update the status of a job.

        Args:
            job_id: ID of the job to update
            status: New status (pending, running, complete, failed)
            commit: Whether to commit the transaction

        Returns:
            Updated ScrapeJob entity or None if not found
        """
        job = self.get_by_id(job_id)
        if job:
            job.status = status
            return self.update(job, commit=commit)
        return None

    def increment_processed(
        self,
        job_id: int,
        commit: bool = True
    ) -> Optional[ScrapeJob]:
        """
        Increment the processed count for a job.

        Args:
            job_id: ID of the job to update
            commit: Whether to commit the transaction

        Returns:
            Updated ScrapeJob entity or None if not found
        """
        job = self.get_by_id(job_id)
        if job:
            job.processed += 1
            return self.update(job, commit=commit)
        return None

    def increment_failed(
        self,
        job_id: int,
        error_info: dict,
        commit: bool = True
    ) -> Optional[ScrapeJob]:
        """
        Increment the failed count and add error information.

        Args:
            job_id: ID of the job to update
            error_info: Dictionary containing error details
            commit: Whether to commit the transaction

        Returns:
            Updated ScrapeJob entity or None if not found
        """
        job = self.get_by_id(job_id)
        if job:
            job.failed += 1

            # Initialize errors list if needed
            if job.errors is None:
                job.errors = []

            # Append new error
            job.errors.append(error_info)

            return self.update(job, commit=commit)
        return None

    def mark_complete(
        self,
        job_id: int,
        commit: bool = True
    ) -> Optional[ScrapeJob]:
        """
        Mark a job as complete and set completion timestamp.

        Args:
            job_id: ID of the job to complete
            commit: Whether to commit the transaction

        Returns:
            Updated ScrapeJob entity or None if not found
        """
        from datetime import datetime

        job = self.get_by_id(job_id)
        if job:
            job.status = 'complete'
            job.completed_at = datetime.utcnow()
            return self.update(job, commit=commit)
        return None

    def get_jobs_by_status(
        self,
        status: str,
        limit: int = 100
    ) -> List[ScrapeJob]:
        """
        Get all jobs with a specific status.

        Args:
            status: Status to filter by
            limit: Maximum number of jobs to return

        Returns:
            List of ScrapeJob entities
        """
        stmt = select(ScrapeJob).where(
            ScrapeJob.status == status
        ).limit(limit)
        return list(self.session.execute(stmt).scalars().all())

    def get_all_jobs(self, limit: int = 100) -> List[ScrapeJob]:
        """
        Get all scrape jobs.

        Args:
            limit: Maximum number of jobs to return

        Returns:
            List of ScrapeJob entities
        """
        return self.list(limit=limit)
