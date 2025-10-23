from pydantic import BaseModel
from datetime import datetime,date, time
from typing import List
from enum import Enum

class inputDate(BaseModel):
    start_date: date

class holidayRequestSubmit(BaseModel):
    request_date: date
    holiday_type: str

class ShiftName(str, Enum):
    AM  = "AM"
    PM = "PM"
    Lounge = "lounge"

class Staffing(str, Enum):
    low = "low"
    high = "high"

class ShiftCreate(BaseModel):
    staffing: Staffing
    shift_name: ShiftName
    start_time: time
    end_time: time
    role: str
    role_count: int

class ShiftUpdate(BaseModel):
    staffing: Staffing | None = None
    shift_name: ShiftName  | None = None
    start_time: time  | None = None
    end_time: time  | None = None
    role: str  | None = None
    role_count: int  | None = None

class ShiftOut(BaseModel):
    id: int
    shift_name: str
    role_name: str
    start_time: time
    end_time: time
    staffing: str

