from pydantic import BaseModel, ConfigDict
from datetime import time
from app.core.utils.enums import TemplateRole, Shifts



class TemplateIn(BaseModel):
    period_id: int
    shift_start: time
    shift_end: time
    role: TemplateRole

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

class TemplateUpdate(BaseModel):
    shift_start: time | None = None
    shift_end: time | None = None

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

class PeriodOut(BaseModel):
    shift_name: Shifts
    start_time: time
    end_time: time

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

class TemplateOut(BaseModel):
    period: PeriodOut
    template: TemplateIn

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)