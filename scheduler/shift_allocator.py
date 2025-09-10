from app.entities.entities import shiftSpecification, assignment
from app.scheduler.rules import TalentGenerator, talentByRole, dailyAssignmentTracker
from datetime import date




class shiftAllocator():
    def __init__(self, assignable_shifts: list[shiftSpecification], talents_to_assign: dict[str, list[talentByRole]], lookup: dict[tuple[int, date], tuple[date, date]], generator: TalentGenerator, tracker:dailyAssignmentTracker):
        self.talents_to_assign = talents_to_assign
        self.assignable_shifts = assignable_shifts
        self.lookup = lookup
        self.generator = generator
        self.tracker = tracker

    def allocate_shifts(self):
        assigned = []
        for shift in self.assignable_shifts: 
            num_assigned = 0
            generate = self.generator(shift, self.talents_to_assign, self.lookup) 
            candidates = list(generate.find_eligible_talents())
            for talent_id in candidates:
                if not self.tracker.check(talent_id, shift.start_time.date()):
                    assigned.append(assignment(talent_id=talent_id, shift=shift))
                    self.tracker.mark_assigned(talent_id, shift.start_time.date())
                    num_assigned += 1
                if num_assigned >= shift.role_count:
                    break
        
        return assigned




            








class unAssignedShiftTracker():

    @staticmethod
    def get_unassigned_shifts(schedule: list[assignment], shifts: list[shiftSpecification]):
        return [shift for shift in shifts if shift not in [a.shift for a in schedule]]



