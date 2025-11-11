from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from typing import Annotated, Union, List
from app.core.models.models import Talent
from app.core.services.talent_constraint_service import TalentConstraintService
from app.core.services.constraint_rule_services import ConstraintRuleService
from app.infrastructure.database.database import session
from app.core.schema.talent_constraint_schema import ConstraintCreate
from app.core.schema.talent_constraint_schema import  ConstraintRuleIn
from app.auth.auth_logic.security import required_roles
from app.auth.pydantic.auth_pydantic import UserRole


talent_constraints = APIRouter(tags=["Talent Constraints"])



@talent_constraints.post("/create_constraint")
def create_constraint(db: Annotated[Session, Depends(session)],
                      data: Annotated[ConstraintCreate, Body()],
                      _:str= Depends(required_roles(UserRole.admin, UserRole.manager))):
    constraint = TalentConstraintService().create_constraint(db=db, data=data)
    return constraint

@talent_constraints.post("/create_constraint_rule")
def create_constraint_rule(db: Annotated[Session, Depends(session)],
                      data: Annotated[ConstraintRuleIn, Body()],
                      _:str= Depends(required_roles(UserRole.admin, UserRole.manager))):
    constraint_rule = ConstraintRuleService().create_rules(db=db, data=data)
    return constraint_rule

