from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import auth, models, schemas
from ..db import get_db

router = APIRouter(prefix="/dictionaries", tags=["dictionaries"])


@router.get("/catering", response_model=list[schemas.CateringCompanyRead])
async def list_catering_companies(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(auth.get_current_active_user)],
):
    return db.query(models.CateringCompany).order_by(models.CateringCompany.name.asc()).all()


@router.post("/catering", response_model=schemas.CateringCompanyRead, status_code=status.HTTP_201_CREATED)
async def create_catering_company(
    company_in: schemas.CateringCompanyCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(auth.get_current_active_admin)],
):
    existing = (
        db.query(models.CateringCompany)
        .filter(models.CateringCompany.tax_id == company_in.tax_id.strip())
        .first()
    )
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Firma o tym NIP już istnieje")
    company = models.CateringCompany(**company_in.model_dump())
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


@router.delete("/catering/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_catering_company(
    company_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(auth.get_current_active_admin)],
):
    company = db.get(models.CateringCompany, company_id)
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nie znaleziono firmy")
    db.delete(company)
    db.commit()
    return None


@router.get("/accommodation", response_model=list[schemas.AccommodationCompanyRead])
async def list_accommodation_companies(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(auth.get_current_active_user)],
):
    return (
        db.query(models.AccommodationCompany)
        .order_by(models.AccommodationCompany.name.asc())
        .all()
    )


@router.post("/accommodation", response_model=schemas.AccommodationCompanyRead, status_code=status.HTTP_201_CREATED)
async def create_accommodation_company(
    company_in: schemas.AccommodationCompanyCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(auth.get_current_active_admin)],
):
    existing = (
        db.query(models.AccommodationCompany)
        .filter(models.AccommodationCompany.tax_id == company_in.tax_id.strip())
        .first()
    )
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Firma o tym NIP już istnieje")
    company = models.AccommodationCompany(**company_in.model_dump())
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


@router.delete("/accommodation/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_accommodation_company(
    company_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(auth.get_current_active_admin)],
):
    company = db.get(models.AccommodationCompany, company_id)
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nie znaleziono firmy")
    db.delete(company)
    db.commit()
    return None


@router.get("/team", response_model=list[schemas.TeamMemberRead])
async def list_team_members(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(auth.get_current_active_user)],
):
    return db.query(models.TeamMember).order_by(models.TeamMember.name.asc()).all()


@router.post("/team", response_model=schemas.TeamMemberRead, status_code=status.HTTP_201_CREATED)
async def create_team_member(
    member_in: schemas.TeamMemberCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(auth.get_current_active_admin)],
):
    existing = (
        db.query(models.TeamMember)
        .filter(models.TeamMember.name == member_in.name.strip())
        .first()
    )
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Osoba o tej nazwie już istnieje")
    member = models.TeamMember(**member_in.model_dump())
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


@router.delete("/team/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team_member(
    member_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(auth.get_current_active_admin)],
):
    member = db.get(models.TeamMember, member_id)
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nie znaleziono osoby")
    db.delete(member)
    db.commit()
    return None
