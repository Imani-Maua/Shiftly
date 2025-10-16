from fastapi import FastAPI
from app.auth.routes import auth_router
from app.core.services.routes import service_router

app = FastAPI(title="Shiftly", version="1.0")
app.include_router(auth_router, prefix="/users")
app.include_router(service_router, prefix="/schedule")




