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

class ShiftTemplateCreate(BaseModel):
    staffing: str
    role: str
    role_count: int

class ShiftTemplateUpdate(BaseModel):
    staffing: str | None = None
    role: str | None = None
    role_count: int | None = None

class ShiftTemplateOut(BaseModel):
    staffing: str
    role: str
    role_count: int

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

