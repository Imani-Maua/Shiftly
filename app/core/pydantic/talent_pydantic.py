from pydantic import BaseModel,EmailStr, ConfigDict
from datetime import date


class TalentCreate(BaseModel):
    firstname: str
    lastname: str
    email: EmailStr
    tal_role: str
    contract_type: str
    hours: int | None = None
    start_date: date

#only a superuser should be able to update all these fields. Otherwise, 
# a manager should only be able to update the contract_type, activity
#Otherwise the data can be easily corrupted, but this will be handled later
class TalentUpdate(BaseModel):
    firstname: str | None = None
    lastname: str | None = None
    email: EmailStr | None = None
    tal_role: str | None = None
    contract_type: str | None = None
    is_active: bool | None = None
    hours: int | None = None
    start_date: date | None = None
    end_date: date | None = None

class TalentOut(BaseModel):
    firstname: str
    lastname: str
    tal_role: str
    contract_type: str
    hours: int
    is_active: bool

class TalentRead(BaseModel):
    firstname: str
    lastname: str
    tal_role: str

    model_config = {
        "from_attributes": True
    }
    
    
