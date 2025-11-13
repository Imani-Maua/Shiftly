from datetime import time
from typing import List, Optional
from sqlalchemy import  String, Time
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from app.database.models.shift_templates import ShiftTemplate


class Base(DeclarativeBase):
    pass

class ShiftPeriod(Base):
    __tablename__ = "shift_periods"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    shift_name: Mapped[Optional[str]] = mapped_column(String(50))
    start_time: Mapped[Optional[time]] = mapped_column(Time)
    end_time: Mapped[Optional[time]] = mapped_column(Time)


    templates: Mapped[List["ShiftTemplate"]] = relationship(back_populates="period")