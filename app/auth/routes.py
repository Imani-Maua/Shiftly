from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, JWTError
import os
import asyncpg
from typing import Annotated
from datetime import timedelta, datetime, timezone
from app.auth.security import authenticate_user, user_in_db, verify_token_type, create_jwt, token_in_db, get_user, required_roles, store_token
from app.auth.models import Token, UserInDB, TokenPayload, UserInvite, AcceptInvite, InviteToken, sendRequest, createUser, UserRole
from app.infrastructure.database.database import get_db, asyncSQLRepo
from app.auth.utils import send_email, hash_password, generate_temporary_password



auth_router = APIRouter()

SECRET_KEY = os.getenv("KEY")
algorithm = "HS256"


@auth_router.post("/create", response_model=UserInvite)
async def create_user(user: Annotated[createUser, Body()],
                       db: Annotated[asyncpg.Connection, Depends(get_db)],
                        _: str = Depends(required_roles(UserRole.superuser, UserRole.admin))) -> UserInvite:
     
    username = f"{user.firstname.strip().lower()}.{user.lastname.strip().lower()}"
    user_exists = await user_in_db(db, username=username)
    if user_exists:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User already exists")
    insert_query = "INSERT INTO users (username, firstname, lastname, email, user_role, pwd_hash, is_active) VALUES ($1, $2, $3, $4 ,$5 ,$6, $7) RETURNING id" 
    temporary = generate_temporary_password()
    hashed = hash_password(temporary)
    row = await db.fetchrow(insert_query, username, user.firstname, user.lastname, user.email, user.user_role, hashed, False) 
    id = row["id"]
    return UserInvite(sub=id,username=username, email=user.email, role=user.user_role, password=temporary) 


INVITE_EXPIRY_HOURS = 24
@auth_router.post("/send_invite", response_model=dict)
async def invite_user(user_id:Annotated[sendRequest, Body()], 
                      db: Annotated[asyncpg.Connection, Depends(get_db)],
                      _: str = Depends(required_roles(UserRole.superuser, UserRole.admin))):
    user: UserInDB = await get_user(db=db, id=user_id.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User does not exist")
    try:        
        payload = TokenPayload(sub=user.username, id=user.id, email=user.email, role=user.user_role, type="invite")
    except:
        raise ValueError("Incorrect data type")
    invite_token_expires = timedelta(hours=INVITE_EXPIRY_HOURS)
    invite_token: InviteToken = create_jwt(data=payload, expiry=invite_token_expires)
    stored_invite = await store_token(data=payload, jwt=invite_token, db=db)

    invite_link = f"https://shiftly.app/register?token={invite_token}"
    name = user.username.split(".")[0].capitalize()

    subject = "You've been invited to Shiftly!"
    body = f""" 
Hello {name},
You’ve been invited to join Shiftly as a {user.user_role}.

    Registration link (valid {INVITE_EXPIRY_HOURS} h): {invite_link}

    Please login and change your password immediately after first access.
    """

    try:
        send_email(to_email=user.email, subject=subject, body=body)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to send email: {e}")
    
    return {"message": f"Invite sent to {user.email}"}

@auth_router.post("/accept_invite", response_model=dict)
async def accept_invite(data: Annotated[AcceptInvite, Body ()], 
                        db: Annotated[asyncpg.Connection, Depends(get_db)]):
    try:
        verify_type= verify_token_type(data.token, "invite")
        payload = TokenPayload(**verify_type)
        token: InviteToken = await token_in_db(db, data.token) 
        if not token:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token missing.")
        
        if datetime.now(timezone.utc) > payload.exp: #using timezone.utc does not cause issues check why since when sending the invite, it does
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Expired token. Ask your admin for a new token")

        user_id = payload.id
        user:UserInDB = await user_in_db(db, id=user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        hashed_pass = hash_password(data.new_password)
        user_query = f"UPDATE users SET pwd_hash = $1, is_active = {True} WHERE id= $2"
        payload = jwt.decode(data.token,SECRET_KEY, algorithms=algorithm)
        jti = payload.get('jti')
        activate_user = await asyncSQLRepo(conn=db, query=user_query, params=(hashed_pass, user_id,)).execute()
        token_query = f"UPDATE invite_token SET used_at = $1 WHERE jti = $2"
        set_used_time = await asyncSQLRepo(conn=db, query=token_query, params=(datetime.now(), jti,)).execute()
        return {"message": "Account activated successfully! Click here to login"}
        
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired invite token")

ACCESS_EXPIRY_DAYS = 4
@auth_router.post("/login_token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                  db: Annotated[asyncpg.Connection, Depends(get_db)]) -> Token:
    user: UserInDB= await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="User account is not active"
        )
    payload = TokenPayload(
        sub= user.username,
        id=user.id,
        email=user.email,
        role = user.user_role,
        type = "access"
    )
    access_token_expires = timedelta(days=ACCESS_EXPIRY_DAYS)
    access_token = create_jwt(data=payload, expiry=access_token_expires)
    store_access_token = await store_token(payload, access_token, db)
    return Token(access_token=access_token, token_type="bearer", role=user.user_role)
       
@auth_router.get("/accept_invite", response_model=dict)
async def get_invite(token:str, db: Annotated[asyncpg.Connection, Depends(get_db)]):
    try:
        payload = verify_token_type(token, "invite")
        user_id = payload.get("id")
        token = await token_in_db(db, token)
        if not token:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invite does not exist")
        user: UserInDB = await user_in_db(db,id=user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return {"email": user.email}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired invite token")


