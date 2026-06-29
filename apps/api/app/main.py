from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.assets.router import router as assets_router
from app.config import settings
from app.exceptions import ConflictError, InvalidFileTypeError, NotFoundError
from app.insights.router import router as insights_router
from app.jobs.router import router as jobs_router
from app.meetings.router import router as meetings_router
from app.structuring.router import router as structuring_router
from app.transcription.router import router as transcription_router

app = FastAPI(title=settings.app_name, version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(meetings_router)
app.include_router(assets_router)
app.include_router(jobs_router)
app.include_router(transcription_router)
app.include_router(structuring_router)
app.include_router(insights_router)


@app.exception_handler(NotFoundError)
def not_found_error_handler(_request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": exc.detail})


@app.exception_handler(ConflictError)
def conflict_error_handler(_request: Request, exc: ConflictError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": exc.detail})


@app.exception_handler(InvalidFileTypeError)
def invalid_file_type_handler(
    _request: Request, exc: InvalidFileTypeError
) -> JSONResponse:
    return JSONResponse(status_code=415, content={"detail": exc.detail})


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "meetmind-api",
        "version": app.version,
    }
