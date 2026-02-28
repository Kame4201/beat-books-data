"""
Service for batch scraping operations with job tracking.

This service orchestrates batch scraping of multiple team/year combinations,
tracks progress via ScrapeJobRepository, handles failures gracefully, and
respects rate limiting via settings.SCRAPE_DELAY_SECONDS (configurable in
src/core/config.py, default 60s).

Architecture:
    BatchScrapeService -> ScrapeJobRepository -> PostgreSQL (scrape_jobs table)
    BatchScrapeService -> scrape_and_store()  -> individual scrape logic

Job lifecycle:  pending -> running -> complete
    Partial failures are recorded but do not abort the batch.
    Each target is processed sequentially with a configurable delay between
    requests to respect Pro-Football-Reference rate limits.
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from src.core.config import settings
from src.core.database import SessionLocal
from src.repositories.scrape_job_repo import ScrapeJobRepository
from src.services.scrape_service import scrape_and_store


class BatchScrapeService:
    """
    Service for batch scraping with job tracking.

    Handles:
    - Creating and tracking scrape jobs
    - Sequential processing with rate limiting
    - Graceful error handling (partial failures don't stop batch)
    - Progress updates
    """

    def __init__(self, session: Session) -> None:
        self.session = session
        self.job_repo = ScrapeJobRepository(session)

    async def create_batch_job(self, targets: list[dict[str, Any]]) -> int:
        """
        Create a new batch scrape job.

        Args:
            targets: List of dicts with 'team' and 'year' keys
                    Example: [{"team": "chiefs", "year": 2024}, ...]

        Returns:
            Job ID for tracking

        Raises:
            ValueError: If targets list is empty or invalid
        """
        if not targets:
            raise ValueError("Targets list cannot be empty")

        # Validate targets format
        for target in targets:
            if "team" not in target or "year" not in target:
                raise ValueError("Each target must have 'team' and 'year' keys")

        # Create job record
        job = self.job_repo.create_job(total_urls=len(targets))
        return job.id

    async def execute_batch_job(
        self, job_id: int, targets: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        Execute a batch scrape job.

        Processes targets sequentially with configured rate limiting.
        Updates job status and progress as it goes.
        Continues on partial failures.

        Args:
            job_id: ID of the job to execute
            targets: List of dicts with 'team' and 'year' keys

        Returns:
            Dict with job results summary

        Raises:
            ValueError: If job not found
        """
        job = self.job_repo.get_by_id(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")

        # Mark job as running
        self.job_repo.update_job_status(job_id, "running")

        succeeded = 0
        failed_count = 0
        errors: list[dict[str, Any]] = []

        # Process each target sequentially
        for idx, target in enumerate(targets):
            team = target["team"]
            year = target["year"]

            try:
                # Scrape and store
                await scrape_and_store(team, year)

                # Increment processed count
                self.job_repo.increment_processed(job_id)
                succeeded += 1

            except Exception as e:
                # Record failure but continue processing
                error_info = {
                    "target": target,
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                }

                self.job_repo.increment_failed(job_id, error_info)
                failed_count += 1
                errors.append(error_info)

            # Rate limiting: configurable delay between requests to avoid
            # 403 bans from Pro-Football-Reference. Uses settings.SCRAPE_DELAY_SECONDS
            # (default 60s, overridable via SCRAPE_DELAY_SECONDS env var).
            # Skip the delay after the last target to avoid unnecessary wait.
            if idx < len(targets) - 1:
                await asyncio.sleep(settings.SCRAPE_DELAY_SECONDS)

        # Mark job as complete
        self.job_repo.mark_complete(job_id)

        return {
            "job_id": job_id,
            "total": len(targets),
            "succeeded": succeeded,
            "failed": failed_count,
            "errors": errors,
        }

    async def run_batch_scrape(self, targets: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Convenience method to create and execute a batch scrape in one call.

        Args:
            targets: List of dicts with 'team' and 'year' keys
                    Example: [{"team": "chiefs", "year": 2024}, ...]

        Returns:
            Dict with job results summary
        """
        job_id = await self.create_batch_job(targets)
        return await self.execute_batch_job(job_id, targets)

    def get_job_status(self, job_id: int) -> dict[str, Any] | None:
        """
        Get the current status of a batch scrape job.

        Args:
            job_id: ID of the job to query

        Returns:
            Dict with job status information, or None if not found
        """
        job = self.job_repo.get_by_id(job_id)
        if not job:
            return None

        return {
            "job_id": job.id,
            "status": job.status,
            "total_urls": job.total_urls,
            "processed": job.processed,
            "failed": job.failed,
            "errors": job.errors,
            "created_at": job.created_at.isoformat(),
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
        }

    def list_jobs(
        self, status: str | None = None, limit: int = 100
    ) -> list[dict[str, Any]]:
        """
        List batch scrape jobs, optionally filtered by status.

        Args:
            status: Optional status filter (pending, running, complete, failed)
            limit: Maximum number of jobs to return

        Returns:
            List of job status dicts
        """
        if status:
            jobs = self.job_repo.get_jobs_by_status(status, limit)
        else:
            jobs = self.job_repo.get_all_jobs(limit)

        return [
            {
                "job_id": job.id,
                "status": job.status,
                "total_urls": job.total_urls,
                "processed": job.processed,
                "failed": job.failed,
                "created_at": job.created_at.isoformat(),
                "completed_at": (
                    job.completed_at.isoformat() if job.completed_at else None
                ),
            }
            for job in jobs
        ]


# Convenience function for standalone use
async def batch_scrape(targets: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Convenience function to run a batch scrape with a new session.

    Args:
        targets: List of dicts with 'team' and 'year' keys

    Returns:
        Dict with job results summary
    """
    db = SessionLocal()
    try:
        service = BatchScrapeService(db)
        return await service.run_batch_scrape(targets)
    finally:
        db.close()
