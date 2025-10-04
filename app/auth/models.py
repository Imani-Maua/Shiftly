from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class createUser(BaseModel):
    firstname:str
    lastname: str
    user_role: str
    email: EmailStr

class AcceptInvite(BaseModel):
    token: str
    new_password: str

class InviteToken(BaseModel):
    id: int
    user_id: int
    token: str
    jti: str
    type: str
    expires_at: datetime | None
    created_at: datetime | None
    used_at: datetime | None

class AccessToken(BaseModel):
    id: int
    user_id: int
    token: str
    jti: str
    type: str
    expires_at: datetime | None
    created_at: datetime | None
    used_at: datetime | None

class sendRequest(BaseModel):
    user_id: int

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

class TokenPayload(BaseModel):
    sub: str
    id: int
    email: EmailStr
    role: Optional[str] = None
    type: str
    exp: Optional[datetime] = None


