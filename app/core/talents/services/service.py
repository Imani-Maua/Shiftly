from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Union, List
from app.core.talents.schema import TalentIn, TalentUpdate, TalentOut
from app.core.utils.crud import CRUDBase
from app.database.models import Talent
from app.core.talents.services.validator import validate_talent_create, validate_talent_update
from app.core.talents.utils import set_contract_hours


class TalentService(CRUDBase[Talent, TalentIn, TalentUpdate]):

    def __init__(self):
        super().__init__(Talent)

    def create_talent(self, db: Session,  data:TalentIn) -> TalentOut:

        talent = db.query(Talent).filter(Talent.email == data.email).first()
        validate_talent_create(data=data, talent=talent)

        contract_hours = set_contract_hours(data.contract_type)
        
        created_talents: Talent = self.create(db=db, obj_in=data)
        created_talents.hours = contract_hours

        db.add(created_talents)
        db.commit()
        db.refresh(created_talents)

        return TalentOut.model_validate(created_talents)

    
    def update_talent(self, db: Session, talent_id:int, data: TalentUpdate):

        talent = db.query(Talent).filter(Talent.id == talent_id).first()
        validate_talent_update(data=data, talent=talent)

        if data.is_active is False:
            talent.end_date = datetime.now().date()
        if data.contract_type:
            talent.hours = set_contract_hours(data.contract_type)
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
            query = query.filter(Talent.tal_role == tal_role)
        
        if contract_type:
            query = query.filter(Talent.contract_type == contract_type)
        
        if is_active is not None:
            query = query.filter(Talent.is_active == is_active)
        
        if name:
            name_pattern = f"%{name.lower()}%"
            query = query.filter(
                or_(Talent.firstname.ilike(name_pattern),
                    Talent.lastname.ilike(name_pattern),
                    (Talent.firstname + " " + Talent.lastname).ilike(name_pattern))
            )
        
        return query.all()
    
    def get_talent(self, db: Session, id: int):
        talent = db.query(Talent).filter(Talent.id == id).first()
        if not talent:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Talent not found")
        return talent
            
        

        
    