from pydantic import BaseModel
from datetime import datetime,date
from typing import List

class inputDate(BaseModel):
    start_date: date

class holidayRequestSubmit(BaseModel):
    request_date: date
    holiday_type: str

