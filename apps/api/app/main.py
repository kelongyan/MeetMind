from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.config import settings
from app.exceptions import NotFoundError
from app.insights.router import router as insights_router
from app.jobs.router import router as jobs_router
from app.meetings.router import router as meetings_router
from app.transcription.router import router as transcription_router

app = FastAPI(title=settings.app_name, version="0.1.0")
app.include_router(meetings_router)
app.include_router(jobs_router)
app.include_router(transcription_router)
app.include_router(insights_router)


@app.exception_handler(NotFoundError)
def not_found_error_handler(_request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": exc.detail})


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "meetmind-api",
        "version": app.version,
    }
