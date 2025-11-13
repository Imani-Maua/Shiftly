from datetime import date
from typing import List
from sqlalchemy import String, Date
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from app.database.models.scheduled_shifts import ScheduledShift


class Base(DeclarativeBase):
    pass




class Schedule(Base):
    __tablename__ = "schedules"

    id: Mapped[int] = mapped_column(primary_key=True,index=True)
    week_start: Mapped[date] = mapped_column(Date)
    week_end: Mapped[date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String, default="draft")

    scheduled_shifts: Mapped[List["ScheduledShift"]] = relationship(back_populates="schedule")