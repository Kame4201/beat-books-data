"""create scrape_jobs table

Adds the scrape_jobs table for tracking batch scraping operations.
Each row represents a batch job with status, progress counters,
and error details. Used by BatchScrapeService to persist job state
across the scraping lifecycle (pending -> running -> complete/failed).

See also: src/entities/scrape_job.py (ScrapeJob entity)

Revision ID: 005
Revises: None
Create Date: 2026-02-16 00:02:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
# down_revision is None for now; will be chained to the correct
# predecessor during rebase when other migration PRs are merged.
revision = '005'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create the scrape_jobs table and its status index.

    Columns match src/entities/scrape_job.py exactly:
    - id: auto-incrementing primary key
    - status: job lifecycle state (pending, running, complete, failed)
    - total_urls: number of URLs queued for scraping
    - processed: count of successfully scraped URLs
    - failed: count of URLs that failed to scrape
    - errors: JSON array of error detail objects
    - created_at: timestamp when the job was created
    - completed_at: timestamp when the job finished (nullable)
    """
    op.create_table(
        'scrape_jobs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('total_urls', sa.Integer(), nullable=False),
        sa.Column('processed', sa.Integer(), nullable=False),
        sa.Column('failed', sa.Integer(), nullable=False),
        sa.Column('errors', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scrape_jobs_status'), 'scrape_jobs', ['status'])


def downgrade() -> None:
    """Drop the scrape_jobs table and its index."""
    op.drop_index(op.f('ix_scrape_jobs_status'), table_name='scrape_jobs')
    op.drop_table('scrape_jobs')
