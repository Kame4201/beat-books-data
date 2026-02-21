"""
Unit tests for base_repo.py (BaseRepository)

Tests cover:
- create: Add entity to session, commit, refresh
- get_by_id: Retrieve by primary key
- list: Paginated listing with limit/offset
- update: Merge and commit changes
- delete: Remove entity from session

All tests use an in-memory SQLite database with a simple test entity.

Run with:
    pytest tests/test_unit/test_repositories/test_base_repo.py -v
"""

import pytest
from sqlalchemy import create_engine, Integer, String, event
from sqlalchemy.orm import sessionmaker, Mapped, mapped_column

from src.entities.base import Base
from src.repositories.base_repo import BaseRepository


# ---- Test entity (not a real app entity, just for testing the base repo) ----
class FakeEntity(Base):
    __tablename__ = "fake_entity"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(64))


@pytest.fixture
def session():
    """Create a fresh in-memory SQLite session with FakeEntity table."""
    engine = create_engine("sqlite:///:memory:")

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    sess = Session()
    yield sess
    sess.close()
    engine.dispose()


@pytest.fixture
def repo(session):
    """Return a BaseRepository bound to FakeEntity."""
    return BaseRepository(session=session, model=FakeEntity)


class TestBaseRepositoryCreate:
    """Tests for BaseRepository.create()."""

    def test_create_with_commit(self, repo, session):
        """Create should add, commit, and refresh the entity."""
        entity = FakeEntity(name="alpha")
        result = repo.create(entity)

        assert result.id is not None
        assert result.name == "alpha"
        # Should be persisted
        assert session.get(FakeEntity, result.id) is not None

    def test_create_without_commit(self, repo, session):
        """Create with commit=False should add but not commit."""
        entity = FakeEntity(name="beta")
        result = repo.create(entity, commit=False)

        # Entity is added to session but may not have an id until flush
        assert result.name == "beta"
        # Manually rollback to verify it was not committed
        session.rollback()
        assert session.query(FakeEntity).filter_by(name="beta").first() is None

    def test_create_multiple(self, repo):
        """Should be able to create multiple entities."""
        e1 = repo.create(FakeEntity(name="first"))
        e2 = repo.create(FakeEntity(name="second"))

        assert e1.id != e2.id
        assert e1.name == "first"
        assert e2.name == "second"


class TestBaseRepositoryGetById:
    """Tests for BaseRepository.get_by_id()."""

    def test_get_existing(self, repo):
        """Should return entity when it exists."""
        entity = repo.create(FakeEntity(name="findme"))

        result = repo.get_by_id(entity.id)

        assert result is not None
        assert result.name == "findme"

    def test_get_nonexistent(self, repo):
        """Should return None for non-existent ID."""
        result = repo.get_by_id(99999)
        assert result is None


class TestBaseRepositoryList:
    """Tests for BaseRepository.list()."""

    def test_list_all(self, repo):
        """Should return all entities."""
        repo.create(FakeEntity(name="a"))
        repo.create(FakeEntity(name="b"))
        repo.create(FakeEntity(name="c"))

        result = repo.list()

        assert len(result) == 3

    def test_list_with_limit(self, repo):
        """Should respect limit parameter."""
        for i in range(5):
            repo.create(FakeEntity(name=f"item_{i}"))

        result = repo.list(limit=3)

        assert len(result) == 3

    def test_list_with_offset(self, repo):
        """Should respect offset parameter."""
        for i in range(5):
            repo.create(FakeEntity(name=f"item_{i}"))

        result = repo.list(limit=100, offset=3)

        assert len(result) == 2

    def test_list_empty(self, repo):
        """Should return empty list when no entities exist."""
        result = repo.list()
        assert result == []


class TestBaseRepositoryUpdate:
    """Tests for BaseRepository.update()."""

    def test_update_with_commit(self, repo):
        """Update should merge changes and commit."""
        entity = repo.create(FakeEntity(name="original"))
        entity.name = "updated"

        result = repo.update(entity)

        assert result.name == "updated"
        # Verify persisted
        fetched = repo.get_by_id(entity.id)
        assert fetched.name == "updated"

    def test_update_without_commit(self, repo, session):
        """Update with commit=False should merge but not commit."""
        entity = repo.create(FakeEntity(name="original"))
        original_id = entity.id
        entity.name = "pending"

        repo.update(entity, commit=False)

        # Rollback should revert
        session.rollback()
        fetched = repo.get_by_id(original_id)
        assert fetched.name == "original"


class TestBaseRepositoryDelete:
    """Tests for BaseRepository.delete()."""

    def test_delete_with_commit(self, repo):
        """Delete should remove the entity and commit."""
        entity = repo.create(FakeEntity(name="deleteme"))
        entity_id = entity.id

        repo.delete(entity)

        assert repo.get_by_id(entity_id) is None

    def test_delete_without_commit(self, repo, session):
        """Delete with commit=False should mark for deletion but not commit."""
        entity = repo.create(FakeEntity(name="keepme"))
        entity_id = entity.id

        repo.delete(entity, commit=False)

        # Rollback should restore
        session.rollback()
        assert repo.get_by_id(entity_id) is not None
