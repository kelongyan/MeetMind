"""FastAPI dependencies for authentication."""

from __future__ import annotations

import uuid

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.auth.service import decode_access_token
from app.config import settings
from app.db.models import User
from app.db.session import get_db_session

_security_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_security_scheme),
    session: Session = Depends(get_db_session),
) -> User:
    """Extract and validate the JWT token, returning the current user.

    When ``auth_required`` is False (dev/local mode), returns a synthetic
    local-dev user so the API remains usable without login.
    """
    if not settings.auth_required:
        return _get_or_create_local_user(session)

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
        )

    try:
        payload = decode_access_token(credentials.credentials)
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        ) from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        ) from exc

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    user = session.get(User, uuid.UUID(user_id))
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    return user


def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_security_scheme),
    session: Session = Depends(get_db_session),
) -> User | None:
    """Like get_current_user but returns None instead of raising 401."""
    if credentials is None:
        return None
    try:
        return get_current_user(credentials, session)
    except HTTPException:
        return None


_LOCAL_USER_EMAIL = "local@meetmind.dev"


def _get_or_create_local_user(session: Session) -> User:
    """Return (or create) a local-dev user for unauthenticated mode."""
    from sqlalchemy import select

    user = session.scalar(select(User).where(User.email == _LOCAL_USER_EMAIL))
    if user is not None:
        return user

    from app.auth.service import hash_password
    from app.db.models import UserRole

    user = User(
        email=_LOCAL_USER_EMAIL,
        display_name="Local Dev User",
        password_hash=hash_password("local-dev-password"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
