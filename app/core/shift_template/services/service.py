from sqlalchemy.orm import Session
from app.core.utils.crud import CRUDBase
from app.database.models import ShiftPeriod, ShiftTemplate
from app.core.shift_template.schema import TemplateIn, TemplateOut, TemplateUpdate
from app.core.shift_template.services.validators import validators, Context, AbstractValidator
from app.core.shift_template.utils import staffing_configuration, set_staffing_needs

#one of the issues with creating shift templates is that we want to allow the user
#to define as many templates as they need within a shift period. The problem that arises with this
#is that there is risk of duplication. That stands as one of the problems with this code as for now.
#There is no way to know if a user creates duplicate templates since even overlapping ones are allowed.
#Introduce fixes in .v2

class TemplateService(CRUDBase[ShiftTemplate, TemplateIn, TemplateUpdate]):

    def __init__(self):
        super().__init__(ShiftTemplate)
    

    def create_template(self, db: Session, data: TemplateIn):
        shift_period = db.query(ShiftPeriod).filter(ShiftPeriod.id == data.period_id).first()
        ctx = Context.context_finder(db=db, data=data,period=shift_period)
        for validator in validators:
            validator: AbstractValidator
            validator.validate_shift_template(ctx)
        created_templates = self.create(db=db, obj_in=data)
        return TemplateIn.model_validate(created_templates)

