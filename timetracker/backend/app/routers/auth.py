from __future__ import annotations

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .. import auth, models, schemas
from ..db import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
) -> schemas.Token:
    """Authenticate a user and return an access token."""
    user = auth.authenticate_user(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return schemas.Token(access_token=access_token)


@router.get("/me", response_model=schemas.UserRead)
async def read_users_me(
    current_user: Annotated[models.User, Depends(auth.get_current_active_user)],
) -> models.User:
    """Return the authenticated user's profile."""
    return current_user


@router.post("/register", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_in: schemas.UserCreate,
    db: Annotated[Session, Depends(get_db)],
) -> models.User:
    """Register a new standard user."""
    normalized_email = user_in.email.strip()
    existing_user = (
        db.query(models.User)
        .filter(models.User.email == normalized_email)
        .first()
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    hashed_password = auth.get_password_hash(user_in.password)
    db_user = models.User(
        email=normalized_email,
        full_name=user_in.full_name.strip() if user_in.full_name else None,
        role="user",
        hashed_password=hashed_password,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
