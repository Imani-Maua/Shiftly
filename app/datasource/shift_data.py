import pandas as pd
from app.database.database import generateDataRepo, dbDataRepo
from app.entities.entities import weekRange, shiftSpecification
from app.utils.utils import fetch_staffing_req
from datetime import datetime


class dbShiftRepo(dbDataRepo):
    def __init__(self, conn):
        self.conn = conn

    def getData(self):
        query = "SELECT * FROM shift_data"
        repo = generateDataRepo(query, self.conn)
        return repo.retrieveData()



class weekBuilder:
    def __init__(self, week_range: weekRange, req_provider):
        self.week_range = week_range
        self.req_provider = req_provider
        
    def shiftRequirements(self): #rename the method
        week = self.week_range.get_week()
        week_df = pd.DataFrame({'date': [day.date() for day in week]})
        week_df.loc[:, "day"] = [day.strftime("%A") for day in week]
        staffing_req = self.req_provider
        week_df.loc[:, "staffing"] = week_df["day"].apply(lambda day: "low" if day in staffing_req["low"] else "high")
        return week_df

class defineShiftRequirements:
    @staticmethod
    def shiftRequirements(week_df: pd.DataFrame, shifts: pd.DataFrame) -> pd.DataFrame:
        week_shifts = week_df.merge(shifts[['staffing', 'shift_name', 'start_time', 'end_time', 'role_name', 'role_count']], on='staffing', how='left')
        return week_shifts



def create_shift_specification(shift_requirements: pd.DataFrame) -> list[shiftSpecification]:
    """
    Returns a list of objects from the shift_requirements dataframes

    Args:
        shift_requirements : dataframe of all shifts that need to be populated

    Return:
        list: shiftSpecification
    """
    shift_list = shift_requirements.to_dict('records')
    shift_specification_object = []
    for shift in shift_list:
        shift.pop('day'); shift.pop('staffing')
        shift_specification_object.append(shiftSpecification(
            start_time=datetime.combine(shift['date'], shift['start_time']),
            end_time=datetime.combine(shift['date'], shift['end_time']),
            shift_name=shift['shift_name'],
            role_name=shift['role_name'],
            role_count=shift['role_count']
        ))
        

    return shift_specification_object








