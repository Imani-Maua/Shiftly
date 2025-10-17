from fastapi import FastAPI
from app.auth.routes import auth_router
from app.core.services.routes import schedule

app = FastAPI(title="Shiftly", version="1.0")
app.include_router(auth_router, prefix="/users")
app.include_router(schedule, prefix="/schedule")





