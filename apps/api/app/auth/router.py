"""Authentication router: register, login, and me endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.schemas import TokenResponse, UserLogin, UserRead, UserRegister
from app.auth.service import authenticate_user, create_access_token, register_user
from app.db.models import User
from app.db.session import get_db_session
from app.exceptions import ConflictError

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(
    payload: UserRegister,
    session: Session = Depends(get_db_session),
) -> TokenResponse:
    try:
        user = register_user(
            session, payload.email, payload.display_name, payload.password
        )
    except ValueError as exc:
        raise ConflictError(str(exc)) from exc

    token, expires_in = create_access_token(user)
    return TokenResponse(
        access_token=token,
        expires_in=expires_in,
        user=UserRead.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
def login(
    payload: UserLogin,
    session: Session = Depends(get_db_session),
) -> TokenResponse:
    user = authenticate_user(session, payload.email, payload.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    token, expires_in = create_access_token(user)
    return TokenResponse(
        access_token=token,
        expires_in=expires_in,
        user=UserRead.model_validate(user),
    )


@router.get("/me", response_model=UserRead)
def get_me(current_user: User = Depends(get_current_user)) -> UserRead:
    return UserRead.model_validate(current_user)
