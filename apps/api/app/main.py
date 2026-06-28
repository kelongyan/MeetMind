from fastapi import FastAPI

from app.config import settings

app = FastAPI(title=settings.app_name, version="0.1.0")


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "meetmind-api",
        "version": app.version,
    }
