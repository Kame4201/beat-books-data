from __future__ import annotations

from sqlalchemy.orm import Session

from src.entities.punting import Punting
from src.repositories.base_repo import BaseRepository


class PuntingRepository(BaseRepository[Punting]):
    def __init__(self, session: Session) -> None:
        super().__init__(session=session, model=Punting)
