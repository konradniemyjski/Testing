from __future__ import annotations

from datetime import datetime
from io import BytesIO
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from openpyxl import Workbook

from .. import auth, models, schemas
from ..db import get_db

router = APIRouter(prefix="/worklogs", tags=["worklogs"])


def _build_user_worklog_query(
    db: Session,
    current_user: models.User,
    project_id: int | None,
    start_date: datetime | None,
    end_date: datetime | None,
):
    query = (
        db.query(models.WorkLog)
        .options(joinedload(models.WorkLog.user))
        .options(joinedload(models.WorkLog.team_member))
        .options(joinedload(models.WorkLog.accommodation_company))
        .options(joinedload(models.WorkLog.catering_company))
    )
    if current_user.role != "admin":
        query = query.filter(models.WorkLog.user_id == current_user.id)
    if project_id is not None:
        query = query.filter(models.WorkLog.project_id == project_id)
    if start_date is not None:
        query = query.filter(models.WorkLog.date >= start_date)
    if end_date is not None:
        query = query.filter(models.WorkLog.date <= end_date)
    return query


@router.get("/", response_model=list[schemas.WorkLogRead])
async def list_worklogs(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(auth.get_current_active_user)],
    project_id: int | None = Query(default=None),
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
):
    query = _build_user_worklog_query(db, current_user, project_id, start_date, end_date)
    return query.order_by(models.WorkLog.date.desc()).all()


@router.get("/latest-by-team", response_model=schemas.WorkLogRead | None)
async def get_latest_worklog_by_team(
    team_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(auth.get_current_active_user)],
):
    """
    Get the most recent worklog for a specific team.
    Used for auto-filling form data.
    """
    query = (
        db.query(models.WorkLog)
        .join(models.TeamMember, models.WorkLog.team_member_id == models.TeamMember.id)
        .filter(models.TeamMember.team_id == team_id)
        .order_by(models.WorkLog.date.desc())
    )
    
    # If user is not admin, ensure they can only see their own logs? 
    # Actually, for suggestions, seeing team's last log might be useful even if not own, 
    # but strictly adhering to privacy:
    if current_user.role != "admin":
        query = query.filter(models.WorkLog.user_id == current_user.id)

    return query.first()


@router.post("/", response_model=schemas.WorkLogRead, status_code=status.HTTP_201_CREATED)
async def create_worklog(
    worklog_in: schemas.WorkLogCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(auth.get_current_active_user)],
):
    project = db.get(models.Project, worklog_in.project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Project does not exist")

    if worklog_in.team_member_id is not None and not db.get(models.TeamMember, worklog_in.team_member_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Team member does not exist")
    if worklog_in.accommodation_company_id is not None and not db.get(
        models.AccommodationCompany, worklog_in.accommodation_company_id
    ):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Accommodation company does not exist")
    if worklog_in.catering_company_id is not None and not db.get(
        models.CateringCompany, worklog_in.catering_company_id
    ):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Catering company does not exist")
    worklog_data = worklog_in.model_dump()
    worklog_data["site_code"] = worklog_data["site_code"].strip()
    if project.code and not worklog_data["site_code"]:
        worklog_data["site_code"] = project.code
    if worklog_data.get("notes"):
        worklog_data["notes"] = worklog_data["notes"].strip() or None
    worklog = models.WorkLog(**worklog_data, user_id=current_user.id)
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
    if "team_member_id" in update_data and update_data["team_member_id"] is not None:
        if not db.get(models.TeamMember, update_data["team_member_id"]):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Team member does not exist")
    if (
        "accommodation_company_id" in update_data
        and update_data["accommodation_company_id"] is not None
    ):
        if not db.get(models.AccommodationCompany, update_data["accommodation_company_id"]):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Accommodation company does not exist")
    if "catering_company_id" in update_data and update_data["catering_company_id"] is not None:
        if not db.get(models.CateringCompany, update_data["catering_company_id"]):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Catering company does not exist")
    if "site_code" in update_data and update_data["site_code"] is not None:
        update_data["site_code"] = update_data["site_code"].strip()
    if "notes" in update_data and update_data["notes"] is not None:
        update_data["notes"] = update_data["notes"].strip() or None
    for field, value in update_data.items():
        setattr(worklog, field, value)
    db.add(worklog)
    db.commit()
    db.refresh(worklog)
    return worklog


@router.get("/export")
async def export_worklogs(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(auth.get_current_active_user)],
    project_id: int | None = Query(default=None),
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
):
    query = _build_user_worklog_query(db, current_user, project_id, start_date, end_date)
    worklogs = (
        query.options(
            joinedload(models.WorkLog.project),
            joinedload(models.WorkLog.team_member).joinedload(models.TeamMember.team),
        )
        .order_by(models.WorkLog.date.asc(), models.WorkLog.id.asc())
        .all()
    )

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Ewidencja czasu pracy"

    headers = [
        "Data",
        "Kod budowy",
        "Nazwa budowy",
        "Członek zespołu",
        "Zespół",
        "Liczba pracowników",
        "Łączna liczba godzin",
        "Posiłki",
        "Firma cateringowa",
        "Noclegi",
        "Firma noclegowa",
        "Nieobecności",
        "Uwagi",
        "Autor",
    ]
    sheet.append(headers)

    for worklog in worklogs:
        project_name = worklog.project.name if worklog.project else ""
        author = worklog.user
        if author is not None:
            display_name = (author.full_name or "").strip() or author.email
            author_label = f"{display_name} (ID: {author.id})"
        else:
            author_label = f"ID: {worklog.user_id}"
        team_member = worklog.team_member.name if worklog.team_member else ""
        team_name = worklog.team_member.team.name if worklog.team_member and worklog.team_member.team else ""
        catering_company = worklog.catering_company.name if worklog.catering_company else ""
        accommodation_company = (
            worklog.accommodation_company.name if worklog.accommodation_company else ""
        )
        sheet.append(
            [
                worklog.date.date().isoformat(),
                worklog.site_code,
                project_name,
                team_member,
                team_name,
                worklog.employee_count,
                float(worklog.hours_worked),
                worklog.meals_served,
                catering_company,
                worklog.overnight_stays,
                accommodation_company,
                worklog.absences,
                worklog.notes or "",
                author_label,
            ]
        )

    for column_cells in sheet.columns:
        max_length = max((len(str(cell.value)) if cell.value is not None else 0) for cell in column_cells)
        adjusted_width = max_length + 2
        column_letter = column_cells[0].column_letter
        sheet.column_dimensions[column_letter].width = min(adjusted_width, 40)

    stream = BytesIO()
    workbook.save(stream)
    stream.seek(0)

    filename = f"raport_godzin_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    headers_response = {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    }

    return StreamingResponse(stream, media_type=headers_response["Content-Type"], headers=headers_response)


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
