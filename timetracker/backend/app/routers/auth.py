from __future__ import annotations

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .. import auth, models, schemas
from ..auth import get_password_hash, verify_password
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


@router.put("/me", response_model=schemas.UserRead)
async def update_users_me(
    payload: schemas.UserSelfUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(auth.get_current_active_user)],
) -> models.User:
    """Update the authenticated user's profile details."""

    update_data = payload.model_dump(exclude_unset=True)
    if not update_data:
        return current_user

    if "email" in update_data:
        normalized_email = update_data["email"].strip()
        if normalized_email != current_user.email:
            existing_user = (
                db.query(models.User)
                .filter(models.User.email == normalized_email, models.User.id != current_user.id)
                .first()
            )
            if existing_user is not None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Podany login jest już zajęty.",
                )
            current_user.email = normalized_email

    if "full_name" in update_data:
        full_name = update_data["full_name"]
        if full_name is not None:
            full_name = full_name.strip() or None
        current_user.full_name = full_name

    new_password = update_data.get("password")
    current_password = update_data.get("current_password")

    if new_password:
        if not current_password or not verify_password(current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Niepoprawne obecne hasło.",
            )
        current_user.hashed_password = get_password_hash(new_password)
    elif current_password and not new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aby zmienić hasło podaj nowe hasło.",
        )

    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return current_user


@router.post("/register", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_in: schemas.UserCreate,
    db: Annotated[Session, Depends(get_db)],
):
    """Register a new user"""
    # Check if user with this email already exists
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

    # Create new user with hashed password
    hashed_password = get_password_hash(user_in.password)
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
