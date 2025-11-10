from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas
from ..db import get_db

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/", response_model=List[schemas.ProjectRead])
def get_projects(
    db: Session = Depends(get_db),
):
    """Get all projects"""
    projects = db.query(models.Project).all()
    return projects


@router.get("/{project_id}", response_model=schemas.ProjectRead)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
):
    """Get single project by ID"""
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/", response_model=schemas.ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(
    project: schemas.ProjectCreate,
    db: Session = Depends(get_db),
):
    """Create a new project"""
    db_project = models.Project(**project.dict())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


@router.put("/{project_id}", response_model=schemas.ProjectRead)
def update_project(
    project_id: int,
    project_update: schemas.ProjectCreate,
    db: Session = Depends(get_db),
):
    """Update an existing project"""
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Update project fields
    for key, value in project_update.dict().items():
        setattr(db_project, key, value)
    
    db.commit()
    db.refresh(db_project)
    return db_project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
):
    """Delete a project"""
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if project has any worklogs
    worklogs_count = db.query(models.WorkLog).filter(models.WorkLog.project_id == project_id).count()
    if worklogs_count > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Nie można usunąć budowy z {worklogs_count} powiązanymi wpisami pracy"
        )
    
    db.delete(db_project)
    db.commit()
    return None
