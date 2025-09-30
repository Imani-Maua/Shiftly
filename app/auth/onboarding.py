from fastapi import Depends
import asyncpg
from typing import Annotated
from datetime import timedelta
from app.auth.models import UserInvite
from app.database.database import get_db
from app.auth.utils import generate_temporary_password, create_access_token, hash_password

INVITE_EXPIRY_HOURS = 24

async def create_user(firstname: str, lastname: str, user_role: str, email: str, db: Annotated[asyncpg.Connection, Depends(get_db)]) -> UserInvite:

    insert_query = "INSERT INTO users (username, firstname, lastname, email, user_role, pwd_hash, is_active) VALUES ($1, $2, $3, $4 ,$5 ,$6, $7) RETURNING id" 
    username = f"{firstname.strip().lower()}.{lastname.strip().lower()}"
    temporary = generate_temporary_password()
    print(temporary)
    hashed = hash_password(temporary)
    row = await db.fetchrow(insert_query, username, firstname, lastname, email, user_role, hashed, False) 
    id = row["id"]
    return UserInvite(sub=id,username=username, email=email, role=user_role, password=temporary)

async def generate_invite_token(user_data: Annotated[UserInvite, Depends(create_user)]):
    expiry = timedelta(hours=INVITE_EXPIRY_HOURS)
    payload = user_data.model_dump(exclude={"password", "username"})
    payload['expiry'] = expiry
    invite_token = create_access_token(payload, expiry=expiry)
    return invite_token
   


