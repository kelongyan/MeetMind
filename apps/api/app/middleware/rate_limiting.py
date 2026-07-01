"""Rate limiting configuration using slowapi."""

from __future__ import annotations

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import settings


def _key_func(request: object) -> str:
    """Extract client IP for rate limiting."""
    return get_remote_address(request)  # type: ignore[arg-type]


limiter = Limiter(
    key_func=_key_func,
    default_limits=[settings.rate_limit_default],
    enabled=settings.rate_limit_enabled and settings.environment != "test",
)
