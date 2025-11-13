from datetime import date, time, datetime
from typing import List, Optional
from sqlalchemy import ForeignKey, String, Integer, Boolean, Numeric, Date, Time
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from app.database.models.talent_constraints import TalentConstraint

class Base(DeclarativeBase):
    pass

class ConstraintRule(Base):
    __tablename__ = "constraint_rules"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    constraint_id: Mapped[Optional[int]] = mapped_column(ForeignKey("talent_constraints.id", ondelete="CASCADE"))
    day: Mapped[Optional[str]] = mapped_column(String(50))
    shifts: Mapped[Optional[str]] = mapped_column(String(50))

    constraint: Mapped[Optional["TalentConstraint"]] = relationship(back_populates="rules")