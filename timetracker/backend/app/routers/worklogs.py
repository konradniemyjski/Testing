from __future__ import annotations

from datetime import datetime
from io import BytesIO
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload
from sqlalchemy import func

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


def _validate_daily_hours(
    db: Session, 
    user_id: int, 
    date: datetime, 
    new_hours: float, 
    exclude_worklog_id: int | None = None,
    extra_hours: float = 0.0
):
    """
    Check if adding new_hours (plus extra_hours from current batch) exceeds 24h for a specific day.
    """
    check_date = date.date() if isinstance(date, datetime) else date
    
    start_of_day = datetime.combine(check_date, datetime.min.time())
    end_of_day = datetime.combine(check_date, datetime.max.time())

    query = db.query(func.sum(models.WorkLog.hours_worked)).filter(
        models.WorkLog.user_id == user_id,
        models.WorkLog.date >= start_of_day,
        models.WorkLog.date <= end_of_day
    )
    
    if exclude_worklog_id:
        query = query.filter(models.WorkLog.id != exclude_worklog_id)
        
    current_db_sum = query.scalar() or 0.0
    
    if current_db_sum + new_hours + extra_hours > 24:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Przekroczono limit 24 godzin pracy w dniu {check_date}."
        )


@router.get("/", response_model=schemas.PaginatedResponse[schemas.WorkLogRead])
async def list_worklogs(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(auth.get_current_active_user)],
    project_id: int | None = Query(default=None),
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=25, ge=1, le=100),
):
    query = _build_user_worklog_query(db, current_user, project_id, start_date, end_date)
    
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


