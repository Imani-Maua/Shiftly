from fastapi import APIRouter, Body
from datetime import date, timedelta
from typing import Annotated
from app.core.services.models import inputDate


service_router = APIRouter()

#generate the schedule
@service_router.post("/generate")
async def generate_schedule(start_date: Annotated[inputDate, Body()]):
    pass
#view unassigned shifts
#view talent availability


#submit a request
#update the status of a request
#list all the requests for a talent/week
