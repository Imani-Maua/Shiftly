from datetime import date, time, datetime
from typing import List, Optional
from sqlalchemy import ForeignKey, String, Integer, Boolean, Numeric
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


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
    hours: Mapped[int] = mapped_column(Integer, default=40)
    start_date: Mapped[Optional[date]]
    end_date: Mapped[Optional[date]]

    requests: Mapped[List["Request"]] = relationship(back_populates="talent")
    constraints: Mapped[List["TalentConstraint"]] = relationship(back_populates="talent")
    scheduled_shifts: Mapped[List["ScheduledShift"]] = relationship(back_populates="talent")



class TalentConstraint(Base):
    __tablename__ = "talent_constraints"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    talent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("talents.id", ondelete="CASCADE"))
    type: Mapped[Optional[str]] = mapped_column(String(50))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    talent: Mapped[Optional["Talent"]] = relationship(back_populates="constraints")
    constraint_days: Mapped[List["ConstraintDay"]] = relationship(back_populates="constraint")



class ConstraintDay(Base):
    __tablename__ = "constraint_days"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    constraint_id: Mapped[Optional[int]] = mapped_column(ForeignKey("talent_constraints.id", ondelete="CASCADE"))
    day: Mapped[Optional[str]] = mapped_column(String(50))
    shifts: Mapped[Optional[str]] = mapped_column(String(50))

    constraint: Mapped[Optional["TalentConstraint"]] = relationship(back_populates="constraint_days")



class ShiftPeriod(Base):
    __tablename__ = "shift_periods"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    shift_name: Mapped[Optional[str]] = mapped_column(String(50))
    start_time: Mapped[Optional[time]]
    end_time: Mapped[Optional[time]]


    templates: Mapped[List["ShiftTemplate"]] = relationship(back_populates="period")


class ShiftTemplate(Base):
    __tablename__ = "shift_templates"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    period_id: Mapped[Optional[int]] = mapped_column(ForeignKey("shift_periods.id", ondelete="CASCADE"))
    staffing: Mapped[Optional[str]] = mapped_column(String(50))
    role: Mapped[Optional[str]] = mapped_column(String(50))
    role_count: Mapped[Optional[int]] = mapped_column(Integer)


    period: Mapped[Optional["ShiftPeriod"]] = relationship(back_populates="templates")



class ScheduledShift(Base):
    __tablename__ = "scheduled_shifts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    talent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("talents.id", ondelete="CASCADE"))
    date_of: Mapped[Optional[date]]
    start_time: Mapped[Optional[time]]
    end_time: Mapped[Optional[time]]
    shift_hours: Mapped[Optional[float]] = mapped_column(Numeric(3, 1))
    schedule_id: Mapped[Optional[int]] = mapped_column(ForeignKey("schedules.id", ondelete="CASCADE"))

   
    talent: Mapped[Optional["Talent"]] = relationship(back_populates="scheduled_shifts")
    schedule: Mapped[Optional["Schedule"]] = relationship(back_populates="scheduled_shifts")

class Schedule(Base):
    __tablename__ = "schedules"

    id: Mapped[int] = mapped_column(primary_key=True,index=True)
    week_start: Mapped[date] = mapped_column(date)
    week_end: Mapped[date] = mapped_column(date)
    status: Mapped[str] = mapped_column(str, default="draft")

    scheduled_shifts: Mapped[List["ScheduledShift"]] = relationship(back_populates="schedule")

class Request(Base):
    __tablename__ = "requests"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    talent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("talents.id", ondelete="CASCADE"))
    req_date: Mapped[date]
    status: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(default=datetime)
    updated_at: Mapped[datetime] = mapped_column(default=datetime)
    holiday_type: Mapped[str] = mapped_column(String(10), default="paid")
    leave_days: Mapped[int] = mapped_column(Integer, default=21)
    paid_taken: Mapped[int] = mapped_column(Integer, default=0)


    talent: Mapped[Optional["Talent"]] = relationship(back_populates="requests")