from dataclasses import dataclass, field
from datetime import datetime
import enum
import pandas as pd
from typing import Type

class Role(enum.Enum):
    leader = "leader"
    server = "server"
    bartender = "bartender"
    hostess = "hostess"
    runner = "runner"

@dataclass
class dbCredentials:
    host: str
    dbname: str
    user: str
    password: str

@dataclass
class shiftSpecification:
    start_time: datetime
    end_time: datetime
    shift_name: str
    role_name: Role
    role_count: int

@dataclass
class talentAvailability:
    talent_id: int
    constraint: bool
    role: Role
    shift_name: str
    window: dict[datetime, tuple[datetime, datetime]] 
    weeklyhours: float

@dataclass
class assignment:
    talent_id : int
    shift_id: int
    shift : shiftSpecification

@dataclass
class weekRange:
    '''
     Represents a range of dates within a week and provides helper methods to
     access the week as a date range and as a mapping from weekday names to dates

     Attributes:
            start_date(str) : starting day of the week (string format, parsed to datetime)
            end_date(str) : ending day of the week (string format, parsed to datetime)
            week(pd.DatetimeIndex) : a range of dates between start_date and end_date
            date_map (dict): a mapping of days of the week to the date, useful since the database is
            not date specific, so the map helps us to map the dates that need to be processed to the day
            repo(pd.DataFrame) : a DataFrame either for talents or shifts to which the date range will be applied
        '''
    start_date: str
    end_date: str
    week: pd.DatetimeIndex = field(init=False)
    date_map: dict = field(init=False)
    def __post_init__(self) -> None:
        '''
        Converts start_date and end_date to datetime.date objects,
        generates the range and builds the day to date mapping
        '''
        self.start_date = pd.to_datetime(self.start_date)
        self.end_date = pd.to_datetime(self.end_date)
        self.week = pd.date_range(self.start_date, self.end_date)
        self.date_map = {day.strftime("%A"): day for day in self.week}


    def get_week(self) ->pd.DatetimeIndex:
        '''
        Return:
            pd.DatetimeIndex: The week as a pandas date range
        '''
        return self.week

    def get_date_map(self) ->dict[str, pd.Timestamp]:
        '''
        Returns:
            dict[str, pd.Timestamp]: a dictionary mapping of days of the week to their corresponding date
        '''
        return self.date_map

@dataclass
class placedRequests:
    request_date: datetime
    request_status: str
    request_type: str
    leave_days: int
    paid_taken: int

@dataclass
class underStaffedShifts:
    shift_id: int
    shift_name: str
    shift_start: datetime
    shift_end: datetime
    role_name: str
    required: int
    assigned: int
    missing: int



