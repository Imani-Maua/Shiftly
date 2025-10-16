import asyncio
from datetime import datetime, timedelta
from app.database.database import dataFrameAdapter, asyncSQLRepo, get_db, db_pool
from app.entities.entities import weekRange
from app.datasource.shift_data import weekBuilder,defineShiftRequirements, create_shift_specification
from app.datasource.talent_data import filterTalents, talentAvailabilityDf, create_talent_objects
from app.datasource.request_data import requestProcessor, create_request_objects
from app.utils.utils import fetch_staffing_req
from app.scheduler.generators import talentByRole
from app.scheduler.shift_allocator import shiftAssignment
from pprint import pprint


    
class defineShiftWeek():
    @staticmethod
    def week_for_schedule():
        today = datetime.now()
        week = today + timedelta(days=6)
        week = weekRange(
            start_date=today,
            end_date=week
        )
        return week
    

async def main():
    # ---- initialize the pool ----
    await db_pool()

    # --- open database connection ---
    async for conn in get_db():

        # --- generate week dates for the schedule ---
        schedule_week = defineShiftWeek.week_for_schedule()

        # --- fetch talent data ---
        talent_repo = asyncSQLRepo(conn, "SELECT * FROM talent_data")
        talent_data = await talent_repo.getData()
        talent_df = dataFrameAdapter.to_dataframe(talent_data)
        process_talent_df = filterTalents(talent_df, schedule_week)
        all_tal = talentAvailabilityDf(process_talent_df).combine_talents()
        talent_objects = create_talent_objects(all_tal)
        talent_group = talentByRole.group_talents(talent_objects)

        # --- fetch shift data ---
        shift_repo = asyncSQLRepo(conn, "SELECT * FROM shift_data")
        shift_data = await shift_repo.getData()
        shift_df = dataFrameAdapter.to_dataframe(shift_data)
        staffing = fetch_staffing_req()
        weekly_builder = weekBuilder(schedule_week, staffing)
        weekly_req = weekly_builder.shiftRequirements()
        shifts = defineShiftRequirements.shiftRequirements(weekly_req, shift_df)
        shift_specs = create_shift_specification(shifts)

        # ------ requests -----
        request_repo = asyncSQLRepo(conn, "SELECT * FROM request_data")
        request_data = await request_repo.getData()
        request_df = dataFrameAdapter.to_dataframe(request_data)
        processed_requests = requestProcessor.change_to_datetime_objects(request_df)
        request_objects = create_request_objects(processed_requests)
        pprint(talent_objects)

        # --- generate schedule ---
        scheduler = shiftAssignment(talent_objects, shift_specs, talent_group)
        schedule = scheduler.generate_schedule()

        
        

    
if __name__ == '__main__':
    asyncio.run(main())