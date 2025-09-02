from app.database.database import dbCredentials, postgreDBConnection
from app.datasource.talent_data import dbTalentRepo, talentDataFrameAdapter, filterTalents, talentAvailabilityDf, create_talent_objects 
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
from app.dataclasses.data_class import weekRange
from app.datasource.shift_data import dbShiftRepo, shiftDataFrameAdapter, weekBuilder,defineShiftRequirements, create_shift_specification
from app.utils.utils import fetch_staffing_req





def fetch_shifts():
    credentials = dbCredentials(
    host="localhost",
    dbname="yourdbname",
    user="yourusername",
    password="yourpassword",
    cursor_factory= RealDictCursor
)
    conn = postgreDBConnection(credentials)
    repo = dbShiftRepo(conn)
    shifts = repo.getShifts()
    today = datetime.now()
    week = today + timedelta(days=6)
    shift_df = shiftDataFrameAdapter.toDataFrame(shifts)


    week = weekRange(
        start_date=today,
        end_date=week
    )
    staffing = fetch_staffing_req()
    shift_week = weekBuilder(week, staffing)
    shift_week1 = shift_week.shiftRequirements()
    shifts = defineShiftRequirements.shiftRequirements(shift_week1, shift_df)
    shift_specs = create_shift_specification(shifts)
    return shift_specs

        




def fetch_talents():
    credentials = dbCredentials(
    host="localhost",
    dbname="yourdbname",
    user="yourusername",
    password="yourpassword",
    cursor_factory= RealDictCursor
)

    psql = postgreDBConnection(credentials)
    talents= dbTalentRepo(psql)
    talent_data = talents.get_talents()
    talent_df = talentDataFrameAdapter.to_dataframe(talent_data)
    today = datetime.now()
    week = today + timedelta(days=6)
    
    
    
    week_range = weekRange(
        start_date=today,
        end_date=week
    )
    filterer = filterTalents(talent_df, week_range)
    all_tal = talentAvailabilityDf(filterer)
    all_talents = all_tal.combine_talents()

    my_talents = create_talent_objects(all_talents)
    return my_talents







   

