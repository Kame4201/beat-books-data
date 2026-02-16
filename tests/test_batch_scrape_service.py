"""
Unit tests for batch scrape service.
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from src.services.batch_scrape_service import BatchScrapeService
from src.entities.scrape_job import ScrapeJob


@pytest.fixture
def mock_session():
    """Mock database session."""
    return Mock()


@pytest.fixture
def mock_job_repo(mock_session):
    """Mock scrape job repository."""
    from src.repositories.scrape_job_repo import ScrapeJobRepository
    repo = Mock(spec=ScrapeJobRepository)
    return repo


@pytest.fixture
def batch_service(mock_session, mock_job_repo):
    """Create batch scrape service with mocked dependencies."""
    service = BatchScrapeService(mock_session)
    service.job_repo = mock_job_repo
    return service


class TestBatchScrapeService:
    """Test batch scrape service functionality."""

    @pytest.mark.asyncio
    async def test_create_batch_job_success(self, batch_service, mock_job_repo):
        """Test successful batch job creation."""
        targets = [
            {"team": "chiefs", "year": 2024},
            {"team": "bills", "year": 2024}
        ]

        # Mock job creation
        mock_job = ScrapeJob(
            id=1,
            status='pending',
            total_urls=2,
            processed=0,
            failed=0
        )
        mock_job_repo.create_job.return_value = mock_job

        job_id = await batch_service.create_batch_job(targets)

        assert job_id == 1
        mock_job_repo.create_job.assert_called_once_with(total_urls=2)

    @pytest.mark.asyncio
    async def test_create_batch_job_empty_targets(self, batch_service):
        """Test batch job creation with empty targets list."""
        with pytest.raises(ValueError, match="Targets list cannot be empty"):
            await batch_service.create_batch_job([])

    @pytest.mark.asyncio
    async def test_create_batch_job_invalid_target(self, batch_service):
        """Test batch job creation with invalid target format."""
        targets = [{"team": "chiefs"}]  # Missing 'year' key

        with pytest.raises(ValueError, match="must have 'team' and 'year' keys"):
            await batch_service.create_batch_job(targets)

    @pytest.mark.asyncio
    async def test_execute_batch_job_success(self, batch_service, mock_job_repo):
        """Test successful batch job execution."""
        job_id = 1
        targets = [
            {"team": "chiefs", "year": 2024},
            {"team": "bills", "year": 2024}
        ]

        # Mock job retrieval
        mock_job = ScrapeJob(
            id=job_id,
            status='pending',
            total_urls=2,
            processed=0,
            failed=0
        )
        mock_job_repo.get_by_id.return_value = mock_job

        # Mock scrape_and_store to avoid actual scraping
        with patch('src.services.batch_scrape_service.scrape_and_store', new_callable=AsyncMock) as mock_scrape:
            with patch('asyncio.sleep', new_callable=AsyncMock):
                result = await batch_service.execute_batch_job(job_id, targets)

        assert result['job_id'] == job_id
        assert result['total'] == 2
        assert result['succeeded'] == 2
        assert result['failed'] == 0
        assert len(result['errors']) == 0

        # Verify status updates
        mock_job_repo.update_job_status.assert_called_once_with(job_id, 'running')
        assert mock_job_repo.increment_processed.call_count == 2
        mock_job_repo.mark_complete.assert_called_once_with(job_id)

    @pytest.mark.asyncio
    async def test_execute_batch_job_partial_failure(self, batch_service, mock_job_repo):
        """Test batch job execution with partial failures."""
        job_id = 1
        targets = [
            {"team": "chiefs", "year": 2024},
            {"team": "invalid", "year": 2024},
            {"team": "bills", "year": 2024}
        ]

        # Mock job retrieval
        mock_job = ScrapeJob(
            id=job_id,
            status='pending',
            total_urls=3,
            processed=0,
            failed=0
        )
        mock_job_repo.get_by_id.return_value = mock_job

        # Mock scrape_and_store - fail on second target
        async def mock_scrape_fn(team, year):
            if team == "invalid":
                raise Exception("Invalid team")

        with patch('src.services.batch_scrape_service.scrape_and_store', side_effect=mock_scrape_fn):
            with patch('asyncio.sleep', new_callable=AsyncMock):
                result = await batch_service.execute_batch_job(job_id, targets)

        assert result['job_id'] == job_id
        assert result['total'] == 3
        assert result['succeeded'] == 2
        assert result['failed'] == 1
        assert len(result['errors']) == 1
        assert 'Invalid team' in result['errors'][0]['error']

        # Verify both success and failure were tracked
        assert mock_job_repo.increment_processed.call_count == 2
        assert mock_job_repo.increment_failed.call_count == 1

    @pytest.mark.asyncio
    async def test_execute_batch_job_not_found(self, batch_service, mock_job_repo):
        """Test batch job execution when job doesn't exist."""
        mock_job_repo.get_by_id.return_value = None

        with pytest.raises(ValueError, match="Job 999 not found"):
            await batch_service.execute_batch_job(999, [])

    def test_get_job_status_success(self, batch_service, mock_job_repo):
        """Test getting job status."""
        mock_job = ScrapeJob(
            id=1,
            status='running',
            total_urls=10,
            processed=5,
            failed=1,
            errors=[{"error": "test error"}],
            created_at=datetime(2024, 1, 1, 12, 0, 0),
            completed_at=None
        )
        mock_job_repo.get_by_id.return_value = mock_job

        status = batch_service.get_job_status(1)

        assert status['job_id'] == 1
        assert status['status'] == 'running'
        assert status['total_urls'] == 10
        assert status['processed'] == 5
        assert status['failed'] == 1
        assert status['errors'] == [{"error": "test error"}]
        assert status['completed_at'] is None

    def test_get_job_status_not_found(self, batch_service, mock_job_repo):
        """Test getting status for non-existent job."""
        mock_job_repo.get_by_id.return_value = None

        status = batch_service.get_job_status(999)

        assert status is None

    def test_list_jobs_all(self, batch_service, mock_job_repo):
        """Test listing all jobs."""
        mock_jobs = [
            ScrapeJob(
                id=1,
                status='complete',
                total_urls=5,
                processed=5,
                failed=0,
                created_at=datetime(2024, 1, 1),
                completed_at=datetime(2024, 1, 1, 1, 0, 0)
            ),
            ScrapeJob(
                id=2,
                status='running',
                total_urls=10,
                processed=5,
                failed=0,
                created_at=datetime(2024, 1, 2),
                completed_at=None
            )
        ]
        mock_job_repo.get_all_jobs.return_value = mock_jobs

        jobs = batch_service.list_jobs()

        assert len(jobs) == 2
        assert jobs[0]['job_id'] == 1
        assert jobs[1]['job_id'] == 2

    def test_list_jobs_by_status(self, batch_service, mock_job_repo):
        """Test listing jobs filtered by status."""
        mock_jobs = [
            ScrapeJob(
                id=1,
                status='running',
                total_urls=10,
                processed=5,
                failed=0,
                created_at=datetime(2024, 1, 1),
                completed_at=None
            )
        ]
        mock_job_repo.get_jobs_by_status.return_value = mock_jobs

        jobs = batch_service.list_jobs(status='running')

        assert len(jobs) == 1
        assert jobs[0]['status'] == 'running'
        mock_job_repo.get_jobs_by_status.assert_called_once_with('running', 100)
