from pydantic import BaseModel, EmailStr



class Talent(BaseModel):
    talent_id: int
    talent_name: str
    tal_role: str
    hours: int
    constraint_type: str | None = None
    constraint_status: bool | None = None
    available_day: str  | None = None
    available_shifts: str  | None = None

