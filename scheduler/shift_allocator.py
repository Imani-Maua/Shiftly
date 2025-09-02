
from app.scripts.demo import fetch_shifts, fetch_talents
from app.dataclasses.data_class import eligibleTalents, shiftSpecification, assignment, shiftInfo
from rules import RulesEvaluator, dailyAssignmentTracker, Constraints
    
class eligibleTalentFinder():
    def __init__(self, talents: list[object], shifts: list[object], rules: list[Constraints]) ->list[eligibleTalents] :
        self.talents = talents
        self.shifts = shifts
        self.rules = rules

    def get_available_talents_per_shift(self):
        eligible_shifts = []

        for shift in self.shifts:
            shift_info = (eligibleTalents(
                        shift_date=shift.date,
                        start_time= shift.start_time,
                        end_time=shift.end_time,
                        talents=[]
                    ))
            
            shift_count = (shiftInfo(role_count=shift.role_count,
                                     shift_info=shift_info))
            for talent in self.talents:
                evaluator = RulesEvaluator(self.rules, talent, shift)
                if evaluator.all_pass():
                    shift_info.talents.append(talent)
            eligible_shifts.append(shift_count)

        return eligible_shifts
       
class shiftAllocator():
    def __init__(self, shift_info: shiftInfo, daily_checker: dailyAssignmentTracker) -> list:
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






















