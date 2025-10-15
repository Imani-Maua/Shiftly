
from app.datasource.talent_data import talentAvailability
from app.datasource.request_data import placedRequests


    
class paidHolidayQuota(): 
    
    @staticmethod
    def can_take_paid_holiday(requests: dict[int,list[placedRequests]]):
        all_okay = True
        for tid, talent_requests in requests.items():
            total_requests = len(talent_requests)
            if total_requests + talent_requests[0].unpaid_taken >= talent_requests[0].leave_days:
                for r in talent_requests:
                    r.request_status = "pending"
                    all_okay = False
            else:
                for r in talent_requests:
                    r.request_status = "approved" 
        return all_okay



class approvedHolidays(): 
    def removeHolidays(self, context) -> dict[int, talentAvailability]:
        availability: dict[int, talentAvailability] = context['availability']
        requests: dict [int, placedRequests]= context['requests']

        for tid, avail in availability.items():
            if requests[tid].request_status =='approved':
                requested_days = set(requests[tid].request_date)
                new_window = {date:spans for date, spans in avail.window.items()if date not in requested_days}
                avail.window = new_window
        return availability





   






    # if we give the paid holiday, we have to store the number of paid holidays that someone has been assigned.
    # Later on, we will add the functionality for checking how many hours are accounted for when someone takes a paid holiday so that this
    # is useful for payroll systems but for now, just count the number of paid holidays taken and subtract from the legal number of holidays remaining
    