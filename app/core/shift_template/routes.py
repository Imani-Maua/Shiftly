from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from typing import Annotated
from app.auth.services.security import required_roles
from app.auth.schema import UserRole
from app.database.session import session
from app.core.shift_template.schema import TemplateIn, TemplateUpdate
from app.core.shift_template.services.service import TemplateService

shift_templates = APIRouter(tags=["Shift Templates"])


@shift_templates.post("/create")
def create_template(db: Annotated[Session, Depends(session)],
                      data: Annotated[TemplateIn, Body()],
                      _:str= Depends(required_roles(UserRole.admin, UserRole.manager))
                      ):
    shift_template = TemplateService().create_template(db=db, data=data)
    return shift_template

@shift_templates.put("/update/{template_id}")
def update_template(db: Annotated[Session,  Depends(session)],
                              template_id: int,
                              update_data: Annotated[TemplateUpdate, Body()],
                             _: str= Depends(required_roles(UserRole.admin, UserRole.manager))
                                ):
    updated_template = TemplateService().update_template(db=db, data=update_data, template_id=template_id)
    return updated_template

@shift_templates.delete("/delete/{template_id}", status_code=204)
def delete_template(db: Annotated[Session, Depends(session)],
                              template_id: int,
                             _: str= Depends(required_roles(UserRole.admin, UserRole.manager))
                              ):
    TemplateService().delete_template(db=db, template_id=template_id)
