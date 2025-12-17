from typing import Annotated, Optional, List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select, distinct
from sqlalchemy.orm import Session, joinedload

from .. import auth, models, schemas
from ..db import get_db

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/participants", response_model=List[str])
async def get_project_participants(
    project_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(auth.get_current_active_user)],
):
    """
    List all distinct workers (User or TeamMember names) who logged time on a specific project.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can view reports")

    # 1. Get User names
    user_names_query = (
        db.query(models.User.full_name)
        .join(models.WorkLog, models.User.id == models.WorkLog.user_id)
        .filter(models.WorkLog.project_id == project_id)
        .filter(models.WorkLog.team_member_id.is_(None))
        .distinct()
    )
    
    # 2. Get TeamMember names
    member_names_query = (
        db.query(models.TeamMember.name)
        .join(models.WorkLog, models.TeamMember.id == models.WorkLog.team_member_id)
        .filter(models.WorkLog.project_id == project_id)
        .distinct()
    )
    
    names = set()
    for (name,) in user_names_query.all():
        if name:
            names.add(name)
            
    for (name,) in member_names_query.all():
        if name:
            names.add(name)
            
    return sorted(list(names))


@router.get("/team-work", response_model=schemas.PaginatedResponse[schemas.WorkLogRead])
async def get_team_work_report(
    team_id: int,
    start_date: datetime,
    end_date: datetime,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(auth.get_current_active_user)],
    page: int = Query(default=1, ge=1),
    size: int = Query(default=50, ge=1, le=200),
):
    """
    List worklogs for a specific team within a date range.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can view reports")
        
    query = (
        db.query(models.WorkLog)
        .join(models.TeamMember, models.WorkLog.team_member_id == models.TeamMember.id)
        .filter(models.TeamMember.team_id == team_id)
        .filter(models.WorkLog.date >= start_date)
        .filter(models.WorkLog.date <= end_date)
        .options(joinedload(models.WorkLog.user))
        .options(joinedload(models.WorkLog.team_member))
        .options(joinedload(models.WorkLog.project))
    )
    
    total = query.count()
    pages = (total + size - 1) // size
    items = (
        query.order_by(models.WorkLog.date.desc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )
    
    return schemas.PaginatedResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/accommodation", response_model=schemas.PaginatedResponse[schemas.WorkLogRead])
async def get_accommodation_report(
    start_date: datetime,
    end_date: datetime,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(auth.get_current_active_user)],
    company_id: Optional[int] = None,
    page: int = Query(default=1, ge=1),
    size: int = Query(default=50, ge=1, le=200),
):
    """
    List worklogs with overnight stays > 0.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can view reports")
        
    query = (
        db.query(models.WorkLog)
        .filter(models.WorkLog.overnight_stays > 0)
        .filter(models.WorkLog.date >= start_date)
        .filter(models.WorkLog.date <= end_date)
        .options(joinedload(models.WorkLog.user))
        .options(joinedload(models.WorkLog.team_member))
        .options(joinedload(models.WorkLog.accommodation_company))
        .options(joinedload(models.WorkLog.project))
    )
    
    if company_id:
        query = query.filter(models.WorkLog.accommodation_company_id == company_id)
        
    total = query.count()
    pages = (total + size - 1) // size
    items = (
        query.order_by(models.WorkLog.date.desc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )
        
    return schemas.PaginatedResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/catering", response_model=schemas.PaginatedResponse[schemas.WorkLogRead])
async def get_catering_report(
    start_date: datetime,
    end_date: datetime,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(auth.get_current_active_user)],
    company_id: Optional[int] = None,
    page: int = Query(default=1, ge=1),
    size: int = Query(default=50, ge=1, le=200),
):
    """
    List worklogs with meals_served > 0.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can view reports")

    query = (
        db.query(models.WorkLog)
        .filter(models.WorkLog.meals_served > 0)
        .filter(models.WorkLog.date >= start_date)
        .filter(models.WorkLog.date <= end_date)
        .options(joinedload(models.WorkLog.user))
        .options(joinedload(models.WorkLog.team_member))
        .options(joinedload(models.WorkLog.catering_company))
        .options(joinedload(models.WorkLog.project))
    )
    
    if company_id:
        query = query.filter(models.WorkLog.catering_company_id == company_id)

    total = query.count()
    pages = (total + size - 1) // size
    items = (
        query.order_by(models.WorkLog.date.desc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )
        
    return schemas.PaginatedResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages
    )
