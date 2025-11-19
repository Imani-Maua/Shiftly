from pydantic import BaseModel, ConfigDict
from enum import Enum
from datetime import time

class Role(Enum):
    MANAGER = "manager" 
    LEADER = "leader"
    BARTENDER = "bartender"
    SERVER = "server"
    RUNNER = "runner"
    HOSTESS = "hostess"
    JOB_FORCE = "job force"

    
class Shifts(Enum):
    AM = "am"
    PM = "pm"
    LOUNGE = "lounge"

class TemplateIn(BaseModel):
    period_id: int
    shift_start: time
    shift_end: time
    role: Role

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

class TemplateUpdate(BaseModel):
    period_id: int
    shift_start: time | None = None
    shift_end: time | None = None
    role: Role | None = None

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

class PeriodOut(BaseModel):
    shift_name: Shifts
    start_time: time
    end_time: time

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

class TemplateOut(BaseModel):
    period: PeriodOut
    template: TemplateIn

    model_config = ConfigDict(from_attributes=True)