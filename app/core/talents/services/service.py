from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Union, List
from app.core.talents.schema import TalentIn, TalentUpdate, TalentOut
from app.core.utils.crud import CRUDBase
from app.database.models import Talent
from app.core.talents.services.validator import input_validators,update_validators, AbstractValidator
from app.core.talents.utils import set_contract_hours, context_finder


class TalentService(CRUDBase[Talent, TalentIn, TalentUpdate]):

    def __init__(self):
        super().__init__(Talent)

    def create_talent(self, db: Session,  data:TalentIn) -> Talent:
        talent = db.query(Talent).filter(Talent.email == data.email).first()
        context = context_finder(db=db, data=data, talent=talent)
        for validator in input_validators:
            validator: AbstractValidator
            validator.validate_talent(context)
        contract_hours = set_contract_hours(data.contract_type)
        
        created_talents: Talent = self.create(db=db, obj_in=data)
        created_talents.hours = contract_hours

        db.add(created_talents)
        db.commit()
        db.refresh(created_talents)

        return TalentOut.model_validate(created_talents)

    
    def update_talent(self, db: Session, talent_id:int, data: TalentUpdate):
        talent = db.query(Talent).filter(Talent.id == talent_id).first()
        context = context_finder(db=db, data=data, talent=talent)
        for validator in update_validators:
            validator: AbstractValidator
            validator.validate_talent(context)
        updated_talent = self.update(db, talent, data)

        return TalentOut.model_validate(updated_talent)
    
    def get_all_talents(self, db: Session,
                              name: str | None = None,
                              tal_role: str | None = None,
                              contract_type: str | None = None,
                              is_active: bool | None = None):
        query = db.query(Talent)
        if not query:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Talent not found")
        if tal_role:
            talents = query.filter(Talent.tal_role == tal_role)
        
        if contract_type:
            talents = query.filter(Talent.contract_type == contract_type)
        
        if is_active is not None:
            talents = query.filter(Talent.is_active == is_active)
        
        if name:
            name_pattern = f"%{name.lower()}%"
            talents = query.filter(
                or_(Talent.firstname.ilike(name_pattern),
                    Talent.lastname.ilike(name_pattern),
                    (Talent.firstname + " " + Talent.lastname).ilike(name_pattern))
            )
        
        return talents.all()
    
    def get_talent(self, db: Session, id: int):
        talent = db.query(Talent).filter(Talent.id == id).first()
        if not talent:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Talent not found")
        return talent
            
        

        
    