from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from typing import Annotated
from app.auth.services.security import required_roles
from app.auth.schema import UserRole
from app.database.session import session
from app.core.shift_template.schema import TemplateIn
from app.core.shift_template.services.service import TemplateService

shift_templates = APIRouter(tags=["Shift Templates"])

# _:str= Depends(required_roles(UserRole.admin, UserRole.manager))
@shift_templates.post("/create")
def create_constraint_rule(db: Annotated[Session, Depends(session)],
                      data: Annotated[TemplateIn, Body()]):
    shift_template = TemplateService().create_template(db=db, data=data)
    return shift_template
