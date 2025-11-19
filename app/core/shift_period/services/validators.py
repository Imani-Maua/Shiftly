from fastapi import HTTPException, status
from datetime import time
from abc import ABC, abstractmethod
from app.core.shift_period.schema import ShiftPeriodIn, ShiftName
from app.database.models import ShiftPeriod

class AbstractValidator(ABC):

    @abstractmethod
    def validate_shift_period(context):
        raise NotImplementedError


class Context:
    @staticmethod
    def define_context(data: ShiftPeriodIn, period: ShiftPeriod):
        context = {
            "data": data,
            "period": period
        }
        return context

class ShiftPeriodValidator(AbstractValidator):


    def validate_shift_period(context):

        data: ShiftPeriodIn = context["data"]
        period: ShiftPeriod = context["period"]

        if period and period.shift_name == data.shift_name:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                                detail="Shift period already exists")

        if data.start_time > data.end_time:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                                detail="Start time cannot be after end time")
        
        if data.start_time == data.end_time:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                                detail="Start time cannot be the same as end time")


class ShiftPeriodTimeFrame(AbstractValidator):

    SHIFT_TIMEFRAME = {
            ShiftName.AM.value: {"start_time": time(6,0), 
                                  "end_time": time(16,0)},
            ShiftName.PM.value: {"start_time": time(11, 00), 
                                  "end_time": time(23, 59)},
            ShiftName.Lounge.value:{"start_time": time(15,0), 
                                      "end_time": time(23, 59)}
                                      }
    @classmethod
    def expected_timeframe(cls, context: dict) -> dict:
        data: ShiftPeriodIn = context["data"]
        shift_name = data.shift_name
        return cls.SHIFT_TIMEFRAME.get(shift_name)
    
    @classmethod
    def validate_shift_period(cls, context):
        data: ShiftPeriodIn = context["data"]

        shift_name = data.shift_name
        start_time = data.start_time
        end_time = data.end_time

        timeframe: dict = cls.expected_timeframe(context)
        if timeframe is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                                detail=f"Unknown shift type: {shift_name}")
        
        if start_time != timeframe["start_time"] or end_time != timeframe["end_time"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"{shift_name} must be from {timeframe["start_time"]} and {timeframe["end_time"]}")
        
        
        
validators= [ShiftPeriodTimeFrame, ShiftPeriodValidator] 
        
        