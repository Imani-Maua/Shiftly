from pydantic import BaseModel
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

class ConstraintCreate(BaseModel):
    talent_id: int 
    type: ConstraintType

class ConstraintRuleIn(BaseModel):
    constraint_id: int
    day: list[Days | None] | None = None
    shifts: list[Shifts | None] | None = None

class ConstraintRuleCreate(BaseModel):
    constraint_id: int
    day: str | None
    shifts: str | None

class ConstraintRuleOut(BaseModel):
    talent_id: int
    constraint_id: int
    type: str
    is_active: bool
    day: str| None = None
    shifts: str | None = None



class ConstraintRuleUpdate(BaseModel):
    constraint_id: int
    day: list[str] | None = None
    shifts: list[str] | None = None


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



