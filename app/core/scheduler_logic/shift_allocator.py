from datetime import datetime
from app.core.entities.entities import shiftSpecification, talentAvailability, assignment, underStaffedShifts
from app.core.scheduler_logic.generators import TalentGenerator, talentByRole
from app.core.scheduler_logic.validators import validators, context
from app.core.scheduler_logic.scheduler_scoring import computeScore, roundRobinPicker


class shiftAssignment():
    def __init__(self, availability: dict[int, talentAvailability], 
                 assignable_shifts: dict[int,shiftSpecification], 
                 talents_to_assign: dict[str, list[talentByRole]]):
        """Allocator responsible for generating a schedule of assignments.

        Args:
            availability (dict[int, talentAvailability]): 
                Mapping of talent IDs to their availability windows, weekly hours, and constraints.
            assignable_shifts (list[shiftSpecification]): 
                List of all shifts that need to be filled.
            talents_to_assign (dict[str, list[talentByRole]]): 
                Mapping of role names to their eligible talent objects.
        """
        self.availability = availability
        self.talents_to_assign = talents_to_assign
        self.assignable_shifts = assignable_shifts

    def generate_schedule(self) -> list[assignment]:
        """Generate a schedule of assignments.

        This method iterates through all assignable shifts and:
        - Builds a lookup window of availability.
        - Finds eligible candidates for each shift (via TalentGenerator).
        - Prioritizes constrained talents before unconstrained ones.
        - Scores candidates with computeScore.
        - Uses roundRobinPicker to fairly distribute assignments among top candidates.
        - Applies validators to enforce scheduling rules (e.g., daily, weekly, or rest requirements).
        - Appends valid assignments to the plan.

        Returns:
            list[assignment]: 
                A list of valid assignment objects for the scheduling period.
        """

        window = {
        (tid, date): [(datetime.combine(date, start), datetime.combine(date, end)) for start, end in spans]
        for tid, avail in self.availability.items()
        for date, spans in avail.window.items()
            }

        plan: list[assignment] = []
        constrained = [talent.talent_id for _, talent in self.availability.items() if talent.constraint is not None]
        unconstrained = [talent.talent_id for _,talent in self.availability.items() if talent.constraint is None]
        
        for shift_id, shift in self.assignable_shifts.items(): 
            generate = TalentGenerator(shift, self.talents_to_assign, window)
            candidates = list(generate.find_eligible_talents())
            sorted_candidates = [tid for tid in candidates if tid in constrained]+\
                                [tid for tid in candidates if tid in unconstrained]
            num_assigned = 0
            for talent_id in sorted_candidates:
                if num_assigned >= shift.role_count:
                    break
                scorer = computeScore(shift=shift, availability=self.availability, assignments=plan)
                top_candidates = scorer.getTopCandidates(candidates)
                round_robin = roundRobinPicker()
                best_fit = round_robin.pickBestFit(shift.role_name, top_candidates)
                ctx = context.contextFinder(talent_id, shift, self.availability, plan)
                if shift.shift_name in self.availability[talent_id].shift_name:
                    if all(validator.can_assign_shift(ctx) for validator in validators):
                        if best_fit:
                            plan.append(assignment(talent_id=talent_id, shift_id=shift_id, shift=shift))
                            for v in validators:
                                if hasattr(v, "mark_assigned"):
                                    v.mark_assigned(ctx)
                            num_assigned += 1   
        return plan


class UnderstaffedShifts:


    def __init__(self, conn, assignable_shifts: dict[int,shiftSpecification], assigned_shifts: list[assignment]):
        self.conn = conn
        self.assignable_shifts = assignable_shifts
        self.assigned_shifts = assigned_shifts
    
    def get_all(self) -> list:

        understaffed = []

        assigned_count: dict[int, int] = {}
        for assignment in self.assigned_shifts:
            assigned_count[assignment.shift_id] = assigned_count.get(assignment.shift_id, 0) + 1

        for shift_id, shift in self.assignable_shifts.items():
            required = shift.role_count
            assigned = assigned_count.get(shift_id, 0)
            if assigned < required:
                understaffed.append(underStaffedShifts(
                    shift_id=shift_id,
                    shift_name= shift.shift_name,
                    shift_start= shift.start_time,
                    shift_end=shift.end_time,
                    role_name= shift.role_name,
                    required=required,
                    assigned=assigned,
                    missing=required-assigned
                ))
        return understaffed
    
    def unassigned_only(self):
        assigned_count: dict[int, int] = {}
        for assignment in self.assigned_shifts:
            assigned_count[assignment.shift_id] = assigned_count.get(assignment.shift_id, 0) + 1
        
        unassigned = [shift for shift_id, shift in self.assignable_shifts.items() 
                      if shift_id not in assigned_count]
        return unassigned





