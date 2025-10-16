import pandas as pd
import asyncpg
from app.infrastructure.database.database import asyncSQLRepo
from app.core.entities.entities import talentAvailability, weekRange
from app.core.entities.entities import placedRequests
from app.infrastructure.utils.utils import map_label_to_time, fetch_all_shifts


class filterTalents:
    '''
    Class that filters out talents based on whether they have active constraints or not.
    '''
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
        constrained = self.repo.loc[(self.repo['constraint_status'].notna())].copy()
        constrained = constrained.groupby(['talent_id','constraint_status', 'available_day']).agg({'available_shifts': lambda x: list(set(x)), 'tal_role': 'first','hours': 'first'}).reset_index()
        constrained.loc[:, 'available_date'] = constrained['available_day'].map(self.week_provider.get_date_map()).dt.date
        return constrained.groupby('talent_id').agg({'talent_id': 'first', 'constraint_status': 'first' ,'tal_role': 'first','hours': 'first', 'available_date': list, 'available_shifts': 'first'}).drop_duplicates(subset=['talent_id'])

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
        unconstrained = self.repo.loc[(self.repo['constraint_status'].isna())].copy()
        unconstrained.loc[:, 'available_date'] = [list(self.week_provider.get_week())] * len(unconstrained)
        unconstrained['available_date'] = unconstrained['available_date'].apply(lambda lst: [d.date() for d in lst])
        unconstrained = unconstrained[['talent_id', 'constraint_status','tal_role', 'hours', 'available_date']]
        unconstrained.loc[:, 'available_shifts'] = [fetch_all_shifts()] * len(unconstrained)
        unconstrained = unconstrained.drop_duplicates(subset=['talent_id'])
        return unconstrained

class talentAvailabilityDf:
    '''
    Class that concatenates the manipulated talent data into a single pd.DataFrame.

    Args:
        filter_obj: pd.DataFrame object which contains infomation about clients with and without constraints

    Return:
        pd.DataFrame: Manipulated talent data concatenated.

    '''
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

def create_talent_objects(talents: pd.DataFrame) -> list[talentAvailability]:
    """
    Returns a list of talent objects from the talent dataframes

    Args:
        talents: dataframe with all available talents
    Return:
        list: talentAvailabilty
    """
    talent_list = talents.to_dict('records')
    talent_object: dict[int, talentAvailability] = {}
    for talent in talent_list:
        window: dict = {}
        for date in list(talent.get('available_date', [])):
            window[date] = []
            for shift in list(talent.get('available_shifts', [])):
                shift_span = map_label_to_time(shift)
                window[date].append(shift_span)

        talent_object[talent.get('talent_id', [])] = talentAvailability(
                    talent_id=talent.get('talent_id'),
                    constraint=talent.get('constraint_status'),
                    role=talent.get('tal_role'),
                    shift_name=talent.get('available_shifts'),
                    window=window,
                    weeklyhours=talent.get('hours')
                                    )
    return talent_object


