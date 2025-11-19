from pydantic import BaseModel, ConfigDict
from datetime import time
from enum import Enum

class ShiftName(Enum):
    AM  = "AM"
    PM = "PM"
    Lounge = "lounge"


   
class ShiftPeriodIn(BaseModel):
    shift_name: ShiftName
    start_time: time
    end_time: time

    model_config = ConfigDict(use_enum_values=True, from_attributes=True)


class ShiftPeriodUpdate(BaseModel):
    shift_name: ShiftName  | None = None
    start_time: time  | None = None
    end_time: time  | None = None

    model_config = ConfigDict(use_enum_values=True, from_attributes=True)

   
class ShiftOut(BaseModel):
    id: int
    shift: ShiftPeriodIn

    