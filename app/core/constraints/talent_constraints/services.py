from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.core.utils.crud import CRUDBase
from app.database.models import TalentConstraint, Talent
from app.core.constraints.talent_constraints.schema import ConstraintCreate, ConstraintUpdate


class TalentConstraintService(CRUDBase[TalentConstraint, ConstraintCreate, ConstraintUpdate]):

    def __init__(self):
        super().__init__(TalentConstraint)
    
    def create_constraint(self, db: Session, data: ConstraintCreate):
       
        talent = db.query(Talent).filter(Talent.id == data.talent_id).first()
        if not talent:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Talent does not exist")
        if not talent.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Talent is inactive")
        exists = db.query(TalentConstraint).filter(TalentConstraint.talent_id == data.talent_id,TalentConstraint.type == data.type.value).first()
        if exists:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Constraint already exists")
        
        data.type = data.type.value
        constraint = self.create(db=db, obj_in=data)
        return constraint

   
    def update_constraint(self,db: Session, constraint_id: int, update_data:ConstraintUpdate):
        constraint = db.query(TalentConstraint).filter(TalentConstraint.id == constraint_id).first()
        if not constraint: 
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Constraint does not exist")
        updated_constraint = self.update(db=db, db_obj=constraint, obj_in=update_data)
        return updated_constraint
        
        
        

    
    