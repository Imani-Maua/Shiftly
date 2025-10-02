from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError
import asyncpg
from typing import Annotated
from datetime import timedelta, datetime, timezone
from app.auth.security import authenticate_user, user_in_db, verify_token, create_access_token, token_in_db, get_user, required_roles
from app.auth.models import Token, UserInDB, TokenPayload, UserInvite, AcceptInvite, InviteToken, sendRequest, createUser
from app.database.database import get_db, asyncSQLRepo
from app.auth.utils import send_email, hash_password, generate_temporary_password


app = FastAPI()
router = APIRouter()

@app.post("/users/create", response_model=UserInvite)
async def create_user(user: Annotated[createUser, Body()],
                       db: Annotated[asyncpg.Connection, Depends(get_db)],
                       _: str = Depends(required_roles("superuser", "admin"))) -> UserInvite:
    
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
@app.post("/users/invite", response_model=dict)
async def invite_user(user_id:Annotated[sendRequest, Body()], 
                      db: Annotated[asyncpg.Connection, Depends(get_db)],
                      _: str =Depends(required_roles("superuser", "admin"))):
    user: UserInDB = await get_user(db=db, id=user_id.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User does not exist")
    try:        
        payload = TokenPayload(sub=user.username, id=user.id, email=user.email, role=user.user_role, type="invite")
    except:
        raise ValueError("Incorrect data type")
    access_token_expires = timedelta(hours=INVITE_EXPIRY_HOURS)
    invite_token: InviteToken = await create_access_token(db=db, data=payload, expiry=access_token_expires, type=payload.type)
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

@app.post("/invite/accept", response_model=dict)
async def accept_invite(data: Annotated[AcceptInvite, Body ()], db: Annotated[asyncpg.Connection, Depends(get_db)]):
    try:
        verify= verify_token(data.token, "invite")
        payload = TokenPayload(**verify)
        token: InviteToken = await token_in_db(db, data.token)
        print("The expiry date is ", payload.exp)
        if not token:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token. Ask your admin for a new token")
        
        if datetime.now(timezone.utc) > payload.exp:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token. Ask your admin for a new token")

        user_id = payload.id
        user:UserInDB = await user_in_db(db, id=user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        hashed_pass = hash_password(data.new_password)
        user_query = f"UPDATE users SET pwd_hash = $1, is_active = {True} WHERE id= $2"
        activate_user = await asyncSQLRepo(conn=db, query=user_query, params=(hashed_pass, user_id,)).execute()
        token_query = f"UPDATE invites SET used_at = $1 WHERE token = $2"
        set_used_time = await asyncSQLRepo(conn=db, query=token_query, params=(datetime.now(), data.token,)).execute()
        if user:
            user_token = TokenPayload(sub=user.username, id=user.id, email=user.email, role=user.user_role, type="access")
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        access_token = await create_access_token(db=db, data=user_token, type="access")
        
        return {"message": "Password set! You are now logged in!",
                "access_token": access_token}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired invite token")

@app.post("/token", response_model=Token)
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
    access_token = await create_access_token(db=db, data=payload, type=payload.type)
    return Token(access_token=access_token, token_type="bearer", role=user.user_role)
       
@app.get("/invite/accept", response_model=dict)
async def get_invite(token:str, db: Annotated[asyncpg.Connection, Depends(get_db)]):
    try:
        payload = verify_token(token, "invite")
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