"""
Service for batch scraping operations with job tracking.

This service orchestrates batch scraping of multiple team/year combinations,
tracks progress, handles failures gracefully, and respects rate limiting.
"""
from __future__ import annotations

import asyncio
from typing import List, Dict, Optional
from datetime import datetime

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

    async def create_batch_job(
        self,
        targets: List[Dict[str, any]]
    ) -> int:
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
            if 'team' not in target or 'year' not in target:
                raise ValueError(
                    "Each target must have 'team' and 'year' keys"
                )

        # Create job record
        job = self.job_repo.create_job(total_urls=len(targets))
        return job.id

    async def execute_batch_job(
        self,
        job_id: int,
        targets: List[Dict[str, any]]
    ) -> Dict[str, any]:
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
        self.job_repo.update_job_status(job_id, 'running')

        results = {
            'job_id': job_id,
            'total': len(targets),
            'succeeded': 0,
            'failed': 0,
            'errors': []
        }

        # Process each target sequentially
        for idx, target in enumerate(targets):
            team = target['team']
            year = target['year']

            try:
                # Scrape and store
                await scrape_and_store(team, year)

                # Increment processed count
                self.job_repo.increment_processed(job_id)
                results['succeeded'] += 1

            except Exception as e:
                # Record failure but continue processing
                error_info = {
                    'target': target,
                    'error': str(e),
                    'timestamp': datetime.utcnow().isoformat()
                }

                self.job_repo.increment_failed(job_id, error_info)
                results['failed'] += 1
                results['errors'].append(error_info)

            # Rate limiting - wait between requests
            # Don't wait after the last item
            if idx < len(targets) - 1:
                await asyncio.sleep(settings.SCRAPE_DELAY_SECONDS)

        # Mark job as complete
        self.job_repo.mark_complete(job_id)

        return results

    async def run_batch_scrape(
        self,
        targets: List[Dict[str, any]]
    ) -> Dict[str, any]:
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

    def get_job_status(self, job_id: int) -> Optional[Dict[str, any]]:
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
            'job_id': job.id,
            'status': job.status,
            'total_urls': job.total_urls,
            'processed': job.processed,
            'failed': job.failed,
            'errors': job.errors,
            'created_at': job.created_at.isoformat(),
            'completed_at': job.completed_at.isoformat() if job.completed_at else None
        }

    def list_jobs(
        self,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, any]]:
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
                'job_id': job.id,
                'status': job.status,
                'total_urls': job.total_urls,
                'processed': job.processed,
                'failed': job.failed,
                'created_at': job.created_at.isoformat(),
                'completed_at': job.completed_at.isoformat() if job.completed_at else None
            }
            for job in jobs
        ]


# Convenience function for standalone use
async def batch_scrape(
    targets: List[Dict[str, any]]
) -> Dict[str, any]:
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
