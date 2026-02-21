"""
Unit tests for scrape job repository.
"""

import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.entities.base import Base
from src.entities.scrape_job import ScrapeJob
from src.repositories.scrape_job_repo import ScrapeJobRepository


@pytest.fixture
def db_session():
    """Create in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def scrape_job_repo(db_session):
    """Create scrape job repository with test session."""
    return ScrapeJobRepository(db_session)


class TestScrapeJobRepository:
    """Test scrape job repository functionality."""

    def test_create_job(self, scrape_job_repo):
        """Test creating a new scrape job."""
        job = scrape_job_repo.create_job(total_urls=10)

        assert job.id is not None
        assert job.status == "pending"
        assert job.total_urls == 10
        assert job.processed == 0
        assert job.failed == 0
        assert job.errors is None

    def test_update_job_status(self, scrape_job_repo):
        """Test updating job status."""
        job = scrape_job_repo.create_job(total_urls=5)
        original_id = job.id

        updated = scrape_job_repo.update_job_status(original_id, "running")

        assert updated is not None
        assert updated.id == original_id
        assert updated.status == "running"

    def test_update_job_status_not_found(self, scrape_job_repo):
        """Test updating non-existent job."""
        result = scrape_job_repo.update_job_status(999, "running")

        assert result is None

    def test_increment_processed(self, scrape_job_repo):
        """Test incrementing processed count."""
        job = scrape_job_repo.create_job(total_urls=10)
        job_id = job.id

        updated = scrape_job_repo.increment_processed(job_id)

        assert updated is not None
        assert updated.processed == 1

        # Increment again
        updated = scrape_job_repo.increment_processed(job_id)
        assert updated.processed == 2

    def test_increment_failed(self, scrape_job_repo):
        """Test incrementing failed count with error info."""
        job = scrape_job_repo.create_job(total_urls=10)
        job_id = job.id

        error_info = {
            "target": {"team": "chiefs", "year": 2024},
            "error": "Connection timeout",
        }

        updated = scrape_job_repo.increment_failed(job_id, error_info)

        assert updated is not None
        assert updated.failed == 1
        assert len(updated.errors) == 1
        assert updated.errors[0]["error"] == "Connection timeout"

    def test_increment_failed_multiple_errors(self, scrape_job_repo):
        """Test accumulating multiple errors."""
        job = scrape_job_repo.create_job(total_urls=10)
        job_id = job.id

        error1 = {"error": "Error 1"}
        error2 = {"error": "Error 2"}

        scrape_job_repo.increment_failed(job_id, error1)
        updated = scrape_job_repo.increment_failed(job_id, error2)

        assert updated.failed == 2
        assert len(updated.errors) == 2

    def test_mark_complete(self, scrape_job_repo):
        """Test marking job as complete."""
        job = scrape_job_repo.create_job(total_urls=5)
        job_id = job.id

        updated = scrape_job_repo.mark_complete(job_id)

        assert updated is not None
        assert updated.status == "complete"
        assert updated.completed_at is not None

    def test_get_jobs_by_status(self, scrape_job_repo):
        """Test filtering jobs by status."""
        # Create jobs with different statuses
        job1 = scrape_job_repo.create_job(total_urls=5)
        job2 = scrape_job_repo.create_job(total_urls=10)
        job3 = scrape_job_repo.create_job(total_urls=15)

        scrape_job_repo.update_job_status(job1.id, "running")
        scrape_job_repo.update_job_status(job2.id, "running")
        scrape_job_repo.update_job_status(job3.id, "complete")

        running_jobs = scrape_job_repo.get_jobs_by_status("running")

        assert len(running_jobs) == 2
        assert all(job.status == "running" for job in running_jobs)

    def test_get_all_jobs(self, scrape_job_repo):
        """Test getting all jobs."""
        scrape_job_repo.create_job(total_urls=5)
        scrape_job_repo.create_job(total_urls=10)
        scrape_job_repo.create_job(total_urls=15)

        all_jobs = scrape_job_repo.get_all_jobs()

        assert len(all_jobs) == 3

    def test_get_by_id(self, scrape_job_repo):
        """Test retrieving job by ID."""
        job = scrape_job_repo.create_job(total_urls=5)
        job_id = job.id

        retrieved = scrape_job_repo.get_by_id(job_id)

        assert retrieved is not None
        assert retrieved.id == job_id
        assert retrieved.total_urls == 5

    def test_get_by_id_not_found(self, scrape_job_repo):
        """Test retrieving non-existent job."""
        result = scrape_job_repo.get_by_id(999)

        assert result is None
