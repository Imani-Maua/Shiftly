from sqlalchemy.orm import Session
from app.core.utils.crud import CRUDBase
from app.database.models import ShiftPeriod, ShiftTemplate
from app.core.shift_template.schema import TemplateIn, TemplateOut, TemplateUpdate
from app.core.shift_template.services.validators import validate_shift_template, validate_shift_template_update, validate_template_delete


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
        validate_shift_template(data=data, period=shift_period)
        created_templates = self.create(db=db, obj_in=data)
        return TemplateOut.model_validate(created_templates)
    
    def update_template(self, db: Session, data: TemplateUpdate, template_id: int):
        template = db.query(ShiftTemplate).filter(ShiftTemplate.id == template_id).first()
        validate_shift_template_update(data=data, template=template)
        updated_template = self.update(db=db, db_obj=template, obj_in=data)
        return TemplateOut.model_validate(updated_template)
    
    def delete_template(self, db: Session, template_id: int):
        template = db.query(ShiftTemplate).filter(ShiftTemplate.id == template_id).first()
        validate_template_delete(template)
        self.delete(db=db, id=template_id)


