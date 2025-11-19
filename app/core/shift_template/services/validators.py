from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from abc import ABC, abstractmethod
from app.core.shift_template.schema import TemplateIn, Role
from app.database.models import ShiftTemplate, ShiftPeriod



class AbstractValidator(ABC):

    @abstractmethod
    def validate_shift_template(context: dict):
        raise NotImplementedError
    

class Context:

    @staticmethod
    def context_finder(*, db:Session, data:TemplateIn, period: ShiftPeriod) -> dict:

        context = {
            "db": db,
            "data": data,
            "period": period
        }

        return context

class ShiftTemplateValidator(AbstractValidator):

    def validate_shift_template(context):

        data: TemplateIn = context["data"]
        period: ShiftPeriod = context["period"]

        
        if data.shift_start == data.shift_end:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                                detail="Start time cannot be the same as end time")
        if data.shift_start < period.start_time or data.shift_start > period.end_time:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Please select a template start time that falls within the shift period.")
        if data.shift_end > period.end_time or data.shift_end < period.start_time:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Please select a template end time that falls within the shift period.")
        
        if data.shift_start > data.shift_end:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                                detail="Start time cannot be after end time")
        


validators = [ShiftTemplateValidator]

    
