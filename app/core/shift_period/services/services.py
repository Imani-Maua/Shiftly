from sqlalchemy.orm import Session
from app.core.utils.crud import CRUDBase
from app.core.shift_period.schema import ShiftPeriodIn,  ShiftPeriodUpdate, ShiftOut
from app.database.models import ShiftPeriod
from app.core.shift_period.services.validators import ShiftPeriodTimeFrame, validate_shift_period, validate_shift_period_update, validate_shift_period_delete



class ShiftPeriodService(CRUDBase[ShiftPeriod, ShiftPeriodIn, ShiftPeriodUpdate]):

    def __init__(self):
        super().__init__(ShiftPeriod)

    def create_shift_period(self, db:Session, data: ShiftPeriodIn):
        
        shift_period = db.query(ShiftPeriod).filter(ShiftPeriod.shift_name == data.shift_name).first()
        ShiftPeriodTimeFrame().validate_shift_period(data=data)
        validate_shift_period(data=data, period=shift_period)
        created_shift_period = self.create(db=db, obj_in=data)
       
        return ShiftOut.model_validate(created_shift_period)

    def update_shift_period(self, db: Session, data: ShiftPeriodUpdate, period_id: int):
        shift_period = db.query(ShiftPeriod).filter(ShiftPeriod.id == period_id).first()
        validate_shift_period_update(data=data, period=shift_period)
        updated_shift = self.update(db=db, db_obj=shift_period, obj_in=data)
        return ShiftOut.model_validate(updated_shift)

    def delete_shift_period(self, db: Session, period_id: int):
        shift_period = db.query(ShiftPeriod).filter(ShiftPeriod.id == period_id).first()
        validate_shift_period_delete(shift_period)
        self.delete(db=db, id=period_id)
        
