from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import auth, models, schemas
from ..db import get_db

router = APIRouter(prefix="/users", tags=["users"])


def _ensure_admin(user: models.User) -> None:
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )


@router.get("/", response_model=list[schemas.UserRead])
async def list_users(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(auth.get_current_active_user)],
):
    _ensure_admin(current_user)
    return db.query(models.User).order_by(models.User.created_at.desc()).all()


@router.patch("/{user_id}/role", response_model=schemas.UserRead)
async def update_user_role(
    user_id: int,
    role_update: schemas.UserRoleUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(auth.get_current_active_user)],
):
    _ensure_admin(current_user)

    user = db.get(models.User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user.id == current_user.id and role_update.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot remove your own admin role",
        )

    user.role = role_update.role
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
