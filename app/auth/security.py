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
from datetime import datetime, timedelta



load_dotenv()

SECRET_KEY = os.getenv("KEY")
algorithm = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_user(db: Annotated[asyncpg.Connection, Depends(get_db)], username: str| None = None, id: int| None = None):
    """
    Retrieve a user from the database by ID or username.

    Args:
        db (asyncpg.Connection): The database connection.
        username (str, optional): The username of the user to fetch.
        id (int, optional): The ID of the user to fetch.

    Returns:
        UserInDB | None: Returns a UserInDB instance if found, otherwise None.

    Raises:
        ValueError: If neither username nor ID is provided.
    """
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
    """
    Authenticate a user by verifying the provided username and password.

    Args:
        db (asyncpg.Connection): The database connection.
        username (str): The username of the user.
        password (str): The plaintext password to verify.

    Returns:
        UserInDB | None: Returns the UserInDB instance if authentication succeeds, otherwise None.
    """
    user: UserInDB = await get_user(db, username)
    if not user or not verify_password(password, user.pwd_hash):
        None
    return user

async def create_access_token(db: Annotated[asyncpg.Connection, Depends(get_db)], data:TokenPayload,type: str, expiry: timedelta | None = None):
    """
    Create a JWT access token and store it in the database.

    Args:
        db (asyncpg.Connection): The database connection.
        data (TokenPayload): The payload to include in the token.
        type (str): The type of token (e.g., "invite", "access").
        expiry (timedelta, optional): Token expiration duration. Defaults to 20 minutes.

    Returns:
        str: The generated JWT token.

    Raises:
        ValueError: If the payload's "sub" field is missing.
    """
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
    """
    Retrieve the currently authenticated user from the JWT token.

    Args:
        token (str): The JWT token provided by the client.
        db (asyncpg.Connection): The database connection.

    Returns:
        UserInDB: The authenticated user.

    Raises:
        HTTPException: If the token is invalid or the user does not exist.
    """
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
    """
    Ensure the current user is active.

    Args:
        current_user (UserInDB): The user retrieved from the token.

    Returns:
        UserInDB: The active user.

    Raises:
        HTTPException: If the user is inactive.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    return current_user  

async def user_in_db(db: Annotated[asyncpg.Connection, Depends(get_db)], id: int = None, username: str = None)-> bool: 
    """
    Check if a user exists in the database.

    Args:
        db (asyncpg.Connection): The database connection.
        id (int, optional): The user's ID.
        username (str, optional): The user's username.

    Returns:
        bool | UserInDB: Returns the UserInDB instance if found, otherwise False.

    Raises:
        ValueError: If neither id nor username is provided.
    """  
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
    """
    Check if a token exists in the database.

    Args:
        db (asyncpg.Connection): The database connection.
        token (str): The token to verify.

    Returns:
        list | bool: Returns the token record if found, otherwise False.
    """
    query = "SELECT token from invites where token = $1"
    repo = await asyncSQLRepo(conn=db, query=query, params=(token,)).getData()
    if repo:
        return repo
    return False

def verify_token(token: str, expectedType: str):
    """
    Verify a JWT token and ensure it matches the expected type.

    Args:
        token (str): The JWT token to verify.
        expectedType (str): The expected type of the token.

    Returns:
        dict: The decoded token payload.

    Raises:
        JWTError: If the token is invalid, expired, or of a wrong type.
    """
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithm)
        if decoded.get("type") != expectedType:
            raise JWTError(f"Invalid Token type: expected: {expectedType}")
        return decoded
    except ExpiredSignatureError:
        raise JWTError("Expired Token")
    except Exception as e:
        raise JWTError("Token verification failed")

def required_roles(*roles):
    """
    Dependency function to enforce user role-based access.

    Args:
        *roles (str): Allowed roles for the endpoint.

    Returns:
        Callable: A dependency function for FastAPI.

    Raises:
        HTTPException: If the current user's role is not allowed.
    """
    def check_role(user: Annotated[UserInDB, Depends(get_current_active_user)]):
        if user.user_role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                                detail="Operation not permitted")
        return user
    return check_role