@router.post("/batch", response_model=list[schemas.WorkLogRead], status_code=status.HTTP_201_CREATED)
async def create_worklogs_batch(
    worklogs_in: list[schemas.WorkLogCreate],
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(auth.get_current_active_user)],
):
    """
    Create multiple worklogs at once.
    """
    created_worklogs = []
    batch_tracker = {} # (user_id, date) -> accumulated_hours
    
    for item in worklogs_in:
        # Validate 24h limit
        # Track hours within this batch for the same day
        check_date = item.date.date()
        tracker_key = (current_user.id, check_date)
        already_in_batch = batch_tracker.get(tracker_key, 0.0)
        
        _validate_daily_hours(
            db, 
            current_user.id, 
            item.date, 
            item.hours_worked, 
            extra_hours=already_in_batch
        )
        batch_tracker[tracker_key] = already_in_batch + item.hours_worked

        project = db.get(models.Project, item.project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Project {item.project_id} does not exist")

        if current_user.role != "admin" and item.team_member_id is not None:
             # Force team_member_id to None for non-admins to prevent them from logging for others
             # Or raise Forbidden. Since UI sets it to None, forcing it here is safer/backwards compatible?
             # Let's raise 403 to be strict.
             raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Użytkownicy mogą dodawać wpisy tylko dla siebie."
             )

        if item.team_member_id is not None and not db.get(models.TeamMember, item.team_member_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Team member {item.team_member_id} does not exist")
        
        if item.accommodation_company_id is not None and not db.get(models.AccommodationCompany, item.accommodation_company_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Accommodation company does not exist")
            
        if item.catering_company_id is not None and not db.get(models.CateringCompany, item.catering_company_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Catering company does not exist")

        worklog_data = item.model_dump()
        worklog_data["site_code"] = worklog_data["site_code"].strip()
        if project.code and not worklog_data["site_code"]:
            worklog_data["site_code"] = project.code
            
        if worklog_data.get("notes"):
            worklog_data["notes"] = worklog_data["notes"].strip() or None
            
        worklog = models.WorkLog(**worklog_data, user_id=current_user.id)
        db.add(worklog)
        created_worklogs.append(worklog)

    db.commit()
    
    for w in created_worklogs:
        db.refresh(w)
        
    return created_worklogs


@router.post("/", response_model=schemas.WorkLogRead, status_code=status.HTTP_201_CREATED)
async def create_worklog(
    worklog_in: schemas.WorkLogCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(auth.get_current_active_user)],
):
    # Validate 24h limit
    _validate_daily_hours(db, current_user.id, worklog_in.date, worklog_in.hours_worked)

    project = db.get(models.Project, worklog_in.project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Project does not exist")

    if current_user.role != "admin" and worklog_in.team_member_id is not None:
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Użytkownicy mogą dodawać wpisy tylko dla siebie."
         )

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

    if "hours_worked" in update_data or "date" in update_data:
        # Re-validate if hours or date changed
        check_date = update_data.get("date", worklog.date)
        check_hours = update_data.get("hours_worked", worklog.hours_worked)
        _validate_daily_hours(
            db, 
            current_user.id, 
            check_date, 
            check_hours, 
            exclude_worklog_id=worklog.id
        )

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
    worklogs_list = (
        query.options(
            joinedload(models.WorkLog.project),
            joinedload(models.WorkLog.team_member).joinedload(models.TeamMember.team),
        )
        .all()
    )

    # Sort by Worker Name, then Date
    def get_worker_name(w: models.WorkLog) -> str:
        if w.team_member and w.team_member.name:
            return w.team_member.name
        if w.user:
             return w.user.full_name or w.user.email or ""
        return ""

    worklogs_list.sort(key=lambda w: (get_worker_name(w), w.date))

    workbook = Workbook()
    
    # Sheet 1: Raw Data
    ws_data = workbook.active
    ws_data.title = "Dane szczegółowe"

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
    ws_data.append(headers)

    # Statistics accumulators
    total_hours = 0.0
    total_meals = 0
    total_stays = 0
    
    # Key: (site_code, project_name) -> {hours, meals, stays}
    site_stats = {}
    
    # Key: worker_name -> {hours, meals, stays, dates: set}
    worker_stats = {}

    for worklog in worklogs_list:
        # 1. Prepare data for row
        project_name = worklog.project.name if worklog.project else ""
        author = worklog.user
        if author is not None:
            display_name = (author.full_name or "").strip() or author.email
            author_label = f"{display_name} (ID: {author.id})"
        else:
            author_label = f"ID: {worklog.user_id}"
        
        worker_name = get_worker_name(worklog)
        team_name = worklog.team_member.team.name if worklog.team_member and worklog.team_member.team else ""
        catering_company = worklog.catering_company.name if worklog.catering_company else ""
        accommodation_company = (
            worklog.accommodation_company.name if worklog.accommodation_company else ""
        )
        
        # 2. Append row to Data Sheet
        ws_data.append(
            [
                worklog.date.date().isoformat(),
                worklog.site_code,
                project_name,
                worker_name,
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

        # 3. Accumulate stats
        h = float(worklog.hours_worked)
        m = worklog.meals_served
        s = worklog.overnight_stays

        total_hours += h
        total_meals += m
        total_stays += s

        site_key = (worklog.site_code, project_name)
        if site_key not in site_stats:
            site_stats[site_key] = {"hours": 0.0, "meals": 0, "stays": 0}
        
        site_stats[site_key]["hours"] += h
        site_stats[site_key]["meals"] += m
        site_stats[site_key]["stays"] += s

        if worker_name not in worker_stats:
            worker_stats[worker_name] = {"hours": 0.0, "meals": 0, "stays": 0, "dates": set()}
        
        worker_stats[worker_name]["hours"] += h
        worker_stats[worker_name]["meals"] += m
        worker_stats[worker_name]["stays"] += s
        worker_stats[worker_name]["dates"].add(worklog.date.date())

    # Adjust column widths for Data Sheet
    for column_cells in ws_data.columns:
        max_length = max((len(str(cell.value)) if cell.value is not None else 0) for cell in column_cells)
        adjusted_width = max_length + 2
        column_letter = column_cells[0].column_letter
        ws_data.column_dimensions[column_letter].width = min(adjusted_width, 40)

    # Sheet 2: Summary Report
    ws_report = workbook.create_sheet("Podsumowanie")
    
    ws_report.append(["PODSUMOWANIE OGÓLNE"])
    ws_report.append(["Suma godzin", "Suma posiłków", "Suma noclegów"])
    ws_report.append([total_hours, total_meals, total_stays])
    
    ws_report.append([])
    ws_report.append(["PODSUMOWANIE WG BUDOWY"])
    ws_report.append(["Kod", "Nazwa", "Godziny", "% Całości", "Posiłki", "Noclegi"])

    # Sort sites by code
    sorted_sites = sorted(site_stats.items(), key=lambda x: x[0][0])
    
    for (code, name), stats in sorted_sites:
        hours = stats["hours"]
        percent = (hours / total_hours * 100) if total_hours > 0 else 0
        ws_report.append([
            code, 
            name, 
            hours, 
            f"{percent:.2f}%", 
            stats["meals"], 
            stats["stays"]
        ])

    ws_report.append([])
    ws_report.append(["PODSUMOWANIE WG OSOBY"])
    ws_report.append(["Osoba", "Dni pracy", "Godziny", "Posiłki", "Noclegi"])

    # Sort workers by name
    sorted_workers = sorted(worker_stats.items(), key=lambda x: x[0])

    for name, stats in sorted_workers:
        ws_report.append([
            name,
            len(stats["dates"]),
            stats["hours"],
            stats["meals"],
            stats["stays"]
        ])

    # Adjust column widths for Report Sheet
    for column_cells in ws_report.columns:
        max_length = max((len(str(cell.value)) if cell.value is not None else 0) for cell in column_cells)
        adjusted_width = max_length + 2
        column_letter = column_cells[0].column_letter
        ws_report.column_dimensions[column_letter].width = min(adjusted_width, 40)

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
