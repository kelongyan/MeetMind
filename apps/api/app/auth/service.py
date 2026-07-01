"""Authentication service: user registration, login, and JWT token management."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import bcrypt
import jwt
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.db.models import User, UserRole


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def register_user(
    session: Session, email: str, display_name: str, password: str
) -> User:
    """Register a new user. Raises ValueError if email already exists."""
    existing = session.scalar(select(User).where(User.email == email))
    if existing is not None:
        raise ValueError("A user with this email already exists")

    user = User(
        id=uuid.uuid4(),
        email=email,
        display_name=display_name,
        password_hash=hash_password(password),
        role=UserRole.MEMBER,
        is_active=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def authenticate_user(session: Session, email: str, password: str) -> User | None:
    """Authenticate a user by email and password. Returns None on failure."""
    user = session.scalar(select(User).where(User.email == email))
    if user is None or not user.is_active:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def create_access_token(user: User) -> tuple[str, int]:
    """Create a JWT access token for the given user.

    Returns (token_string, expires_in_seconds).
    """
    expires_in = settings.jwt_expire_minutes * 60
    now = datetime.now(UTC)
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role.value,
        "iat": now,
        "exp": now + timedelta(seconds=expires_in),
    }
    token = jwt.encode(
        payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )
    return token, expires_in


def decode_access_token(token: str) -> dict:
    """Decode and validate a JWT token. Raises jwt.PyJWTError on failure."""
    return jwt.decode(
        token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
    )
