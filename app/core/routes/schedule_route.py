from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session
from datetime import date
from typing import Annotated
import asyncpg
from app.infrastructure.database.database import get_db, session
from app.auth.security import required_roles
from app.auth.models import UserRole
from app.core.pydantic.pydantic import inputDate
from app.core.utils.models import Schedule
from app.core.services.schedule_service import ScheduleService



schedule = APIRouter()


@schedule.post("/generate")
async def generate_schedule(db: Annotated[asyncpg.Connection, Depends(get_db)],
                            start_date: Annotated[inputDate, Body()], 
                             _: str = Depends(required_roles(UserRole.superuser, UserRole.admin))):
    schedule = await ScheduleService.generate_schedule(start_date)
    return schedule


@schedule.get("/view/{week_start}")
async def view_schedule(db: Annotated[Session, Depends(session)],
                        week_start: date,
                        _: str = Depends(required_roles(UserRole.admin, UserRole.manager))):
    result = ScheduleService(db)
    schedule = await result.get_schedule_by_week_start(week_start)
    return schedule
    #set this such that you can only give a date that is on Sunday/Monday depending on when week_start is












