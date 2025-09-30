from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
import asyncpg
from typing import Annotated
from datetime import timedelta
from app.auth.security import authenticate_user, get_user, user_in_db
from app.auth.models import Token, UserInDB, TokenPayload, UserInvite
from app.database.database import get_db
from app.auth.onboarding import create_user, generate_invite_token
from app.auth.utils import create_access_token, send_email




app = FastAPI()
router = APIRouter()



@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Annotated[asyncpg.Connection, Depends(get_db)]) -> Token:
    user: UserInDB= await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = TokenPayload(
        sub= user.id,
        email=user.email,
        role = user.user_role
    )
    access_token_expires = timedelta(minutes=20)
    access_token = create_access_token(data=payload, expiry=access_token_expires)
    return Token(access_token=access_token, token_type="bearer", role=user.user_role)


@app.post("/users/invite")
async def invite_user(firstname: str, lastname: str, user_role: str, email: str, db: Annotated[asyncpg.Connection, Depends(get_db)]):
    username = f"{firstname.strip().lower}.{lastname.strip().lower}"
    user =  await user_in_db(db=db, username=username)
    try:
        if user:
            user_data: UserInvite = await create_user(firstname, lastname, user_role, email, db)
    except:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User already exists")

    payload = TokenPayload(sub=user_data.sub, email=email, role=user_role)
    INVITE_EXPIRY_HOURS = 24
    access_token_expires = timedelta(hours=INVITE_EXPIRY_HOURS)
    invite_token = create_access_token(payload, access_token_expires)
    invite_link = f"https://shiftly.app/register?token={invite_token}"
    name = user_data.username.split(".")[0].capitalize()

    subject = "You've been invited to Shiftly!"
    body = f""" 
Hello {name},
You’ve been invited to join Shiftly as a {user_data.role}.

    Temporary password: {user_data.password}
    Registration link (valid {INVITE_EXPIRY_HOURS}h): {invite_link}

    Please login and change your password immediately after first access.
    """

    try:
        send_email(to_email=email, subject=subject, body=body)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to send email: {e}")
    
    return {f"Invite sent to {email}"}

