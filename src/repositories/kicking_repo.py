from __future__ import annotations

from sqlalchemy.orm import Session

from src.entities.kicking import Kicking
from src.repositories.base_repo import BaseRepository


class KickingRepository(BaseRepository[Kicking]):
    def __init__(self, session: Session) -> None:
        super().__init__(session=session, model=Kicking)
