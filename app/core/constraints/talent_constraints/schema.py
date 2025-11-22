from pydantic import BaseModel, ConfigDict
from app.core.utils.enums import ConstraintType, Days, Shifts



class ConstraintIn(BaseModel):
    talent_id: int 
    type: ConstraintType

    model_config = ConfigDict(use_enum_values=True, from_attributes=True)

class ConstraintUpdate(BaseModel):
    is_active: bool
    days: Days | None = None
    shifts: Shifts | None = None

class ConstraintOut(BaseModel):
    talent_id: int
    type: ConstraintType
    is_active: bool
    day: list[Days] | None = None 
    shift: list[Shifts] | None = None

    model_config = ConfigDict(use_enum_values=True, from_attributes=True)


