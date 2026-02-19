from __future__ import annotations

from typing import Generic, TypeVar, Type, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import select

T = TypeVar("T")


class BaseRepository(Generic[T]):
    def __init__(self, session: Session, model: Type[T]) -> None:
        self.session = session
        self.model = model

    def create(self, obj: T, *, commit: bool = True) -> T:
        self.session.add(obj)
        if commit:
            self.session.commit()
            self.session.refresh(obj)
        return obj

    def get_by_id(self, id_: Any) -> Optional[T]:
        return self.session.get(self.model, id_)

    def list(self, *, limit: int = 100, offset: int = 0) -> list[T]:
        stmt = select(self.model).limit(limit).offset(offset)
        return list(self.session.execute(stmt).scalars().all())

    def update(self, obj: T, *, commit: bool = True) -> T:
        obj = self.session.merge(obj)
        if commit:
            self.session.commit()
            self.session.refresh(obj)
        return obj

    def delete(self, obj: T, *, commit: bool = True) -> None:
        self.session.delete(obj)
        if commit:
            self.session.commit()

    def upsert(self, obj: T, unique_fields: dict, *, commit: bool = True) -> T:
        """Insert *obj* or update the existing row matched by *unique_fields*."""
        stmt = select(self.model)
        for field, value in unique_fields.items():
            stmt = stmt.where(getattr(self.model, field) == value)
        existing = self.session.execute(stmt).scalars().first()

        if existing:
            for key, value in vars(obj).items():
                if key.startswith("_") or key == "id":
                    continue
                setattr(existing, key, value)
            if commit:
                self.session.commit()
                self.session.refresh(existing)
            return existing

        self.session.add(obj)
        if commit:
            self.session.commit()
            self.session.refresh(obj)
        return obj
