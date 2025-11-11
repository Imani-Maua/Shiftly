from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, JWTError
import os
import asyncpg
from typing import Annotated
from datetime import timedelta, datetime, timezone
from app.auth.auth_logic.security import authenticate_user, user_in_db, verify_token_type, create_jwt, token_in_db, get_user, required_roles, store_token
from app.auth.pydantic.auth_pydantic import Token, UserInDB, TokenPayload, UserInvite, AcceptInvite, InviteToken, sendRequest, createUser, UserRole
from app.infrastructure.database.database import get_db, asyncSQLRepo
from app.auth.utils.utils import send_email, hash_password, generate_temporary_password


from app.auth.services.auth_services import AuthService


auth_router = APIRouter()

SECRET_KEY = os.getenv("KEY")
algorithm = "HS256"


@auth_router.post("/create", response_model=UserInvite)
async def create_user(user: Annotated[createUser, Body()],
                       db: Annotated[asyncpg.Connection, Depends(get_db)],
                        _: str = Depends(required_roles(UserRole.superuser, UserRole.admin))) -> UserInvite:
    user = await AuthService.create_user(db=db, user=user)
    return user



@auth_router.post("/send_invite", response_model=dict)
async def invite_user(user_id:Annotated[sendRequest, Body()], 
                      db: Annotated[asyncpg.Connection, Depends(get_db)],
                      _: str = Depends(required_roles(UserRole.superuser, UserRole.admin))):
    invite = await AuthService.invite_user(user_id=user_id, db=db)
    return invite

@auth_router.post("/accept_invite", response_model=dict)
async def accept_invite(data: Annotated[AcceptInvite, Body ()], 
                        db: Annotated[asyncpg.Connection, Depends(get_db)]):
    invite = await AuthService.accept_invite(data=data, db=db)
    return invite

@auth_router.get("/accept_invite", response_model=dict)
async def get_invite(token:str, db: Annotated[asyncpg.Connection, Depends(get_db)]):
    
    invite = await AuthService.get_invite(db=db, token=token)
    return invite


@auth_router.post("/login_token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                  db: Annotated[asyncpg.Connection, Depends(get_db)]) -> Token:
    login = await AuthService.login(form_data=form_data, db=db)
    return login
    



