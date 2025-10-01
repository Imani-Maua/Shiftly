from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
import asyncpg
import os
import uuid
from jose import jwt, JWTError, ExpiredSignatureError
from dotenv import load_dotenv
from typing import Annotated
from app.auth.models import UserInDB, TokenData, TokenPayload
from app.database.database import get_db, asyncSQLRepo
from app.auth.utils import verify_password
from datetime import datetime, timedelta, timezone



load_dotenv()

SECRET_KEY = os.getenv("KEY")
algorithm = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_user(db: Annotated[asyncpg.Connection, Depends(get_db)], username: str| None = None, id: int| None = None):
    id_query = "SELECT * FROM users where id = $1"
    user_query = "SELECT * FROM users where username = $1"
    if id is not None:
        repo= await asyncSQLRepo(conn=db, query=id_query, params=(id,)).getData()
    elif username is not None:
        repo= await asyncSQLRepo(conn=db, query=user_query, params=(username,)).getData()
    else:
        raise ValueError("Must provide id or username")
    if repo:
        return UserInDB(**dict(repo[0]))
    return None
    
async def authenticate_user(db: Annotated[asyncpg.Connection, Depends(get_db)], username:str, password: str):
    user: UserInDB = await get_user(db, username)
    if not user or not verify_password(password, user.pwd_hash):
        None
    return user

async def create_access_token(db: Annotated[asyncpg.Connection, Depends(get_db)], data:TokenPayload,type: str, expiry: timedelta | None = None):
    now = datetime.now() #check why I cannot use an aware datetime object here
    expire = now + (expiry if expiry else timedelta(minutes=20))
    data.exp = expire
    if not data.sub:
        raise ValueError("Missing sub field in token data")
    token = jwt.encode(data.model_dump(), SECRET_KEY, algorithm=algorithm)
    jti = str(uuid.uuid4())
    token_query = "INSERT INTO invites (user_id, token, jti, type, expires_at, created_at) VALUES($1 ,$2 ,$3 ,$4 ,$5 ,$6)"
    insert_token = await asyncSQLRepo(conn=db, query=token_query, params=(data.id, token, jti, type, expire, now)).execute()
    return token
    
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

async def user_in_db(db: Annotated[asyncpg.Connection, Depends(get_db)], id: int = None, username: str = None)-> bool:   
    id_query = "SELECT * FROM users where id = $1"
    user_query = "SELECT * FROM users where username = $1"
    if id is not None:
        repo= await asyncSQLRepo(conn=db, query=id_query, params=(id,)).getData()
    elif username is not None:
        repo= await asyncSQLRepo(conn=db, query=user_query, params=(username,)).getData()
    else:
        raise ValueError("Must provide id or username")
    if repo:
        return UserInDB(**repo[0])
    return False 

async def token_in_db(db: Annotated[asyncpg.Connection, Depends(get_db)], token):
    query = "SELECT token from invites where token = $1"
    repo = await asyncSQLRepo(conn=db, query=query, params=(token,)).getData()
    if repo:
        return repo
    return False


def verify_token(token: str, expectedType: str):
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithm)
        if decoded.get("type") != expectedType:
            raise JWTError(f"Invalid Token type: expected: {expectedType}")
        return decoded
    except ExpiredSignatureError:
        raise JWTError("Expired Token")
    except Exception as e:
        raise JWTError("Token verification failed")








