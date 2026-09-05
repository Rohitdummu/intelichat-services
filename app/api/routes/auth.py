from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.schemas.auth import Token, UserCreate, UserLogin, UserRead
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserRead, summary="Register a new user")
def register_user(payload: UserCreate, db: Session = Depends(get_db)) -> UserRead:
    service = AuthService(db)
    try:
        user = service.register_user(payload.email, payload.password)
        db.commit()
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return user


@router.post("/login", response_model=Token, summary="Log in and obtain an access token")
def login_user(payload: UserLogin, db: Session = Depends(get_db)) -> Token:
    service = AuthService(db)
    try:
        user = service.authenticate(payload.email, payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    token = service.create_token(user)
    return Token(access_token=token)


@router.get("/me", response_model=UserRead, summary="Get the authenticated user")
def get_me(current_user=Depends(get_current_user)) -> UserRead:
    return current_user
