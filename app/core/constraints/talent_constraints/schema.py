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



