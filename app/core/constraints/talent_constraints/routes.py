from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from typing import Annotated
from app.core.constraints.talent_constraints.services import TalentConstraintService
from app.database.session import session
from app.core.constraints.talent_constraints.schema import ConstraintCreate
from app.auth.services.security import required_roles
from app.auth.schema import UserRole


talent_constraints = APIRouter(tags=["Talent Constraints"])



@talent_constraints.post("/create_constraint")
def create_constraint(db: Annotated[Session, Depends(session)],
                      data: Annotated[ConstraintCreate, Body()],
                      _:str= Depends(required_roles(UserRole.admin, UserRole.manager))):
    constraint = TalentConstraintService().create_constraint(db=db, data=data)
    return constraint



