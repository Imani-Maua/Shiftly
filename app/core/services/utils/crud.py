from fastapi import HTTPException, status
from typing import Generic, TypeVar, Type, Optional, Annotated
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError



ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model
    

    def get(self, db:Session, id: int)-> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id).first()
    

    def get_all(self, db:Session):
        return db.query(self.model).all()
    
    def create(self, db:Session, obj_in: CreateSchemaType) -> Optional[ModelType]:
        obj = self.model(**obj_in.model_dump())
        try:
            db.add(obj)
            db.commit()
            db.refresh(obj)
            return obj
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database error while creating model:{str(e)}")
            
    
    def update(self, db:Session, db_obj: ModelType, obj_in:UpdateSchemaType) -> Optional[ModelType]:
        try:
            for field, value in obj_in.model_dump(exclude_unset=True).items():
                setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database error while updating model:{str(e)}")
            

    
    def delete(self, db:Session, id: int):
        try:
            obj = db.query(self.model).get(id)
            if obj:
                db.delete(obj)
                db.commit()
            return obj
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database error while deleting model:{str(e)}")
            
        