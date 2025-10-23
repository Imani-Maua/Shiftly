from fastapi import APIRouter, Body, Depends, HTTPException, status
from datetime import date, timedelta, datetime
from typing import Annotated
import asyncpg
from app.core.services.models import inputDate, ShiftUpdate, ShiftCreate, ShiftOut
from app.core.entities.entities import shiftSpecification, assignment
from app.core.services.utils.utils import get_week_range
from app.core.services.scheduler.data_services import process_request_data, process_shift_data, process_talent_data, approvedHolidayRequests
from app.core.services.scheduler.generators import talentByRole
from app.core.services.scheduler.shift_allocator import shiftAssignment, UnderstaffedShifts
from app.infrastructure.database.database import get_db
from app.core.entities.entities import weekRange
from app.auth.security import required_roles
from app.auth.models import UserRole


schedule = APIRouter()
holidays = APIRouter()


@schedule.post("/generate")
async def generate_schedule(db: Annotated[asyncpg.Connection, Depends(get_db)],
                            start_date: Annotated[inputDate, Body()], 
                             _: str = Depends(required_roles(UserRole.superuser, UserRole.admin))):
    try:
        week_for_schedule = get_week_range(start_date)
        talent_objects = await process_talent_data(week_for_schedule, db)
        shift_openings = await process_shift_data(week_for_schedule, db)
        placed_requests = await process_request_data(db=db)
        talent_approved_requests = await approvedHolidayRequests.process_approved_holidays(db, talent_objects,placed_requests)
        talents_by_role = talentByRole.group_talents(talent_approved_requests)
        shift_assignments = shiftAssignment(talent_approved_requests, shift_openings, talents_by_role)
        generated_assignments = shift_assignments.generate_schedule()
        
        understaffed = UnderstaffedShifts(db, shift_openings, generated_assignments).get_all()
        return {
            "status": "complete" if not understaffed else "understaffed",
            "generated assignments":generated_assignments, 
            "understaffed shifts": understaffed
            }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except asyncpg.PostgresError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail= "Database error:" + str(e))
    except KeyError as e:
        raise HTTPException(status_code=500, detail="Data missing key: " + str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unexpected error: " + str(e))
    
@schedule.post("/create_shift")
async def create_shift_period(db: Annotated[asyncpg.Connection, Depends(get_db)],
                              data: Annotated[ShiftCreate, Body()],
                              _: str = Depends(required_roles(UserRole.admin, UserRole.manager))):
    period_query = """
            INSERT INTO shift_periods(staffing, shift_name, start_time, end_time)
            VALUES($1, $2, $3, $4) RETURNING id"""
    period_id_record = await db.fetchrow(period_query, 
                                         data.staffing,
                                         data.shift_name.value if hasattr(data.shift_name, "value") else data.shift_name,
                                         data.start_time,
                                         data.end_time)
    period_id = period_id_record["id"]
    template_query = """
            INSERT INTO shift_templates(period_id, role, role_count)
            VALUES($1, $2, $3)"""
    shift_id_record = await db.fetchrow(template_query, period_id, data.role, data.role_count)
    shift_id = shift_id_record["id"]
    return ShiftOut(
        id=shift_id,
        shift_name=data.shift_name.value if hasattr(data.shift_name, "value") else data.shift_name,
        role_name= data.role,
        start_time=data.start_time,
        end_time=data.end_time,
        staffing=data.staffing
    )
    



 #submit a request
   
#view unassigned shifts

#view talent availability



#update the status of a request
#list all the requests for a talent/week
