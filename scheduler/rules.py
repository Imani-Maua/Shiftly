from abc import ABC, abstractmethod

    
class Constraints(ABC):
    @abstractmethod
    def check(self, talent: object, shift: object) ->bool:
        raise NotImplementedError

class roleShiftValidator(Constraints):
    def check(self, talent: object, shift:object) -> bool:
        return talent.role == shift.role_name
    
class dateMatcher(Constraints):
    def check(self, talent, shift):
        return shift.date in talent.window.keys()

    
class dailyAssignmentTracker(Constraints):

    def __init__(self):
        self.assigned = set()

    def mark_assigned(self, talent_id, shift_date):
        self.assigned.add((talent_id, shift_date))

    def check(self, talent_id, shift_date) -> bool:
        return (talent_id, shift_date) in self.assigned 
    
#a list of rules that a talent must satisfy before being assigned to a shift 
eligibility_rules = [roleShiftValidator(), dateMatcher()]

class RulesEvaluator():
    def __init__(self, eligibility: list, talent:object, shift:object):
        self.eligibility = eligibility
        self.talent = talent
        self.shift = shift

    def all_pass(self):
        return all(rule.check(self.talent, self.shift) for rule in self.eligibility)