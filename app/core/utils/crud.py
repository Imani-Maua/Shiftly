from typing import Generic, TypeVar, Type, Optional, Union
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.exc import DatabaseError as AlchemyDatabaseError
import asyncpg
from app.core.utils.exceptions import DatabaseError



ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


#later add logs to log operations

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model
    

    def get(self, db:Union[Session, asyncpg.Connection], id: int)-> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id).first()
    

    def get_all(self, db:Union[Session, asyncpg.Connection], **filters) -> list[ModelType]:
       query = db.query(self.model)
       for field, value in filters.items():
           if value is not None and hasattr(self.model, field):
               query = query.filter(getattr(self.model, field) == value)
        
       return query.all()
    
    def batch_create(self, db: Union[Session, asyncpg.Connection], objs_in: Optional[CreateSchemaType]):
        objs = [self.model(**obj.model_dump()) for obj in objs_in]
        try:
            db.add_all(objs)
            db.commit()
            for obj in objs:
                db.refresh(obj)
            return objs
        except AlchemyDatabaseError:
            db.rollback()
            raise DatabaseError("A database error has occurred during generation. Please try again")

    def create(self, db:Union[Session, asyncpg.Connection], obj_in: Optional[CreateSchemaType]) -> Optional[ModelType]:
        obj = self.model(**obj_in.model_dump())
        try:
            db.add(obj)
            db.commit()
            db.refresh(obj)
            return obj
        except AlchemyDatabaseError as e:
            db.rollback()
            raise DatabaseError("A database error has occurred during generation. Please try again")
    
    def update(self, db:Union[Session, asyncpg.Connection], db_obj: ModelType, obj_in:UpdateSchemaType) -> Optional[ModelType]:
        try:
            update_data = obj_in.model_dump(exclude_unset=True)
            update_data = {key:value for key, value in update_data.items() if value is not None}
            for field, value in update_data.items():
                setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except AlchemyDatabaseError as e:
            db.rollback()
            raise DatabaseError("A database error has occurred during generation. Please try again")
            

    
    def delete(self, db:Union[Session, asyncpg.Connection], id: int):
        try:
            obj = db.query(self.model).get(id)
            if obj:
                db.delete(obj)
                db.commit()
            return obj
        except AlchemyDatabaseError as e:
            db.rollback()
            raise RuntimeError("A database error has occurred during generation. Please try again")
        