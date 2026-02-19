from __future__ import annotations

from sqlalchemy.orm import Session

from src.entities.returns import TeamReturns
from src.repositories.base_repo import BaseRepository


class ReturnsRepository(BaseRepository[TeamReturns]):
    def __init__(self, session: Session) -> None:
        super().__init__(session=session, model=TeamReturns)
