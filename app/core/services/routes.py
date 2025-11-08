from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import date, timedelta, datetime
from typing import Annotated
import asyncpg
from app.core.services.utils.models import ShiftPeriod
from app.core.services.utils.pydantic import inputDate, ShiftOut, ShiftPeriodCreate, ShiftPeriodUpdate
from app.core.services.utils.utils import get_week_range
from app.core.services.scheduler.data_services import process_request_data, process_shift_data, process_talent_data, approvedHolidayRequests
from app.core.services.scheduler.generators import talentByRole
from app.core.services.scheduler.shift_allocator import shiftAssignment, UnderstaffedShifts
from app.infrastructure.database.database import get_db, session
from app.auth.security import required_roles
from app.auth.models import UserRole
from app.core.services.utils.crud import CRUDBase




schedule = APIRouter()
holidays = APIRouter()
talents = APIRouter()


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
    

@schedule.post("/shift_period/create")
async def create_shift_period(db: Annotated[Session, Depends(session)],
                              data: Annotated[ShiftPeriodCreate, Body()],
                              _: str = Depends(required_roles(UserRole.admin, UserRole.manager))):
    period_generator = CRUDBase[ShiftPeriod, ShiftPeriodCreate, ShiftPeriodCreate](ShiftPeriod)
    

    shift_period = period_generator.create(db,data)
    return ShiftOut(
        id=shift_period.id,
        shift_name=shift_period.shift_name,
        start_time=shift_period.start_time,
        end_time=shift_period.end_time,
    )
    

@schedule.patch("/shift_period/{period_id}")
async def update_shift_period(db: Annotated[Session,  Depends(session)],
                              period_id: int,
                              update_data: Annotated[ShiftPeriodUpdate, Body()],
                              _: str= Depends(required_roles(UserRole.admin, UserRole.manager))
                                ):
    crud_shift = CRUDBase[ShiftPeriod, ShiftPeriodCreate, ShiftPeriodUpdate](ShiftPeriod)
    shift_period = db.query(ShiftPeriod).get(period_id)
    if not shift_period:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shift period not found")
    updated_shift = crud_shift.update(db, shift_period, update_data)
    return ShiftOut(
            id=updated_shift.id,
            shift_name=updated_shift.shift_name,
            start_time=updated_shift.start_time,
            end_time=updated_shift.end_time
        )


@talents.post("/create_talent")
async def create_talent():
    pass


 #submit a request
   
#view unassigned shifts

#view talent availability



#update the status of a request
#list all the requests for a talent/week
