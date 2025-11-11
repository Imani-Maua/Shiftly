from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from itertools import product
from app.core.utils.crud import CRUDBase
from app.core.models.models import TalentConstraint, ConstraintRule
from app.core.schema.talent_constraint_schema import  ConstraintRuleCreate, ConstraintRuleUpdate, ConstraintType, ConstraintRuleIn, ConstraintRuleOut



class ConstraintRuleService(CRUDBase[ConstraintRule, ConstraintRuleIn, ConstraintRuleUpdate]):

    def __init__(self):
        super().__init__(ConstraintRule)

    def create_rules(self, db: Session, data: ConstraintRuleIn):
        constraint= db.query(TalentConstraint).filter(TalentConstraint.id == data.constraint_id).first()

        if not constraint:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Constraint does not exist")
        if constraint.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Constraint already exists")
        
        #validate type-specific rules
        if not data.day and not data.shifts:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Must provide at least one day or shift")
        if constraint.type == ConstraintType.AVAILABILITY.value and data.shifts:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot assign shifts to an availability only constraint. Only days can be specified")
        if constraint.type == ConstraintType.SHIFT_RESTRICTION.value and data.day:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot assign days to an shift-only constraint. Only shifts can be specified")
        if constraint.type == ConstraintType.COMBINATION.value and (not data.day or not data.shifts):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Combination constraints require both days and shifts to be specified.")
        
        days = [day.value for day in (data.day or [])] or [None]
        shifts = [shift.value for shift in (data.shifts or [])] or [None]

        rules_to_create = []
        for in_day, in_shift in product(days, shifts):
            exists = db.query(ConstraintRule).filter_by(constraint_id= data.constraint_id,
                                                                   day = in_day,
                                                                   shifts = in_shift).first()
            if exists:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Rule already exists")
            
            rules_to_create.append(ConstraintRuleCreate(constraint_id=data.constraint_id, day=in_day, shifts=in_shift))
        
        
        created_rules: list[ConstraintRuleCreate] = []
        for rules in rules_to_create:
            created_rule =self.create(db=db, obj_in=rules)
            created_rules.append(created_rule)
        constraint.is_active = True
        
        result = [
        ConstraintRuleOut.model_validate({
            "id": rule.id,
            "constraint_id": constraint.id,
            "day": rule.day,
            "shifts": rule.shifts,
            "talent_id": constraint.talent_id,
            "type": constraint.type,
            "is_active": constraint.is_active
        })
        for rule in created_rules
    ]

        return result
        