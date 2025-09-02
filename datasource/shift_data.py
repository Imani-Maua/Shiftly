from abc import ABC, abstractmethod
from app.database.database import executeQuery
from app.dataclasses.data_class import weekRange, shiftSpecification
import pandas as pd
from app.utils.utils import fetch_staffing_req



class shiftRepo(ABC):

    @abstractmethod
    def getShifts(self):
        pass
    
class dbShiftRepo(shiftRepo):

    #by the end of this class running, we have a list of dictonaries from the database which we need to transform into dataframes
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def getShifts(self):
        conn = self.db_connection.opendb()
        try:
            query = "SELECT * FROM shift_data"
            shifts = executeQuery.runQuery(conn, query, fetch=True)
        finally:
            self.db_connection.closedb()
        return shifts
    

class shiftDataFrameAdapter:
    @staticmethod
    def toDataFrame(shifts: list) -> pd.DataFrame:
        return pd.DataFrame(shifts)

class weekBuilder:
    def __init__(self, week_range: weekRange, req_provider:fetch_staffing_req):
        self.week_range = week_range
        self.req_provider = req_provider
    def shiftRequirements(self):
        week = self.week_range.get_week()
        week_df = pd.DataFrame({'date': [day.date() for day in week]})
        week_df.loc[:, "day"] = [day.strftime("%A") for day in week]
        staffing_req = self.req_provider
        week_df.loc[:, "staffing"] = week_df["day"].apply(lambda day: "low" if day in staffing_req["low"] else "high")
        return week_df
    
class defineShiftRequirements:
    @staticmethod
    def shiftRequirements(week_df: weekBuilder, shifts: pd.DataFrame) -> pd.DataFrame:
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
        shift.pop('day'); shift.pop('staffing'); shift.pop('shift_name')
        shift_specification_object.append(shiftSpecification(**shift))

    return shift_specification_object



        
    
    
    

