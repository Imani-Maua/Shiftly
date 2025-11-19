from sqlalchemy.orm import Session
from app.core.utils.crud import CRUDBase
from app.core.shift_period.schema import ShiftPeriodIn,  ShiftPeriodUpdate
from app.database.models import ShiftPeriod
from app.core.shift_period.services.validators import validators, Context, AbstractValidator


class ShiftPeriodService(CRUDBase[ShiftPeriod, ShiftPeriodIn, ShiftPeriodUpdate]):

    def __init__(self):
        super().__init__(ShiftPeriod)

    def create_shift_period(self, db:Session, data: ShiftPeriodIn):
        
        shift_period = db.query(ShiftPeriod).filter(ShiftPeriod.shift_name == data.shift_name).first()
        context = Context.define_context(data=data, period=shift_period)

        for validator in validators:
            validator: AbstractValidator
            validator.validate_shift_period(context)
        created_shift_period = self.create(db=db, obj_in=data)
       
        return ShiftPeriodIn.model_validate(created_shift_period)


