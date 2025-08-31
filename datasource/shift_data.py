from abc import ABC, abstractmethod
import pandas as pd
from app.database import SessionLocal
from app.models import Shift_Period, Shift_Template, String, staffing, staffing_days
from sqlalchemy import func, cast
from app.utils.utils import fetch_all_shifts
from app.data_class import weekRange
from datetime import datetime, timedelta
from pprint import pprint
from app.data_class import shiftSpecification


class shiftRepository(ABC):

    @abstractmethod
    def get_shifts(self):
        pass
    def open_shifts(self):
        pass

class dbShiftRepository(shiftRepository):
    def get_shifts(self) -> pd.DataFrame:
        db = SessionLocal() #this has to be refactored
        query = db.query(
        Shift_Period.id.label('period_id'),
        cast(Shift_Period.staffing, String).label("staffing"),
        Shift_Period.label.label('shift'),
        Shift_Period.start,
        Shift_Period.end,
        cast(Shift_Template.role, String).label('role'),
        Shift_Template.count
    ).join(Shift_Template, Shift_Period.id == Shift_Template.period_id, isouter=True)
        shift_df = pd.read_sql(query.statement, db.bind)
        return shift_df

class create_shift_requirements_df(weekRange):
    def shift_requirements_df(self) -> pd.DataFrame:
       requirement_df = pd.DataFrame({'date': [day.date() for day in self.get_week()]})
       requirement_df.loc[:, 'day'] = [day.strftime("%A") for day in self.get_week()]
       requirement_df.loc[:, 'staffing'] = requirement_df['day'].apply(lambda day: staffing.low.value if day in staffing_days[staffing.low] else staffing.high.value)
       week_shifts = requirement_df.merge(self.repo[['staffing', 'shift', 'start', 'end', 'role', 'count']], on='staffing', how='left')
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
        shift.pop('day'); shift.pop('staffing'); shift.pop('shift')
        shift_specification_object.append(shiftSpecification(**shift))

    return shift_specification_object
today = datetime.now()
week = today + timedelta(days=6)

repo = dbShiftRepository().get_shifts()

obj = create_shift_requirements_df(start_date=today, end_date=week, repo=repo).shift_requirements_df()
print(obj)




    
        
        
    
    
    

