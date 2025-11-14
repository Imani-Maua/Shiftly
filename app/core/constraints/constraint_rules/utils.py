from itertools import product
from app.core.constraints.constraint_rules.schema import  ConstraintRuleIn, ConstraintRuleCreate




def generate_rule_combinations(data: ConstraintRuleIn) -> list[ConstraintRuleCreate]:
        days = [day.value for day in (data.day or [])] or [None]
        shifts = [shift.value for shift in (data.shifts or [])] or [None]

        rules = []

        for day, shift in product(days, shifts):
            rules.append(ConstraintRuleCreate(
                constraint_id = data.constraint_id,
                day = day,
                shifts = shift
            ))
        
        return rules

