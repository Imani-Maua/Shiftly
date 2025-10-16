from pydantic import BaseModel
from datetime import date

class inputDate(BaseModel):
    start_date: date