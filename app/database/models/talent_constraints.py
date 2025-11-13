from typing import List, Optional
from sqlalchemy import ForeignKey, String, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from app.database.models.talents import Talent
from app.database.models.constraint_rules import ConstraintRule


class Base(DeclarativeBase):
    pass

class TalentConstraint(Base):
    __tablename__ = "talent_constraints"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    talent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("talents.id", ondelete="CASCADE"))
    type: Mapped[Optional[str]] = mapped_column(String(50))
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)

    talent: Mapped[Optional["Talent"]] = relationship(back_populates="constraints")
    rules: Mapped[List["ConstraintRule"]] = relationship(back_populates="constraint")