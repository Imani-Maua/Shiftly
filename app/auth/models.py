from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class CreateUser(BaseModel):
    firstname:str
    lastname: str
    role: str
    email: EmailStr
    password: str
    is_active: bool = False


class TokenPayload(BaseModel):
    sub: int
    email: EmailStr
    role: Optional[str] = None
    exp: Optional[datetime] = None

class UserInvite(BaseModel):
    sub: int
    username: str
    email: EmailStr
    role: str
    password: str

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserLogin(BaseModel):
    username: str
    password: str

class UserInDB(BaseModel):
    id: int
    username: str
    email: EmailStr
    firstname: str
    lastname: str
    user_role: str
    pwd_hash: str
    is_active: bool
    #permissions: list[str] | None = None
    #created_by: str
    #created_at: datetime | None = None
    #last_login: datetime | None = None

class UserCreate(UserBase):
    password: str
    role: str

class UserOut(UserBase):
    role: str
    
class Token(BaseModel):
    access_token: str
    token_type: str
    role: str

class TokenData(BaseModel):
    username: str | None=None

