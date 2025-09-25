from datetime import datetime, timedelta
from app.database.database import postgreContextManager, postgreCredentials, dataFrameAdapter
from app.datasource.talent_data import dbTalentRepo, filterTalents, talentAvailabilityDf, create_talent_objects
from app.entities.entities import weekRange
from app.datasource.shift_data import dbShiftRepo, weekBuilder,defineShiftRequirements, create_shift_specification
from app.utils.utils import fetch_staffing_req
from app.scheduler.generators import talentByRole
from app.scheduler.shift_allocator import shiftAssignment
from pprint import pprint



class DataRetriever():
    def __init__(self, repo):
        self.repo = repo

    def fetch_data(self):
        credentials = postgreCredentials()
        conn = postgreContextManager(credentials)
        retrieve_repo = self.repo(conn)
        data = retrieve_repo.getData()
        return data

class BuildDataFrame():
    def __init__(self, raw_data):
        self.raw_data = raw_data

    def convertToDataFrame(self):
        to_df = dataFrameAdapter.to_dataframe(self.raw_data)
        return to_df
    
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

class talentDataManager():
    def __init__(self,talents_df, week_range):
        self.talents_df = talents_df
        self.week_range = week_range
    def generate_talent_objects(self):
        filterer = filterTalents(self.talents_df, self.week_range)
        all_tal = talentAvailabilityDf(filterer)
        all_talents = all_tal.combine_talents()
        my_talents = create_talent_objects(all_talents)
        return my_talents
    
class shiftDataManager():
    def __init__(self, shift_df, week_range):
        self.shift_df = shift_df
        self.week_range = week_range
    
    def generate_shift_objects(self):
        staffing = fetch_staffing_req()
        weekly_builder = weekBuilder(self.week_range, staffing)
        weekly_req = weekly_builder.shiftRequirements()
        shifts = defineShiftRequirements.shiftRequirements(weekly_req, shift_df)
        shift_specs = create_shift_specification(shifts)
        return shift_specs

#database connection and data retrival
credentials = postgreCredentials() 
conn = postgreContextManager(credentials) 

#generate week dates for the schedule
schedule_week = defineShiftWeek.week_for_schedule()

#processing talent data
talent_data = DataRetriever(dbTalentRepo).fetch_data() 
process_talent = BuildDataFrame(talent_data)
talent_df = process_talent.convertToDataFrame()
process_talent_df = talentDataManager(talent_df, schedule_week)
talent_objects = process_talent_df.generate_talent_objects()

#processing shift data
shift_data = DataRetriever(dbShiftRepo).fetch_data()
process_shift= BuildDataFrame(shift_data)
shift_df = process_shift.convertToDataFrame()
process_shift_df = shiftDataManager(shift_df, schedule_week)
shift_objects = process_shift_df.generate_shift_objects()

#generating talents by role and availability

talent_group = talentByRole.group_talents(talent_objects)


#generating the schedule

scheduler = shiftAssignment(talent_objects, shift_objects, talent_group)
schedule = scheduler.generate_schedule()


pprint(schedule)