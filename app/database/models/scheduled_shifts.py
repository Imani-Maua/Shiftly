from datetime import date, time, datetime
from typing import  Optional
from sqlalchemy import ForeignKey, Numeric, Date, Time
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from app.database.models.talents import Talent
from app.database.models.schedules import Schedule


class Base(DeclarativeBase):
    pass


class ScheduledShift(Base):
    __tablename__ = "scheduled_shifts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    talent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("talents.id", ondelete="CASCADE"))
    date_of: Mapped[Optional[date]] = mapped_column(Date)
    start_time: Mapped[Optional[time]] = mapped_column(Time)
    end_time: Mapped[Optional[time]] = mapped_column(Time)
    shift_hours: Mapped[Optional[float]] = mapped_column(Numeric(3, 1))
    schedule_id: Mapped[Optional[int]] = mapped_column(ForeignKey("schedules.id", ondelete="CASCADE"))

   
    talent: Mapped[Optional["Talent"]] = relationship(back_populates="scheduled_shifts")
    schedule: Mapped[Optional["Schedule"]] = relationship(back_populates="scheduled_shifts")