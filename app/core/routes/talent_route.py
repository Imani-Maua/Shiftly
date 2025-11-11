from fastapi import APIRouter, Depends, Body, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated, Union, List
from app.core.utils.models import Talent
from app.core.services.talent_service import TalentService
from app.core.pydantic.talent_pydantic import TalentCreate, TalentUpdate, TalentOut, TalentRead
from app.infrastructure.database.database import session
from app.auth.auth_logic.security import required_roles
from app.auth.pydantic.auth_pydantic import UserRole


talents = APIRouter()

@talents.post("/create_talent")
async def create_talent(db:Annotated[Session, Depends(session)],
                        data: Annotated[Union[TalentCreate, List[TalentCreate]],Body()],
                        _:str= Depends(required_roles(UserRole.admin, UserRole.manager))):
    service = TalentService()

    if isinstance(data, TalentCreate):
        return await service.create_talent(db, data)
    
    created_talents = []
    for talent in data:
        created_talent = await service.create_talent(db, talent)
        created_talents.append(created_talent)
    
    return created_talents

@talents.put("/update_talent/{talent_id}")
async def update_talent(db: Annotated[Session, Depends(session)],
                        talent_id: int,
                        data: Annotated[TalentUpdate, Body()],
                        _: str=Depends(required_roles(UserRole.admin, UserRole.manager))):
    talent = await TalentService().update_talent(db, talent_id, data)
    return talent

@talents.get("/retrieve_talents")
async def get_all_talents(db: Annotated[Session, Depends(session)], name: str | None = None, 
                          tal_role: str | None = None,
                          contract_type: str | None = None,
                          is_active: bool | None = None) -> list[TalentRead]:
    talents: list[Talent] = TalentService().get_all(db, name=name, tal_role=tal_role, contract_type=contract_type, is_active=is_active)
    
    return [TalentRead.model_validate(talent) for talent in talents]

@talents.get("/retrieve_talent/{id}", response_model=TalentRead)
def get_a_talent(db: Annotated[Session, Depends(session)], id:int):
    talent: Talent = TalentService().get_talent(db, id)
    
    return TalentRead.model_validate(talent)

