from typing import Optional
from sqlalchemy import ForeignKey, String, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from app.database.models.shift_periods import ShiftPeriod


class Base(DeclarativeBase):
    pass



class ShiftTemplate(Base):
    __tablename__ = "shift_templates"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    period_id: Mapped[Optional[int]] = mapped_column(ForeignKey("shift_periods.id", ondelete="CASCADE"))
    staffing: Mapped[Optional[str]] = mapped_column(String(50))
    role: Mapped[Optional[str]] = mapped_column(String(50))
    role_count: Mapped[Optional[int]] = mapped_column(Integer)


    period: Mapped[Optional["ShiftPeriod"]] = relationship(back_populates="templates")