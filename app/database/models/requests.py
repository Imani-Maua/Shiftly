from datetime import date, datetime
from typing import Optional
from sqlalchemy import ForeignKey, String, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from app.database.models.talents import Talent


class Base(DeclarativeBase):
    pass


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