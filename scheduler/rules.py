from abc import ABC, abstractmethod
from app.entities.entities import talentAvailability, shiftSpecification
from datetime import date

class Constraints(ABC):
    @abstractmethod
    def check(self, talent: talentAvailability, shift: shiftSpecification) ->bool:
        raise NotImplementedError

class roleShiftValidator(Constraints):
    def check(self, talent: talentAvailability, shift: shiftSpecification) -> bool:
        return talent.role == shift.role_name

class dateMatcher(Constraints):
    def check(self, talent: talentAvailability, shift: shiftSpecification):
        return shift.date in talent.window.keys()


class dailyAssignmentTracker(Constraints):

    def __init__(self):
        self.assigned = set()

    def mark_assigned(self, talent_id: int, shift_date: date):
        self.assigned.add((talent_id, shift_date))

    def check(self, talent: int, shift_date: date) -> bool:
        return (talent, shift_date) in self.assigned

#a list of rules that a talent must satisfy before being assigned to a shift
eligibility_rules = [roleShiftValidator(), dateMatcher()]

class RulesEvaluator():
    def __init__(self, eligibility: list[Constraints], talent:talentAvailability, shift:shiftSpecification):
        self.eligibility = eligibility
        self.talent = talent
        self.shift = shift

    def all_pass(self):
        return all(rule.check(self.talent, self.shift) for rule in self.eligibility)