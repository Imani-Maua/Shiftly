from fastapi import Depends
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import DatabaseError as AlchemyDatabaseError
from typing import Annotated, Union
from datetime import date
import asyncpg
from app.database.database import get_db
from app.database.session import session
from app.core.utils.helpers import get_week_range
from app.core.schedule.schema import inputDate
from app.core.schedule.services.data_services import process_request_data, process_shift_data, process_talent_data, approvedHolidayRequests
from app.core.schedule.services.generators import talentByRole
from app.core.schedule.services.shift_allocator import shiftAssignment, UnderstaffedShifts
from app.core.utils.exceptions import ValidationError, DatabaseError, NotFoundError, AppBaseException
from app.database.models import Schedule



class ScheduleService:
    def __init__(self, db: Union[Session, asyncpg.Connection]):
        self.db = db

    @staticmethod
    async def generate_schedule(db: Annotated[asyncpg.Connection, Depends(get_db)], start_date: inputDate):
        try:
            week_for_schedule = get_week_range(start_date=start_date)
            talent_objects = await process_talent_data(week_for_schedule, db)
            shift_openings = await process_shift_data(week_for_schedule, db)
            placed_requests = await process_request_data(db)
            approved_requests = await approvedHolidayRequests.process_approved_holidays(db, talent_objects, placed_requests)
            talents_by_role = talentByRole.group_talents(approved_requests)
            shift_assignments = shiftAssignment(approved_requests, shift_openings, talents_by_role)
            generated_assignments = shift_assignments.generate_schedule()

            understaffed = UnderstaffedShifts(db, shift_openings, generated_assignments)

            return {
                "status": "completely filled" if not understaffed else "understaffed",
                "genereated_assignments": generated_assignments,
                "understaffed_shifts": understaffed
            }
        except ValueError as e:
            raise ValidationError(f"Invalid input: {e}")
        except asyncpg.PostgresError as e:
            raise DatabaseError("A database error has occurred during schedule generation. Please try again")
        except KeyError as e:
            raise NotFoundError(f"Missing key during schedule generation: {e}")
        except Exception as e:
            raise AppBaseException(f"Internal Server error during schedule generation: {e}")
    
    async def get_schedule_by_week_start(self, week_start: date):
        try:

            schedule = self.db.query(Schedule).options(joinedload(Schedule.scheduled_shifts)).filter(Schedule.week_start == week_start).first()
            if not schedule:
                raise NotFoundError(f"Schedule does not exist")
            return schedule
        except ValueError as e:
            raise ValidationError(f"Invalid date format.")
        except AlchemyDatabaseError as e:
            raise DatabaseError("A database error has occured during schedule generation. Please try again.")
        except Exception as e:
            raise AppBaseException(f"Internal Server Error while retrieving schedule.")

    
            

