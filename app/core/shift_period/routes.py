from fastapi import Depends, Body, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from typing import Annotated
from app.database.session import session
from app.core.shift_period.schema import ShiftPeriodIn, ShiftOut, ShiftPeriodUpdate
from app.database.models import ShiftPeriod
from app.auth.services.security import required_roles
from app.auth.schema import UserRole
from app.core.utils.crud import CRUDBase
from app.core.shift_period.services.services import ShiftPeriodService

shift_period = APIRouter(tags=["Shift Period"])


# change the UserRole.enum values
@shift_period.post("/create")
def create_shift_period(db: Annotated[Session, Depends(session)],
                              data: Annotated[ShiftPeriodIn, Body()],
                              _: str = Depends(required_roles(UserRole.superuser))):


    shift_period = ShiftPeriodService().create_shift_period(db=db, data=data)
    return shift_period

  
@shift_period.patch("/update/{period_id}")
def update_shift_period(db: Annotated[Session,  Depends(session)],
                              period_id: int,
                              update_data: Annotated[ShiftPeriodUpdate, Body()],
                              _: str= Depends(required_roles(UserRole.admin, UserRole.manager))
                                ):
    

    updated_shift_period = ShiftPeriodService().update_shift_period(db=db, data=update_data, period_id=period_id)
    return updated_shift_period

@shift_period.delete("/delete/{period_id}", status_code=204)
def delete_shift_period(db: Annotated[Session, Depends(session)],
                              period_id: int,
                              _: str= Depends(required_roles(UserRole.admin, UserRole.manager))
                              ):
    ShiftPeriodService().delete_shift_period(db=db, period_id=period_id)
   