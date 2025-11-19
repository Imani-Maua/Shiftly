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
async def create_shift_period(db: Annotated[Session, Depends(session)],
                              data: Annotated[ShiftPeriodIn, Body()],
                              _: str = Depends(required_roles(UserRole.superuser))):


    shift_period = ShiftPeriodService().create_shift_period(db=db, data=data)
    return shift_period
    
@shift_period.patch("/update/{period_id}")
async def update_shift_period(db: Annotated[Session,  Depends(session)],
                              period_id: int,
                              update_data: Annotated[ShiftPeriodUpdate, Body()],
                              _: str= Depends(required_roles(UserRole.admin, UserRole.manager))
                                ):
    crud_shift = CRUDBase[ShiftPeriod, ShiftPeriodIn, ShiftPeriodUpdate](ShiftPeriod)
    shift_period = db.query(ShiftPeriod).get(period_id)
    if not shift_period:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shift period not found")
    updated_shift = crud_shift.update(db, shift_period, update_data)
    return ShiftOut(
            id=updated_shift.id,
            shift_name=updated_shift.shift_name,
            start_time=updated_shift.start_time,
            end_time=updated_shift.end_time
        )

@shift_period.delete("/delete/{period_id}", status_code=204)
async def delete_shift_period(db: Annotated[Session, Depends(session)],
                              period_id: int,
                              _: str= Depends(required_roles(UserRole.admin, UserRole.manager))):
    crud_shift = CRUDBase[ShiftPeriod, ShiftPeriodIn, ShiftPeriodUpdate](ShiftPeriod)
    shift_period = db.query(ShiftPeriod).get(period_id)
    if not shift_period:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shift period not found")
    
    return crud_shift.delete(db, period_id)