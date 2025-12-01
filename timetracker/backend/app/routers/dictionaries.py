from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from .. import auth, models, schemas
from ..db import get_db

router = APIRouter(prefix="/dictionaries", tags=["dictionaries"])


def get_default_team(db: Session) -> models.Team:
    team = (
        db.query(models.Team)
        .options(joinedload(models.Team.members))
        .order_by(models.Team.id.asc())
        .first()
    )
    if team:
        team.members = (
            db.query(models.TeamMember)
            .filter(
                (models.TeamMember.team_id == team.id)
                | (models.TeamMember.team_id.is_(None))
            )
            .order_by(models.TeamMember.name.asc())
            .all()
        )
        return team

    team = models.Team(name="Zespół")
    db.add(team)
    db.commit()
    db.refresh(team)
    return team


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


@router.put("/catering/{company_id}", response_model=schemas.CateringCompanyRead)
async def update_catering_company(
    company_id: int,
    company_in: schemas.CateringCompanyUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(auth.get_current_active_admin)],
):
    company = db.get(models.CateringCompany, company_id)
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nie znaleziono firmy")

    existing = (
        db.query(models.CateringCompany)
        .filter(
            models.CateringCompany.tax_id == company_in.tax_id.strip(),
            models.CateringCompany.id != company_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Firma o tym NIP już istnieje")

    company.tax_id = company_in.tax_id.strip()
    company.name = company_in.name.strip()
    db.commit()
    db.refresh(company)
    return company


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


@router.put(
    "/accommodation/{company_id}", response_model=schemas.AccommodationCompanyRead
)
async def update_accommodation_company(
    company_id: int,
    company_in: schemas.AccommodationCompanyUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(auth.get_current_active_admin)],
):
    company = db.get(models.AccommodationCompany, company_id)
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nie znaleziono firmy")

    existing = (
        db.query(models.AccommodationCompany)
        .filter(
            models.AccommodationCompany.tax_id == company_in.tax_id.strip(),
            models.AccommodationCompany.id != company_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Firma o tym NIP już istnieje")

    company.tax_id = company_in.tax_id.strip()
    company.name = company_in.name.strip()
    db.commit()
    db.refresh(company)
    return company


@router.get("/team", response_model=schemas.TeamRead)
async def get_team(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(auth.get_current_active_user)],
):
    return get_default_team(db)


@router.put("/team", response_model=schemas.TeamRead)
async def update_team(
    team_in: schemas.TeamUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(auth.get_current_active_admin)],
):
    team = get_default_team(db)
    team.name = team_in.name.strip()
    db.add(team)
    db.commit()
    db.refresh(team)
    return get_default_team(db)


@router.post("/team/members", response_model=schemas.TeamMemberRead, status_code=status.HTTP_201_CREATED)
async def create_team_member(
    member_in: schemas.TeamMemberCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(auth.get_current_active_admin)],
):
    target_team_id = member_in.team_id or get_default_team(db).id

    existing = (
        db.query(models.TeamMember)
        .filter(models.TeamMember.name == member_in.name.strip())
        .first()
    )
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Osoba o tej nazwie już istnieje")

    member = models.TeamMember(**member_in.model_dump())
    member.team_id = target_team_id
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


@router.put("/team/members/{member_id}", response_model=schemas.TeamMemberRead)
async def update_team_member(
    member_id: int,
    member_in: schemas.TeamMemberUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(auth.get_current_active_admin)],
):
    member = db.get(models.TeamMember, member_id)
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nie znaleziono osoby")

    target_team_id = member_in.team_id or get_default_team(db).id

    existing = (
        db.query(models.TeamMember)
        .filter(
            models.TeamMember.name == member_in.name.strip(),
            models.TeamMember.id != member_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Osoba o tej nazwie już istnieje")

    member.name = member_in.name.strip()
    member.role = member_in.role
    member.team_id = target_team_id

    db.add(member)
    db.commit()
    db.refresh(member)
    return member


@router.delete("/team/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
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
