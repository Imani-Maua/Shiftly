from pydantic import BaseModel, ConfigDict
from enum import Enum


class Days(Enum):
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"
    SUNDAY = "Sunday"

class Shifts(Enum):
    AM = "am"
    PM = "pm"
    LOUNGE = "lounge"

class ConstraintType(Enum):
    AVAILABILITY = "availability"
    SHIFT_RESTRICTION = "shift restriction"
    COMBINATION = "combination"

class ConstraintRuleIn(BaseModel):
    constraint_id: int
    day: list[Days | None] | None = None
    shifts: list[Shifts | None] | None = None

class ConstraintRuleCreate(BaseModel):
    constraint_id: int
    day: str | None
    shifts: str | None

class ConstraintOut(BaseModel):
    id: int
    talent_id: int
    type: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class ConstraintRuleOut(BaseModel):
    constraint: ConstraintOut
    day: str| None = None
    shifts: str | None = None

    model_config = ConfigDict(from_attributes=True)

class ConstraintRuleUpdate(BaseModel):
    constraint_id: int
    day: list[str] | None = None
    shifts: list[str] | None = None

