from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
import asyncpg
from jose import jwt, JWTError
from datetime import timedelta, timezone, datetime
from app.config.config import Settings
from app.auth.schema import createUser, UserInvite, sendRequest, UserInDB, TokenPayload, InviteToken, AcceptInvite, Token
from app.auth.services.security import user_in_db, get_user, create_jwt, store_token, verify_token_type, token_in_db, authenticate_user
from app.auth.utils.utils import generate_temporary_password, hash_password, send_email
from app.database.database import asyncSQLRepo

settings = Settings()
algorithm = "HS256"
JWT_KEY = settings.KEY

class AuthService():
    
    @staticmethod
    async def create_user(*, db:asyncpg.Connection, user:createUser):
        username = f"{user.firstname.strip().lower()}.{user.lastname.strip().lower()}"
        user_exists = await user_in_db(db=db, username=username)
        if user_exists:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User already exists")
        insert_query = "INSERT INTO users (username, firstname, lastname, email, user_role, pwd_hash, is_active) VALUES ($1, $2, $3, $4 ,$5 ,$6, $7) RETURNING id"
        temporary = generate_temporary_password() 
        if not temporary:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate temporary password")
        hashed = hash_password(temporary)
        row = await db.fetchrow(insert_query, username, user.firstname, user.lastname, user.email, user.user_role, hashed, False) 
        id = row["id"]
        return UserInvite(sub=id,username=username, email=user.email, role=user.user_role, password=temporary) 
    
    @staticmethod
    async def invite_user(*, user_id:sendRequest, db: asyncpg.Connection):
        INVITE_EXPIRY_HOURS = 24
        user: UserInDB = await get_user(db=db, id=user_id.user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User does not exist")
        try:
            payload = TokenPayload(sub=user.username, id=user.id, email=user.email, role=user.user_role, type="invite")
        except:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid input value")
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
    
    @staticmethod
    async def accept_invite(*, data: AcceptInvite, db: asyncpg.Connection):
        try:
            token_type = verify_token_type(data.token, "invite")
            payload = TokenPayload(**token_type)
            token: InviteToken = await token_in_db(db, data.token)
            if not token:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token missing.")
            
            if datetime.now(timezone.utc) > payload.exp:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Expired token. Ask your admin for a new token")
            user_id = payload.id
            user: UserInDB = await user_in_db(db=db, id=user_id)
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
            hashed_password = hash_password(data.new_password)
            user_query = f"UPDATE users SET pwd_hash = $1, is_active = {True} WHERE id= $2"
            payload = jwt.decode(data.token, JWT_KEY, algorithms=algorithm)
            jti = payload.get("jti")
            activate_user = await asyncSQLRepo(conn=db, query=user_query, params=(hashed_password, user_id,)).execute()
            token_query = f"UPDATE invite_token SET used_at = $1 WHERE jti = $2"
            set_used_time = await asyncSQLRepo(conn=db, query=token_query, params=(datetime.now(), jti,)).execute()
            return {"message": "Account activated successfully! Click here to login"}
        
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired invite token")

    @staticmethod
    async def get_invite(*, token:str, db: asyncpg.Connection):
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

    @staticmethod
    async def login(*, form_data:OAuth2PasswordRequestForm, db: asyncpg.Connection):
        ACCESS_EXPIRY_DAYS = 4
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
       



        


