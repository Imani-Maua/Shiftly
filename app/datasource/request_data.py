import pandas as pd
from collections import defaultdict
from datetime import date
from app.entities.entities import placedRequests


class requestProcessor():

    @staticmethod
    def groupRequests(repo) -> pd.DataFrame:
        repo['request_date'] = pd.to_datetime(repo['request_date'])
        repo['request_date'] = repo['request_date'].apply(lambda d: d.date())
        return repo
       


def create_request_objects(requests: pd.DataFrame) -> dict[int, list[date]]:
    request_list = requests.to_dict('records')
    request_object = defaultdict(list)
    for request in request_list:
        request_object[request.get('talent_id', [])].append(placedRequests(
            request_date=request.get('request_date', []),
            request_status=request.get('status', []),
            request_type=request.get('holiday_type', []),
            leave_days=request.get('leave_days', []),
            unpaid_taken=request.get('unpaid_taken', [])))

    return request_object
    
    