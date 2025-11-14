from fastapi import Depends
import asyncpg
from typing import Annotated
from app.database.database import dataFrameAdapter, asyncSQLRepo, get_db
from app.core.schedule.services.data.request_data import requestProcessor, create_request_objects
from app.core.schedule.services.data.talent_data import filterTalents, talentAvailabilityDf, create_talent_objects
from app.core.schedule.services.data.shift_data import weekBuilder, defineShiftRequirements, create_shift_specification
from app.core.schedule.services.entities import placedRequests, talentAvailability
from app.core.utils.helpers import fetch_staffing_req


async def process_request_data(db: Annotated[asyncpg.Connection, Depends(get_db)]):

    request_repo = await asyncSQLRepo(db, "SELECT * from request_data").getData()
    request_df = dataFrameAdapter.to_dataframe(request_repo)
    request_todatetime = requestProcessor.change_to_datetime_objects(request_df)
    request_objects = create_request_objects(request_todatetime)
    return request_objects

async def process_talent_data(schedule_week, db: Annotated[asyncpg.Connection, Depends(get_db)]):

    talent_repo = await asyncSQLRepo(db, "SELECT * from talent_data").getData()
    talent_df = dataFrameAdapter.to_dataframe(talent_repo)
    filter_talents = filterTalents(talent_df, schedule_week)
    combine_talents = talentAvailabilityDf(filter_talents).combine_talents()
    talent_objects = create_talent_objects(combine_talents)
    return talent_objects

async def process_shift_data(schedule_week, db: Annotated[asyncpg.Connection, Depends(get_db)]):

    shift_repo = await asyncSQLRepo(db, "SELECT * from shift_data").getData()
    shift_df = dataFrameAdapter.to_dataframe(shift_repo)
    staffing = fetch_staffing_req()
    build_week = weekBuilder(schedule_week, staffing)
    week_requirements = build_week.shiftRequirements()
    week_shifts = defineShiftRequirements.shiftRequirements(week_requirements, shift_df)
    shift_objects = create_shift_specification(week_shifts)
    return shift_objects

class paidHolidayQuota(): 
    
    @staticmethod
    async def can_take_paid_holiday(db:asyncpg.Connection, requests: dict[int,list[placedRequests]]):
        all_okay = True
        for tid, talent_requests in requests.items():
            total_requests = len(talent_requests)
            if total_requests + talent_requests[0].paid_taken > talent_requests[0].leave_days:
                for r in talent_requests:
                    r.request_status = "rejected"
                    all_okay = False
            else:
                for r in talent_requests:
                    r.request_status = "approved" 
                new_paid_taken = total_requests + talent_requests[0].paid_taken
                new_paid_taken_query = '''UPDATE requests 
                                            SET paid_taken = $1
                                                WHERE talent_id = $2'''
                execute_query = await asyncSQLRepo(conn=db, query=new_paid_taken_query, params=(new_paid_taken, tid,)).execute()

        return all_okay
    

class approvedHolidayRequests: 
    @staticmethod
    async def process_approved_holidays(db: asyncpg.Connection, talent_available_days: dict[int,talentAvailability], 
                       requests: dict[int, list[placedRequests]]) -> dict[int, talentAvailability]:
        
        await paidHolidayQuota().can_take_paid_holiday(db, requests)

        for tid, avail in talent_available_days.items():
            
            approved_requests = [req for req in requests[tid] if req.request_status == "approved"]
            requested_days = set()
            for req in approved_requests: requested_days.add(req.request_date)
            avail.window = {date:spans for date, spans in avail.window.items()if date not in requested_days}
        return talent_available_days



