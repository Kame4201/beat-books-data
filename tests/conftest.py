import os

# Set DATABASE_URL before any src imports so Settings() doesn't fail during collection
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.entities.base import Base


@pytest.fixture
def db_session():
    """In-memory SQLite for unit tests. Never hits production DB."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    engine.dispose()
