from fastapi import FastAPI
from app.auth.routes import auth_router
from app.core.services.routes import schedule, shift_period

app = FastAPI(title="Shiftly", version="1.0")
app.include_router(auth_router, prefix="/users")
app.include_router(schedule, prefix="/schedule")
app.include_router(shift_period, prefix="/shift_period")






