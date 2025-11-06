from typing import Generic, TypeVar, Type, Optional, Annotated
from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session



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
        db.add(obj)
        db.commit(obj)
        db.refresh(obj)
        return obj
    
    def update(self, db:Session, db_obj: ModelType, obj_in:UpdateSchemaType) -> Optional[ModelType]:
        for field, value in obj_in.model_dump(exclude_unset=True).items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db:Session, id: int):
        obj = db.query(self.model).get(id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj
        