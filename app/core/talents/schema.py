from pydantic import BaseModel,EmailStr, ConfigDict
from datetime import date
from enum import Enum



class Role(Enum):
    MANAGER = "manager" 
    ASSISTANT_MANAGER = "assistant manager"
    SUPERVISOR = "supervisor"
    BARTENDER = "bartender"
    SERVER = "server"
    RUNNER = "runner"
    HOSTESS = "hostess"
    JOB_FORCE = "job force"


class ContractType(Enum):
    FULL_TIME = "full-time"
    PART_TIME = "part-time"
    STUDENT = "student"


class TalentIn(BaseModel):
    firstname: str
    lastname: str
    email: EmailStr
    tal_role: Role
    contract_type: ContractType
    start_date: date

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

#only a superuser should be able to update all these fields. 

class TalentUpdate(BaseModel):
    firstname: str | None = None
    lastname: str | None = None
    email: EmailStr | None = None
    tal_role: Role | None = None
    contract_type: ContractType | None = None
    is_active: bool | None = None

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

class TalentOut(BaseModel):
    firstname: str
    lastname: str
    tal_role: str
    contract_type: str
    hours: int
    is_active: bool
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

class TalentRead(BaseModel):
    firstname: str
    lastname: str
    tal_role: str

    model_config = ConfigDict(from_attributes=True)