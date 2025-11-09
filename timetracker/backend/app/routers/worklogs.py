from __future__ import annotations

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from .. import auth, models, schemas
from ..db import get_db

router = APIRouter(prefix="/worklogs", tags=["worklogs"])


@router.get("/", response_model=list[schemas.WorkLogRead])
async def list_worklogs(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(auth.get_current_active_user)],
    project_id: int | None = Query(default=None),
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
):
    query = db.query(models.WorkLog).filter(models.WorkLog.user_id == current_user.id)
    if project_id is not None:
        query = query.filter(models.WorkLog.project_id == project_id)
    if start_date is not None:
        query = query.filter(models.WorkLog.date >= start_date)
    if end_date is not None:
        query = query.filter(models.WorkLog.date <= end_date)
    return query.order_by(models.WorkLog.date.desc()).all()


@router.post("/", response_model=schemas.WorkLogRead, status_code=status.HTTP_201_CREATED)
async def create_worklog(
    worklog_in: schemas.WorkLogCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(auth.get_current_active_user)],
):
    project = db.get(models.Project, worklog_in.project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Project does not exist")
    worklog = models.WorkLog(**worklog_in.model_dump(), user_id=current_user.id)
    db.add(worklog)
    db.commit()
    db.refresh(worklog)
    return worklog


@router.put("/{worklog_id}", response_model=schemas.WorkLogRead)
async def update_worklog(
    worklog_id: int,
    worklog_in: schemas.WorkLogUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(auth.get_current_active_user)],
):
    worklog = db.get(models.WorkLog, worklog_id)
    if not worklog or worklog.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Work log not found")
    update_data = worklog_in.model_dump(exclude_unset=True)
    if "project_id" in update_data:
        project = db.get(models.Project, update_data["project_id"])
        if not project:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Project does not exist")
    for field, value in update_data.items():
        setattr(worklog, field, value)
    db.add(worklog)
    db.commit()
    db.refresh(worklog)
    return worklog


@router.delete("/{worklog_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_worklog(
    worklog_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(auth.get_current_active_user)],
):
    worklog = db.get(models.WorkLog, worklog_id)
    if not worklog or worklog.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Work log not found")
    db.delete(worklog)
    db.commit()
    return None
