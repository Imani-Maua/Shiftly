from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from typing import Annotated
from app.core.constraints.talent_constraints.services.services import TalentConstraintService
from app.database.session import session
from app.core.constraints.talent_constraints.schema import ConstraintIn
from app.auth.services.security import required_roles
from app.auth.schema import UserRole


talent_constraints = APIRouter(tags=["Talent Constraints"])



@talent_constraints.post("/create")
def create_constraint(db: Annotated[Session, Depends(session)],
                      data: Annotated[ConstraintIn, Body()],
                      #_:str= Depends(required_roles(UserRole.admin, UserRole.manager))
                      ):
    constraint = TalentConstraintService().create_constraint(db=db, data=data)
    return constraint

@talent_constraints.delete("/delete/{constraint_id}", status_code=204)
def delete_constraint(db: Annotated[Session, Depends(session)],
                              constraint_id: int,
                              #_: str= Depends(required_roles(UserRole.admin, UserRole.manager))
                              ):
    TalentConstraintService().delete_constraint(db=db, constraint_id=constraint_id)

