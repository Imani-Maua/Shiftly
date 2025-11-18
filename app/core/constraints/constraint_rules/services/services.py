from fastapi import HTTPException, status
from sqlalchemy import and_
from sqlalchemy.orm import Session
from itertools import product
from app.core.utils.crud import CRUDBase
from app.database.models import ConstraintRule, TalentConstraint
from app.core.constraints.constraint_rules.schema import  ConstraintRuleCreate, ConstraintRuleUpdate, ConstraintRuleIn, ConstraintRuleOut, ConstraintType
from app.core.constraints.constraint_rules.utils import generate_rule_combinations
from app.core.constraints.constraint_rules.services.validators import validators, Context, AbstractValidator


class RulesConfiguration():
     
     @staticmethod
     def rules_configuration(constraint: TalentConstraint) -> dict:

        CONSTRAINT_VALIDATION_RULES = {
        ConstraintType.AVAILABILITY.value: {"allow_day": True, "allow_shift": False},
        ConstraintType.SHIFT_RESTRICTION.value: {"allow_day": False, "allow_shift": True},
        ConstraintType.COMBINATION.value: {"allow_day": True, "allow_shift": True, "require_both": True}
    }
        
        if not constraint:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Constraint does not exist")
        
        if constraint.is_active:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
                                detail="Constraint already exists. Click here to update")

        rules_config = CONSTRAINT_VALIDATION_RULES.get(constraint.type)



        if not rules_config:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                                detail=f"Unknown constraint type: {constraint.type}")

        return rules_config  


class ConstraintRuleService(CRUDBase[ConstraintRule, ConstraintRuleIn, ConstraintRuleUpdate]):

    def __init__(self):
        super().__init__(ConstraintRule)
       
    
    def create_rules(self, db: Session, data:ConstraintRuleIn):
        constraint = db.query(TalentConstraint).filter(
            TalentConstraint.id == data.constraint_id).first()
        
        rules_config = RulesConfiguration.rules_configuration(constraint=constraint)
        
        ctx = Context.contextFinder(
            db=db, data=data, rules_config=rules_config, constraint=constraint)

        for validator in validators:
            validator: AbstractValidator
            validator.pass_validation(ctx)
        
        rules_to_process: list[ConstraintRuleCreate] = generate_rule_combinations(data)

        constraint.is_active = True
        

        created_rules: list[ConstraintRule] = self.batch_create(db=db, objs_in=rules_to_process)
        
        
        return [ConstraintRuleOut.model_validate(rule) for rule in created_rules]

        