from __future__ import annotations

from sqlalchemy.orm import Session

from src.entities.games import Games
from src.repositories.base_repo import BaseRepository


class GamesRepository(BaseRepository[Games]):
    def __init__(self, session: Session) -> None:
        super().__init__(session=session, model=Games)
