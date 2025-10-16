from pydantic import BaseModel
from datetime import datetime,date
from typing import List

class inputDate(BaseModel):
    start_date: date

