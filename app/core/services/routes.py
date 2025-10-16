from fastapi import APIRouter, Body, Depends, HTTPException, status
from datetime import date, timedelta, datetime
from typing import Annotated
import asyncpg
from app.core.services.models import inputDate
from app.core.services.utils.utils import get_week_range
from app.core.services.scheduler.data_services import process_request_data, process_shift_data, process_talent_data, approvedHolidayRequests
from app.core.services.scheduler.generators import talentByRole
from app.core.services.scheduler.shift_allocator import shiftAssignment
from app.infrastructure.database.database import get_db
from app.core.entities.entities import weekRange


service_router = APIRouter()


@service_router.post("/generate")
async def generate_schedule(start_date: Annotated[inputDate, Body()], 
                            db: Annotated[asyncpg.Connection, Depends(get_db)]):
    try:
        week_for_schedule = get_week_range(start_date)
        talent_objects = await process_talent_data(week_for_schedule, db)
        shift_openings = await process_shift_data(week_for_schedule, db)
        placed_requests = await process_request_data(db=db)
        talent_approved_requests = await approvedHolidayRequests.process_approved_holidays(db, talent_objects,placed_requests)
        talents_by_role = talentByRole.group_talents(talent_approved_requests)
        shift_assignments = shiftAssignment(talent_approved_requests, shift_openings, talents_by_role)
        generate_shift_assignments = shift_assignments.generate_schedule()
        return generate_shift_assignments
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except asyncpg.PostgresError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail= "Database error:" + str(e))
    except KeyError as e:
        raise HTTPException(status_code=500, detail="Data missing key: " + str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unexpected error: " + str(e))
    

    
#view unassigned shifts
#view talent availability


#submit a request
#update the status of a request
#list all the requests for a talent/week
