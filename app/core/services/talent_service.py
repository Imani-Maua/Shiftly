from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.core.schema.talent_schema import TalentCreate, TalentUpdate
from app.core.utils.crud import CRUDBase
from app.core.models.models import Talent
from datetime import datetime


class TalentService(CRUDBase[Talent, TalentCreate, TalentUpdate]):

    def __init__(self):
        super().__init__(Talent)

    def create_talent(self, db: Session,  data:TalentCreate) -> Talent:
        if data.contract_type not in ("full-time", "part-time", "student"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid contract type")
        contract_hours = {
            "full-time": 40,
            "part-time": 30,
            "student": 24
        }

        data.hours = contract_hours[data.contract_type]
        
        existing = db.query(Talent).filter(Talent.email == data.email).first() #change this to uuid since emails are not unique
        if existing:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Talent with this email already exists")
        talent = self.create(db, data)
        return talent
    
    def update_talent(self, db: Session, talent_id:int, data: TalentUpdate):
        talent = db.query(Talent).filter(Talent.id == talent_id).first()
        if not talent:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Talent not found")
        if data.contract_type and data.contract_type not in ("full-time", "part-time", "student"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid contract type")
        contract_hours = {
            "full-time": 40,
            "part-time": 30,
            "student": 24
        }

        data.hours = contract_hours[data.contract_type]

        if data.is_active == False:
            data.end_date = datetime.now().date()
        
        updated_talent = self.update(db, talent, data)
        return updated_talent
    
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
            
        

        
    