from sqlalchemy import (
    Column, Integer, String, Boolean, Date, Time, Numeric, ForeignKey, 
    TIMESTAMP, func
) 
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class Talent(Base):
    __tablename__ = "talents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    firstname = Column(String(50))
    lastname = Column(String(50))
    email = Column(String(100))
    tal_role = Column(String(50), nullable=False)
    contract_type = Column(String(50), default="full-time")
    is_active = Column(Boolean, default=True)
    hours = Column(Integer, default=40)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)

    constraints = relationship("TalentConstraint", back_populates="talent")
    scheduled_shifts = relationship("ScheduledShift", back_populates="talent")
    requests = relationship("Request", back_populates="talent")


class TalentConstraint(Base):
    __tablename__ = "talent_constraints"

    id = Column(Integer, primary_key=True, autoincrement=True)
    talent_id = Column(Integer, ForeignKey("talents.id"))
    type = Column(String(50))
    is_active = Column(Boolean, default=True)

    talent = relationship("Talent", back_populates="constraints")
    constraint_days = relationship("ConstraintDay", back_populates="constraint")


class ConstraintDay(Base):
    __tablename__ = "constraint_days"

    id = Column(Integer, primary_key=True, autoincrement=True)
    constraint_id = Column(Integer, ForeignKey("talent_constraints.id"))
    day = Column(String(50))
    shifts = Column(String(50))

    constraint = relationship("TalentConstraint", back_populates="constraint_days")


class ShiftPeriod(Base):
    __tablename__ = "shift_periods"

    id = Column(Integer, primary_key=True, autoincrement=True)
    staffing = Column(String(50))
    shift_name = Column(String(50))
    start_time = Column(Time)
    end_time = Column(Time)

    templates = relationship("ShiftTemplate", back_populates="period")


class ShiftTemplate(Base):
    __tablename__ = "shift_templates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    period_id = Column(Integer, ForeignKey("shift_periods.id"))
    role = Column(String(50))
    role_count = Column(Integer)

    period = relationship("ShiftPeriod", back_populates="templates")


class ScheduledShift(Base):
    __tablename__ = "scheduled_shifts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    talent_id = Column(Integer, ForeignKey("talents.id"))
    date_of = Column(Date)
    start_time = Column(Time)
    end_time = Column(Time)
    shift_hours = Column(Numeric(3, 1))

    talent = relationship("Talent", back_populates="scheduled_shifts")


class Request(Base):
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    talent_id = Column(Integer, ForeignKey("talents.id"))
    req_date = Column(Date, nullable=False)
    status = Column(String(50))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    holiday_type = Column(String(10), default="paid")
    leave_days = Column(Integer, default=21)
    paid_taken = Column(Integer, default=0)

    talent = relationship("Talent", back_populates="requests")


class InviteToken(Base):
    __tablename__ = "invite_token"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer)
    token = Column(String(255), nullable=False, unique=True)
    jti = Column(String(36), unique=True)
    type = Column(String(20), nullable=False)
    expires_at = Column(TIMESTAMP, nullable=False)
    used_at = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
