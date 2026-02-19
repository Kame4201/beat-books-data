from __future__ import annotations

from sqlalchemy.orm import Session

from src.entities.standings import Standings
from src.repositories.base_repo import BaseRepository


class StandingsRepository(BaseRepository[Standings]):
    def __init__(self, session: Session) -> None:
        super().__init__(session=session, model=Standings)
