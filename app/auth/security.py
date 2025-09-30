from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
import asyncpg
import hashlib
import os
from passlib.context import CryptContext
from jose import jwt, JWTError
from dotenv import load_dotenv
from typing import Annotated
from datetime import datetime, timedelta, timezone
from app.auth.models import UserInDB, TokenData, TokenPayload
from app.database.database import get_db, asyncSQLRepo
from app.auth.utils import verify_password



load_dotenv()

SECRET_KEY = os.getenv("KEY")
algorithm = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_user(db: Annotated[asyncpg.Connection, Depends(get_db)], username: str):
    query = "SELECT * from users where username = $1"
    repo = asyncSQLRepo(conn=db, query=query, params=(username,))
    result = await repo.getData()
    if result:
        return UserInDB(**dict(result[0]))
    return None
    
async def authenticate_user(db: Annotated[asyncpg.Connection, Depends(get_db)], username:str, password: str):
    user: UserInDB = await get_user(db, username)
    if not user or not verify_password(password, user.pwd_hash):
        return None
    return user

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: asyncpg.Connection = Depends(get_db)) -> UserInDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[algorithm])
        username = payload.get("sub")  
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await get_user(db, username=token_data.username)   
    if user is None:
        raise credentials_exception
    return user  

async def get_current_active_user(current_user: Annotated[UserInDB, Depends(get_current_user)]): 
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    return current_user  

async def user_in_db(db: Annotated[asyncpg.Connection, Depends(get_db)], username: str):   
    query = "SELECT * FROM users where username = $1"
    repo= asyncSQLRepo(conn=db, query=query, params=(username))
    result = repo.getData()
    if result:
        return True
    return False










