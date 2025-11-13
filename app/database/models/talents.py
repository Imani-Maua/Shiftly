from datetime import date
from typing import List, Optional
from sqlalchemy import  String, Integer, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from app.database.models.talent_constraints import TalentConstraint
from app.database.models.requests import Request
from app.database.models.scheduled_shifts import ScheduledShift

class Base(DeclarativeBase):
    pass

class Talent(Base):
    __tablename__ = "talents"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    firstname: Mapped[Optional[str]] = mapped_column(String(50))
    lastname: Mapped[Optional[str]] = mapped_column(String(50))
    email: Mapped[Optional[str]] = mapped_column(String(100))
    tal_role: Mapped[str] = mapped_column(String(50))
    contract_type: Mapped[str] = mapped_column(String(50), default="full-time")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    hours: Mapped[int] = mapped_column(Integer)
    start_date: Mapped[Optional[date]]
    end_date: Mapped[Optional[date]]

    requests: Mapped[List["Request"]] = relationship(back_populates="talent")
    constraints: Mapped[List["TalentConstraint"]] = relationship(back_populates="talent")
    scheduled_shifts: Mapped[List["ScheduledShift"]] = relationship(back_populates="talent")