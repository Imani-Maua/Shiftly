from fastapi import Depends
import asyncpg
from typing import Annotated
from app.infrastructure.database.database import dataFrameAdapter, asyncSQLRepo, get_db, db_pool
from app.infrastructure.datasource.request_data import requestProcessor, create_request_objects
from app.infrastructure.datasource.talent_data import filterTalents, talentAvailabilityDf, create_talent_objects
from app.infrastructure.datasource.shift_data import weekBuilder, defineShiftRequirements, create_shift_specification
from app.core.services.scheduler.generators import talentByRole
from app.core.services.utils.utils import fetch_staffing_req


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
    group_talents = talentByRole.group_talents(talent_objects)
    return group_talents

async def process_shift_data(schedule_week, db: Annotated[asyncpg.Connection, Depends(get_db)]):

    shift_repo = await asyncSQLRepo(db, "SELECT * from shift_data").getData()
    shift_df = dataFrameAdapter.to_dataframe(shift_repo)
    staffing = fetch_staffing_req()
    build_week = weekBuilder(schedule_week, staffing)
    week_requirements = build_week.shiftRequirements()
    week_shifts = defineShiftRequirements.shiftRequirements(week_requirements, shift_df)
    shift_objects = create_shift_specification(week_shifts)
    return shift_objects




