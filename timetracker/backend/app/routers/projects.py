from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from .. import auth, models, schemas
from ..db import get_db

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/", response_model=list[schemas.ProjectRead])
async def list_projects(
    db: Annotated[Session, Depends(get_db)],
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
):
    return (
        db.query(models.Project)
        .order_by(models.Project.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.post("/", response_model=schemas.ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_in: schemas.ProjectCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[models.User, Depends(auth.get_current_active_user)],
):
    project_data = project_in.model_dump()
    project_data["code"] = project_data["code"].strip()
    project_data["name"] = project_data["name"].strip()
    if project_data.get("description"):
        project_data["description"] = project_data["description"].strip() or None

    if not project_data["code"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Project code cannot be empty")
    if not project_data["name"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Project name cannot be empty")

    existing_name = db.query(models.Project).filter(models.Project.name == project_data["name"]).first()
    if existing_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Project name already in use")

    existing_code = db.query(models.Project).filter(models.Project.code == project_data["code"]).first()
    if existing_code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Project code already in use")
    project = models.Project(**project_data)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("/{project_id}", response_model=schemas.ProjectRead)
async def read_project(project_id: int, db: Annotated[Session, Depends(get_db)]):
    project = db.get(models.Project, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


@router.put("/{project_id}", response_model=schemas.ProjectRead)
async def update_project(
    project_id: int,
    project_in: schemas.ProjectUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[models.User, Depends(auth.get_current_active_admin)],
):
    project = db.get(models.Project, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    update_data = project_in.model_dump(exclude_unset=True)
    if "name" in update_data:
        update_data["name"] = update_data["name"].strip() if update_data["name"] is not None else None
        if update_data["name"] == "":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Project name cannot be empty")
        existing = (
            db.query(models.Project)
            .filter(models.Project.name == update_data["name"], models.Project.id != project_id)
            .first()
        )
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Project name already in use")
    if "code" in update_data:
        update_data["code"] = update_data["code"].strip() if update_data["code"] is not None else None
        if update_data["code"] == "":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Project code cannot be empty")
        existing_code = (
            db.query(models.Project)
            .filter(models.Project.code == update_data["code"], models.Project.id != project_id)
            .first()
        )
        if existing_code:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Project code already in use")
    if "description" in update_data and update_data["description"] is not None:
        update_data["description"] = update_data["description"].strip() or None
    for field, value in update_data.items():
        setattr(project, field, value)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[models.User, Depends(auth.get_current_active_admin)],
):
    project = db.get(models.Project, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    db.delete(project)
    db.commit()
    return None
