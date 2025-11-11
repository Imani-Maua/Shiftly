from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from app.core.utils.exceptions import AppBaseException
from app.core.routes.schedule_route import schedule
from app.core.routes.talent_route import talents
from app.auth.routes.routes import auth_router
from app.core.routes.talent_constraint_route import talent_constraints


app = FastAPI(title="Shiftly", version="1.0")

app.include_router(auth_router, prefix="/users")
app.include_router(schedule, prefix="/schedule")
app.include_router(talents, prefix="/talents")
app.include_router(talent_constraints, prefix="/talent_constraints")









