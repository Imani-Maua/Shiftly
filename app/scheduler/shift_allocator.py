from app.entities.entities import shiftSpecification, talentAvailability, assignment
from app.scheduler.generators import TalentGenerator, talentByRole, dailyAssignmentTracker, MaxHoursValidators
from datetime import date


class shiftAllocator():
    pass


class unAssignedShiftTracker():

    @staticmethod
    def get_unassigned_shifts(schedule: list[assignment], shifts: list[shiftSpecification]):
        return [shift for shift in shifts if shift not in [a.shift for a in schedule]]



