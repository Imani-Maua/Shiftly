from app.database.database import dbCredentials, postgreDBConnection
from app.datasource.talent_data import dbTalentRepo, talentDataFrameAdapter, filterTalents, talentAvailabilityDf, create_talent_objects 
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
from app.data_class import weekRange


if __name__ == '__main__':
    credentials = dbCredentials(
    host="localhost",
    dbname="scheduler",
    user="mauaimani",
    password="WayneWilliam",
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
    
    print(create_talent_objects(all_talents))