from pydantic import BaseModel,EmailStr, ConfigDict
from datetime import date
from app.core.utils.enums import Role, ContractType


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