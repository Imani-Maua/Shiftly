from app.entities.entities import eligibleTalents, shiftSpecification, assignment, shiftInfo, talentAvailability
from app.scheduler.rules import RulesEvaluator, dailyAssignmentTracker, Constraints

class eligibleTalentFinder():
    def __init__(self, talents: list[talentAvailability], shifts: list[shiftSpecification], rules: list[Constraints]):
        self.talents = talents
        self.shifts = shifts
        self.rules = rules

    def get_available_talents_per_shift(self):
        eligible_shifts: list[shiftInfo] = []

        for shift in self.shifts:
            shift_talents = (eligibleTalents(
                        shift_date=shift.date,
                        start_time= shift.start_time,
                        end_time=shift.end_time,
                        talents=[]
                    ))

            shift_info = (shiftInfo(role_count=shift.role_count, shift_info=shift_talents))
            for talent in self.talents:
                evaluator = RulesEvaluator(self.rules, talent, shift)
                if evaluator.all_pass():
                    shift_talents.talents.append(talent)
            eligible_shifts.append(shift_info)

        return eligible_shifts

class shiftAllocator():
    def __init__(self, shift_info: list[shiftInfo], daily_checker: dailyAssignmentTracker):
        self.shift_info = shift_info
        self.daily_checker = daily_checker


    def allocate_shifts(self) ->list:
        assignedShifts = []
        for eligible_shift in self.shift_info:
            num_assigned = 0
            for talent in eligible_shift.shift_info.talents:
                if not self.daily_checker.check(talent.talent_id, eligible_shift.shift_info.shift_date):
                    assignedShifts.append(assignment(
                    talent_id=talent.talent_id,
                    shift=shiftSpecification(
                        date=eligible_shift.shift_info.shift_date,
                        start_time=eligible_shift.shift_info.start_time,
                        end_time=eligible_shift.shift_info.end_time,
                        role_name=talent.role,
                        role_count=eligible_shift.role_count
                    )
                ))
                num_assigned += 1
                self.daily_checker.mark_assigned(talent.talent_id, eligible_shift.shift_info.shift_date)

                if num_assigned >= eligible_shift.role_count:
                    break

        return assignedShifts






















