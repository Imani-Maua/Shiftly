from models import  Shift_Period, Shift_Template, staffing, staffing_days
from sqlalchemy.orm import Session
from database import SessionLocal
import pandas as pd

db = SessionLocal()
def load_shift_periods(db: Session):
    query = db.query(
        Shift_Period.id.label('period_id'),
        Shift_Period.staffing.label("staffing"),
        Shift_Period.label.label('shift'),
        Shift_Period.start,
        Shift_Period.end,
        Shift_Template.role.label('role'),
        Shift_Template.count
    ).join(Shift_Template, Shift_Period.id == Shift_Template.period_id, isouter=True)

    df = pd.read_sql(query.statement, db.bind)
    return df

def shift_requirements(start_date, end_date) :
    templates = load_shift_periods(db)
    week = pd.date_range(start_date, end_date)
    #here I built the dataframe from scratch then merged it with the existing templates based on matching staffing requirements
    week_df = pd.DataFrame({'date': [day.date() for day in week]})
    week_df.loc[:, 'day'] = [day.strftime("%A") for day in week]
    week_df.loc[:, 'staffing'] = week_df['day'].apply(lambda day: staffing.low.value if day in staffing_days[staffing.low] else staffing.high.value)
    week_shifts = week_df.merge(templates[['staffing', 'shift', 'start', 'end', 'role', 'count']],on='staffing',how='left')
    return week_shifts


shifts = load_shift_periods(db)





#this is test data to check if the code is working


#load_shift_periods(db)
#load_talents(db)
#talent= talent_availability(today, week)
#objects = create_talent_objects(talent)
#pprint(objects)

#data = shift_requirements(today, week)
#objects = create_shift_specification(data)
#print(objects)
#pprint(data.to_dict('records'))
#schedule_talents(today, week)


# create classes for rules to be followed



