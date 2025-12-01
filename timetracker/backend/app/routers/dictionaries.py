from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from .. import auth, models, schemas
from ..db import get_db

router = APIRouter(prefix="/dictionaries", tags=["dictionaries"])


def ensure_default_team(db: Session) -> None:
    existing_team = db.query(models.Team).order_by(models.Team.id.asc()).first()
    if existing_team:
        return

    team = models.Team(name="Zespół")
    db.add(team)
    db.commit()


def serialize_teams(db: Session) -> list[models.Team]:
    ensure_default_team(db)
    teams = (
        db.query(models.Team)
        .options(joinedload(models.Team.members))
        .order_by(models.Team.name.asc(), models.Team.id.asc())
        .all()
    )
    for team in teams:
        team.members = (
            db.query(models.TeamMember)
            .filter(models.TeamMember.team_id == team.id)
            .order_by(models.TeamMember.name.asc())
            .all()
        )
    return teams


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


@router.get("/team", response_model=list[schemas.TeamRead])
async def list_teams(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(auth.get_current_active_user)],
):
    return serialize_teams(db)


@router.post("/team", response_model=schemas.TeamRead, status_code=status.HTTP_201_CREATED)
async def create_team(
    team_in: schemas.TeamCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(auth.get_current_active_admin)],
):
    ensure_default_team(db)
    trimmed_name = team_in.name.strip()
    existing = (
        db.query(models.Team).filter(models.Team.name == trimmed_name).first()
    )
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Zespół o tej nazwie już istnieje")

    team = models.Team(name=trimmed_name)
    db.add(team)
    db.commit()
    db.refresh(team)
    loaded = (
        db.query(models.Team)
        .options(joinedload(models.Team.members))
        .filter(models.Team.id == team.id)
        .first()
    )
    return loaded or team


@router.put("/team/{team_id}", response_model=schemas.TeamRead)
async def update_team(
    team_id: int,
    team_in: schemas.TeamUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(auth.get_current_active_admin)],
):
    team = db.get(models.Team, team_id)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nie znaleziono zespołu")

    trimmed_name = team_in.name.strip()
    existing = (
        db.query(models.Team)
        .filter(models.Team.name == trimmed_name, models.Team.id != team_id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Zespół o tej nazwie już istnieje")

    team.name = trimmed_name
    db.add(team)
    db.commit()
    db.refresh(team)
    loaded = (
        db.query(models.Team)
        .options(joinedload(models.Team.members))
        .filter(models.Team.id == team.id)
        .first()
    )
    return loaded or team


@router.post("/team/members", response_model=schemas.TeamMemberRead, status_code=status.HTTP_201_CREATED)
async def create_team_member(
    member_in: schemas.TeamMemberCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(auth.get_current_active_admin)],
):
    ensure_default_team(db)
    target_team_id = member_in.team_id
    if target_team_id is None:
        target_team = db.query(models.Team).order_by(models.Team.id.asc()).first()
        target_team_id = target_team.id if target_team else None

    if target_team_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Brak zespołu do przypisania")

    team = db.get(models.Team, target_team_id)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nie znaleziono zespołu")

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

    ensure_default_team(db)
    target_team_id = member_in.team_id
    if target_team_id is None:
        target_team = db.query(models.Team).order_by(models.Team.id.asc()).first()
        target_team_id = target_team.id if target_team else None

    if target_team_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Brak zespołu do przypisania")

    team = db.get(models.Team, target_team_id)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nie znaleziono zespołu")

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
