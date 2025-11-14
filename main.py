from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from app.core.utils.exceptions import AppBaseException
from app.core.schedule.routes import schedule
from app.core.talents.routes import talents
from app.auth.routes import auth_router
from app.core.constraints.talent_constraints.routes import talent_constraints
from app.core.constraints.constraint_rules.routes import constraint_rules


app = FastAPI(title="Shiftly", version="1.0")

app.include_router(auth_router, prefix="/users")
app.include_router(schedule, prefix="/schedule")
app.include_router(talents, prefix="/talents")
app.include_router(talent_constraints, prefix="/talent_constraints")
app.include_router(constraint_rules, prefix="/constraint_rules")









