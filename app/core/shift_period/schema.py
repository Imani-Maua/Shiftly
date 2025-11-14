from pydantic import BaseModel
from datetime import time
from enum import Enum

class ShiftName(str, Enum):
    AM  = "AM"
    PM = "PM"
    Lounge = "lounge"

class ShiftPeriodCreate(BaseModel):
    shift_name: ShiftName
    start_time: time
    end_time: time

class ShiftPeriodUpdate(BaseModel):
    shift_name: ShiftName  | None = None
    start_time: time  | None = None
    end_time: time  | None = None
   
class ShiftOut(BaseModel):
    id: int
    shift_name: str
    start_time: time
    end_time: time