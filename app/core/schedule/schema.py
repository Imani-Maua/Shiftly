from pydantic import BaseModel
from datetime import date, time
from enum import Enum

class inputDate(BaseModel):
    start_date: date

class Staffing(str, Enum):
    low = "low"
    high = "high"





