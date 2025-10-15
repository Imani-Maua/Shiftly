import asyncio
from jose import jwt
from app.database.database import asyncSQLRepo, get_db, db_pool
from app.auth.routes import login_for_access_token, invite_user, accept_invite
from app.auth.security import get_user, authenticate_user, verify_token, user_in_db, create_access_token
from app.auth.utils import verify_password
from app.auth.models import TokenPayload, AcceptInvite
from pprint import pprint




async def main():
    # ---- initialize the pool ----
    await db_pool()

    # --- open database connection ---
    async for conn in get_db():
        authenticate = await login_for_access_token(username="elaine.maua", password="strongpassword123", db=conn)
        print(authenticate)


if __name__ == '__main__':
    asyncio.run(main())