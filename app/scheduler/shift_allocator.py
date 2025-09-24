from app.entities.entities import shiftSpecification, talentAvailability, assignment
from app.scheduler.generators import TalentGenerator, talentByRole
from app.scheduler.validators import validators, dailyAssignmentValidator, context
from datetime import datetime

class shiftAssignment():
    def __init__(self, availability: dict[int, talentAvailability], assignable_shifts: list[shiftSpecification], talents_to_assign: dict[str, list[talentByRole]]):
        """Initialize the proposal generator for potential shift assignments.

        Builds the internal availability lookup and prepares the daily assignment tracker.

        Args:
            availability (dict[int, talentAvailability]): Mapping of talent IDs to their availability.
            assignable_shifts (list[shiftSpecification]): List of shifts that need potential assignment.
            talents_to_assign (dict[str, list[talentByRole]]): Mapping of role names to lists of available talents.
        """
        self.availability = availability
        self.talents_to_assign = talents_to_assign
        self.assignable_shifts = assignable_shifts


    def generate_schedule(self):
        """Generate all eligible assignments based on talent availability, constraints, and validators.

        Iterates through assignable shifts, checks for eligible talents according to role, availability,
        daily assignment, weekly hours, and other validators, and returns a list of Assignment objects.

        Returns:
            list[assignment]: List of assignments that satisfy all validation rules.
        """

        window = {
        (tid, date): [(datetime.combine(date, start), datetime.combine(date, end)) for start, end in spans]
        for tid, avail in self.availability.items()
        for date, spans in avail.window.items()
            }

        plan: list[assignment] = []
        dailyValidator = dailyAssignmentValidator()
        constrained = [talent.talent_id for _, talent in self.availability.items() if talent.constraint is not None]
        unconstrained = [talent.talent_id for _,talent in self.availability.items() if talent.constraint is None]
        
        for shift in self.assignable_shifts: 
            num_assigned = 0
            generate = TalentGenerator(shift, self.talents_to_assign, window)
            candidates = list(generate.find_eligible_talents())
            sorted_candidates = [tid for tid in candidates if tid in constrained]+\
                                [tid for tid in candidates if tid in unconstrained]
            for talent_id in sorted_candidates:
                if num_assigned >= shift.role_count:
                    break

                ctx = context.contextFinder(talent_id, shift, self.availability, plan)
                if shift.shift_name in self.availability[talent_id].shift_name:
                    if all(validator.can_assign_shift(ctx) for validator in validators):
                        plan.append(assignment(talent_id=talent_id, shift=shift))
                        check = dailyAssignmentValidator()
                        mark_assigned = check.mark_assigned(ctx)
                        num_assigned += 1
                
        return plan


class unAssignedShiftTracker():

    @staticmethod
    def get_unassigned_shifts(schedule: list[assignment], shifts: list[shiftSpecification]):
        return [shift for shift in shifts if shift not in [a.shift for a in schedule]]



