from __future__ import annotations

from sqlalchemy.orm import Session

from src.entities.team_defense import TeamDefense
from src.repositories.base_repo import BaseRepository


class TeamDefenseRepository(BaseRepository[TeamDefense]):
    def __init__(self, session: Session) -> None:
        super().__init__(session=session, model=TeamDefense)
