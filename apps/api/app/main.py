from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text

from app.action_items.router import router as action_items_router
from app.assets.router import router as assets_router
from app.auth.router import router as auth_router
from app.config import settings
from app.exceptions import (
    ConflictError,
    FileTooLargeError,
    InvalidFileTypeError,
    NotFoundError,
)
from app.export.router import router as export_router
from app.insights.router import router as insights_router
from app.jobs.router import router as jobs_router
from app.knowledge.router import router as knowledge_router
from app.logging_config import configure_logging
from app.meetings.router import router as meetings_router
from app.middleware.rate_limiting import limiter
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.observability.provider_telemetry import ProviderCallError
from app.operations.router import router as operations_router
from app.qa.router import router as qa_router
from app.structuring.router import router as structuring_router
from app.transcription.router import router as transcription_router

# Configure structured logging before anything else.
configure_logging(environment=settings.environment)

app = FastAPI(title=settings.app_name, version="0.1.0")

# --- Middleware (outermost first) ---
app.add_middleware(RequestIDMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={"detail": f"Rate limit exceeded: {exc.detail}"},
    )


# --- Routers ---
app.include_router(auth_router)
app.include_router(meetings_router)
app.include_router(assets_router)
app.include_router(jobs_router)
app.include_router(transcription_router)
app.include_router(structuring_router)
app.include_router(insights_router)
app.include_router(action_items_router)
app.include_router(knowledge_router)
app.include_router(operations_router)
app.include_router(qa_router)
app.include_router(export_router)


# --- Exception handlers ---


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


@app.exception_handler(FileTooLargeError)
def file_too_large_handler(_request: Request, exc: FileTooLargeError) -> JSONResponse:
    return JSONResponse(status_code=413, content={"detail": exc.detail})


@app.exception_handler(ProviderCallError)
def provider_call_error_handler(
    _request: Request, exc: ProviderCallError
) -> JSONResponse:
    return JSONResponse(status_code=502, content={"detail": exc.detail})


# --- Health check ---


@app.get("/health", tags=["health"], response_model=None)
def health_check() -> dict[str, object] | JSONResponse:
    from app.db.session import SessionLocal

    checks: dict[str, str] = {}

    # Database check (always required)
    try:
        with SessionLocal() as session:
            session.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as exc:
        checks["database"] = f"error: {exc}"
        return JSONResponse(
            status_code=503,
            content={
                "status": "degraded",
                "service": "meetmind-api",
                "version": app.version,
                "checks": checks,
            },
        )

    # Optional Redis check
    if settings.health_check_redis and settings.redis_url:
        try:
            import redis

            r = redis.from_url(settings.redis_url, socket_timeout=2)
            r.ping()
            checks["redis"] = "ok"
        except Exception as exc:
            checks["redis"] = f"error: {exc}"

    # Optional S3/MinIO check
    if settings.health_check_s3 and settings.s3_endpoint_url:
        try:
            import urllib.request

            req = urllib.request.Request(
                settings.s3_endpoint_url + "/minio/health/live",
                method="GET",
            )
            urllib.request.urlopen(req, timeout=2)
            checks["object_storage"] = "ok"
        except Exception as exc:
            checks["object_storage"] = f"error: {exc}"

    return {
        "status": "ok",
        "service": "meetmind-api",
        "version": app.version,
        "checks": checks,
    }
