from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from typing import Annotated, Union, List
from app.core.talents.services.service import TalentService
from app.core.talents.schema import TalentIn, TalentUpdate, TalentRead
from app.database.session import session
from app.auth.services.security import required_roles
from app.auth.schema import UserRole
from app.database.models import Talent


talents = APIRouter(tags=["Talents"])



@talents.post("/create_talent")
def create_talent(db:Annotated[Session, Depends(session)],
                        data: Annotated[TalentIn,Body()],
                        _: str=Depends(required_roles(UserRole.admin, UserRole.manager))):
    talents = TalentService().create_talent(db=db, data=data)
    return talents
  
@talents.put("/update_talent/{talent_id}")
def update_talent(db: Annotated[Session, Depends(session)],
                        talent_id: int,
                        data: Annotated[TalentUpdate, Body()],
                        _:str= Depends(required_roles(UserRole.admin, UserRole.manager))):
    talent = TalentService().update_talent(db, talent_id, data)
    return talent

@talents.get("/retrieve_talents")
def get_all_talents(db: Annotated[Session, Depends(session)], name: str | None = None, 
                          tal_role: str | None = None,
                          contract_type: str | None = None,
                          is_active: bool | None = None) -> list[TalentRead]:

    talents: list[Talent] = TalentService().get_all(db, name=name, 
                                                    tal_role=tal_role, 
                                                    contract_type=contract_type, 
                                                    is_active=is_active)
    
    return [TalentRead.model_validate(talent) for talent in talents]

@talents.get("/retrieve_talent/{id}", response_model=TalentRead)
def get_a_talent(db: Annotated[Session, Depends(session)], id:int):
    
    talent: Talent = TalentService().get_talent(db, id)
    
    return TalentRead.model_validate(talent)

