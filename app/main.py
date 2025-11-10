from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from app.core.utils.exceptions import AppBaseException
from app.core.routes.schedule_route import schedule
from app.core.routes.talent_route import talents
from app.auth.routes import auth_router


app = FastAPI(title="Shiftly", version="1.0")


@app.exception_handler(AppBaseException)
async def app_exception_handler(request: Request, exc: AppBaseException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "path": str(request.url)}
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Unexpected internal server error"}
    )

app.include_router(auth_router, prefix="/users")
app.include_router(schedule, prefix="/schedule")
app.include_router(talents, prefix="/talents")









