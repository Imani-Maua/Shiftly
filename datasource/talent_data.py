from abc import ABC, abstractmethod
import pandas as pd
from datetime import timedelta, datetime, date
from app.data_class import talentAvailability
from app.utils.utils import map_label_to_time, fetch_all_shifts
from app.data_class import weekRange, dbCredentials
from app.database.database import postgreDBConnection, executeQuery
from psycopg2.extras import RealDictCursor
from pprint import pprint




#think about how I am going to import and use get_db() which opens a database session, and closes it


class talentRepo(ABC):

    '''
    Abstract base class for a TalentRepository

    Defines the interface for fetching talent data
    '''
    @abstractmethod
    def get_talents(self):

        pass

class dbTalentRepo(talentRepo):
    '''
    
    '''
    def __init__(self, db_connection):
        self.db_session = db_connection
    def get_talents(self) -> list:
        '''
        Fetches all the talents and their related data from the database

        Args:
            db.connection: A connection object to the database

        Returns:
            list: list[psycopg2.extras.RealDictRow]
        '''
        conn = self.db_session.opendb()
        try:
            query = "SELECT * FROM talent_data"
            results = executeQuery.runQuery(conn, query, fetch=True)
        finally:
            self.db_session.closedb()
        
        return results


class talentDataFrameAdapter:
     @staticmethod
     def to_dataframe(talents:list) -> pd.DataFrame:
             return pd.DataFrame(talents)
                
class filterTalents:
    def __init__(self, repo: pd.DataFrame, week_provider: weekRange):
        self.repo = repo
        self.week_provider = week_provider

    def create_constrained_df(self) -> pd.DataFrame:
        '''
        returns a formmatted dataframe of talents who have constraints.
        Each row containts in the output DataFrame represents a unique talent and contains:
          talent's id: int,
          role: str, 
          date:(list[datetime.time]): list of dates a talent is available to work,
          shifts(list[shifts]): A list of shifts the talent is available to work on those dates.

        Return:
            Dataframe: Aggregated and formmatted Dataframe of constrained talents
        '''
        constrained = self.repo.groupby(['talent_id', 'available_day']).agg({'available_shifts': lambda x: list(set(x)), 'tal_role': 'first'}).reset_index().copy()
        constrained.loc[:, 'available_date'] = constrained['available_day'].map(self.week_provider.get_date_map()).dt.date
        return constrained.groupby('talent_id').agg({'talent_id': 'first', 'tal_role': 'first', 'available_date': list, 'available_shifts': 'first'})

    def create_unconstrained_df(self) -> pd.DataFrame:
        '''
        Returns a formatted dataframe of talents who can work anyday for any shift
        Each row containts in the output DataFrame represents a unique talent and contains:
          talent's id: int,
          role: str, 
          date:(list[datetime.time]): list of dates a talent is available to work,
          shifts(list[shifts]): A list of shifts the talent is available to work on those dates.
        
        Args:
            shifts: list of all available shifts in a day
        Return:
            Dataframe: formmatted dataframe of unconstrained talents.
        '''
        unconstrained = self.repo.copy()
        unconstrained.loc[:, 'available_date'] = [list(self.week_provider.get_week())] * len(unconstrained)
        unconstrained['available_date'] = unconstrained['available_date'].apply(lambda lst: [d.date() for d in lst])
        unconstrained = unconstrained[['talent_id', 'tal_role', 'available_date']]
        unconstrained.loc[:, 'available_shifts'] = [fetch_all_shifts()] * len(unconstrained)
        unconstrained = unconstrained.drop_duplicates(subset=['talent_id'])
        return unconstrained
    

class talentAvailabilityDf: 
    def __init__(self, filter_obj: filterTalents):
        self.filter = filter_obj
        self.constrained = self.filter.create_constrained_df()
        self.unconstrained = self.filter.create_unconstrained_df()

    def combine_talents(self):
        '''
        Returns a concatenated dataframe of both constrained and unconstrained talents.
        It is imperative to have format the constrained/unconstrained talents separately because the dates and shifts
        for talents with constraints have to be filtered out first

        Returns:
            Dataframe: All talents and the days that they are available to work

        '''
        return pd.concat([self.constrained, self.unconstrained], ignore_index=True)
    

credentials = dbCredentials(
    host="localhost",
    dbname="scheduler",
    user="mauaimani",
    password="WayneWilliam",
    cursor_factory= RealDictCursor
)

      
def create_talent_objects(talents: pd.DataFrame, weeklyhours: float = 32) -> list[talentAvailability]:
    """
    Returns a list of talent objects from the talent dataframes

    Args:
        talents: dataframe with all available talents
    Return:
        list: talentAvailabilty
    """
    talent_list = talents.to_dict('records')
    talent_object = []
    for talent in talent_list:
        for date in list(talent.get('available_date', [])):
            window: dict = {}
            window[date] = []
            for shift in list(talent.get('available_shifts', [])):
                shift_span = map_label_to_time(shift)
                window[date].append(shift_span)
            talent_object.append(talentAvailability(
                talent_id=talent.get('talent_id'),
                role=talent.get('tal_role'),
                window=window,
                weeklyhours=weeklyhours
            ))
    return talent_object


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

print(create_talent_objects(all_talents))

       

    

