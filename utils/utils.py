from datetime import datetime, date, time
from pathlib import Path
import json

def map_label_to_time(label: str):
    label = label.lower()
    lookup = {
        'am': (time(6,0), time(15,0)),
        'pm': (time(15,0), time(23,30)),
        'lounge': (time(11,0), time(23,59))
    }
    return lookup.get(label, (time(6,0), time(15,0)))

def create_datetime(date, time):
    return datetime.combine(date, time)

def fetch_all_shifts():
    base_path = Path(__file__).parent.parent
    json_path = base_path/"config"/"shifts.json"
    with open(json_path) as p:
        shifts = json.load(p)['shifts']
    return shifts

