from abc import ABC, abstractmethod
from entities.data_class import talentAvailability, shiftSpecification

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

    def mark_assigned(self, talent: talentAvailability, shift: shiftSpecification):
        self.assigned.add((talent.talent_id, shift.date))

    def check(self, talent: talentAvailability, shift: shiftSpecification) -> bool:
        return (talent.talent_id, shift.date) in self.assigned

#a list of rules that a talent must satisfy before being assigned to a shift
eligibility_rules = [roleShiftValidator(), dateMatcher()]

class RulesEvaluator():
    def __init__(self, eligibility: list[Constraints], talent:talentAvailability, shift:shiftSpecification):
        self.eligibility = eligibility
        self.talent = talent
        self.shift = shift

    def all_pass(self):
        return all(rule.check(self.talent, self.shift) for rule in self.eligibility)