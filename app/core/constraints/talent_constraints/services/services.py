from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.core.utils.crud import CRUDBase
from app.database.models import TalentConstraint, Talent
from app.core.constraints.talent_constraints.schema import ConstraintIn, ConstraintUpdate, ConstraintOut
from app.core.constraints.talent_constraints.services.validators import validate_constraint_input, validate_constraint_delete


class TalentConstraintService(CRUDBase[TalentConstraint, ConstraintIn, ConstraintUpdate]):

    def __init__(self):
        super().__init__(TalentConstraint)
    
    def create_constraint(self, db: Session, data: ConstraintIn):
       
        talent = db.query(Talent).filter(Talent.id == data.talent_id).first()
        constraint = db.query(TalentConstraint).filter(TalentConstraint.talent_id == data.talent_id,TalentConstraint.type == data.type).first()
        validate_constraint_input(talent=talent, constraint=constraint)
        created_constraint: TalentConstraint = self.create(db=db, obj_in=data)
        return ConstraintOut.model_validate(created_constraint)

   
    def delete_constraint(self, db: Session, constraint_id: int):
        constraint = db.query(TalentConstraint).filter(TalentConstraint.id == constraint_id).first()
        validate_constraint_delete(constraint)
        self.delete(db=db, id=constraint_id)
        
        
        

    
    