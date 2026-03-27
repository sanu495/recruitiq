from typing import Type, TypeVar, Generic, List, Optional
from sqlmodel import Session, select, SQLModel
from fastapi import HTTPException

T = TypeVar("T", bound=SQLModel)


class GenericDal(Generic[T]):
    def __init__(self, model: Type[T], db: Session):
        self.model = model
        self.db_session = db

    # ── Create ─────────────────────────────────────────────────────────────────
    def create(self, obj: T) -> T:
        self.db_session.add(obj)
        self.db_session.commit()
        self.db_session.refresh(obj)
        return obj

    # ── Get by ID ──────────────────────────────────────────────────────────────
    def get(self, id: int) -> Optional[T]:
        obj = self.db_session.get(self.model, id)
        if not obj:
            raise HTTPException(
                status_code=404,
                detail=f"{self.model.__name__} with id {id} not found"
            )
        return obj

    # ── Get All ────────────────────────────────────────────────────────────────
    def get_all(self) -> List[T]:
        statement = select(self.model)
        return self.db_session.exec(statement).all()

    # ── Update ─────────────────────────────────────────────────────────────────
    def update(self, id: int, obj_data: dict) -> Optional[T]:
        db_obj = self.get(id)
        for key, value in obj_data.items():
            if value is not None:
                setattr(db_obj, key, value)
        self.db_session.add(db_obj)
        self.db_session.commit()
        self.db_session.refresh(db_obj)
        return db_obj

    # ── Delete ─────────────────────────────────────────────────────────────────
    def delete(self, id: int) -> bool:
        obj = self.get(id)
        self.db_session.delete(obj)
        self.db_session.commit()
        return True

    # ── Get by any single field ────────────────────────────────────────────────
    def get_by_field(self, field: str, value) -> Optional[T]:
        """
        Example usage:
            dal.get_by_field("email", "sanu@gmail.com")
            dal.get_by_field("status", "open")
        """
        statement = select(self.model).where(
            getattr(self.model, field) == value
        )
        return self.db_session.exec(statement).first()

    # ── Get many by field ──────────────────────────────────────────────────────
    def get_many_by_field(self, field: str, value) -> List[T]:
        """
        Example usage:
            dal.get_many_by_field("recruiter_id", 1)
            dal.get_many_by_field("stage", "applied")
        """
        statement = select(self.model).where(
            getattr(self.model, field) == value
        )
        return self.db_session.exec(statement).all()