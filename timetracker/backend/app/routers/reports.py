from datetime import datetime
from io import BytesIO
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from .. import auth, models, schemas
from ..routers.worklogs import _build_user_worklog_query
from ..db import get_db

router = APIRouter(prefix="/reports", tags=["reports"])

from enum import Enum

class ReportType(str, Enum):
    PARTICIPANTS = "participants"
    TEAM_WORK = "team_work"
    ACCOMMODATION = "accommodation"
    CATERING = "catering"

def _generate_excel_from_worklogs(worklogs: list[models.WorkLog], title: str) -> BytesIO:
    from openpyxl import Workbook
    from openpyxl.styles import Font, Border, Side, Alignment

    wb = Workbook()
    ws = wb.active
    ws.title = title

    # Headers
    headers = ["Data", "Pracownik", "Zespół", "Budowa", "Godziny", "Posiłki", "Noclegi"]
    for col_idx, header in enumerate(headers, 1):
        ws.cell(row=1, column=col_idx, value=header).font = Font(bold=True)

    # Data
    for row_idx, log in enumerate(worklogs, 2):
        worker_name = log.team_member.name if log.team_member else (log.user.full_name or log.user.email)
        team_name = log.team_member.team.name if log.team_member and log.team_member.team else (log.user.team.name if log.user.team else "")
        project_code = log.project.code if log.project else ""
        
        date_val = log.date
        if isinstance(date_val, datetime):
            date_val = date_val.replace(tzinfo=None)
        ws.cell(row=row_idx, column=1, value=date_val)
        ws.cell(row=row_idx, column=2, value=worker_name)
        ws.cell(row=row_idx, column=3, value=team_name)
        ws.cell(row=row_idx, column=4, value=project_code)
        ws.cell(row=row_idx, column=5, value=log.hours_worked)
        ws.cell(row=row_idx, column=6, value=log.meals_served)
        ws.cell(row=row_idx, column=7, value=log.overnight_stays)

    # Auto-width
    for column_cells in ws.columns:
        length = max(len(str(cell.value) or "") for cell in column_cells)
        ws.column_dimensions[column_cells[0].column_letter].width = length + 2

    stream = BytesIO()
    wb.save(stream)
    stream.seek(0)
    return stream

@router.get("/export")
async def export_data(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(auth.get_current_active_user)],
    type: ReportType,
    project_id: int | None = None,
    team_id: int | None = None,
    company_id: int | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
):
    from openpyxl import Workbook
    stream = None
    filename = f"raport_{type.value}_{datetime.now().strftime('%Y%m%d')}.xlsx"

    if type == ReportType.PARTICIPANTS:
        if not project_id:
            raise HTTPException(status_code=400, detail="project_id is required for participants export")
            
        # Re-use logic for participants query
        query = (
            db.query(models.WorkLog)
            .options(joinedload(models.WorkLog.team_member), joinedload(models.WorkLog.user))
            .filter(models.WorkLog.project_id == project_id)
        )
        if current_user.role != "admin":
            query = query.filter(models.WorkLog.user_id == current_user.id)
            
        worklogs = query.all()
        names = set()
        for log in worklogs:
            if log.team_member and log.team_member.name:
                names.add(log.team_member.name)
            elif log.user.full_name:
                names.add(log.user.full_name)
            else:
                names.add(log.user.email)
        sorted_names = sorted(list(names))

        wb = Workbook()
        ws = wb.active
        ws.title = "Uczestnicy"
        ws.cell(row=1, column=1, value="Nazwisko i Imię")
        for idx, name in enumerate(sorted_names, 2):
            ws.cell(row=idx, column=1, value=name)
            
        stream = BytesIO()
        wb.save(stream)
        stream.seek(0)

    elif type == ReportType.TEAM_WORK:
        if not team_id:
             raise HTTPException(status_code=400, detail="team_id is required for team_work export")
        
        base_query = _build_user_worklog_query(db, current_user, None, start_date, end_date)
        query = (
            base_query
            .join(models.WorkLog.team_member, isouter=True)
            .join(models.WorkLog.user, isouter=True)
            .filter(
                (models.TeamMember.team_id == team_id) | 
                ((models.WorkLog.team_member_id == None) & (models.User.team_id == team_id))
            )
            .options(joinedload(models.WorkLog.project))
        )
        worklogs = query.all()
        stream = _generate_excel_from_worklogs(worklogs, "Praca Zespołu")

    elif type == ReportType.ACCOMMODATION:
        query = _build_user_worklog_query(db, current_user, None, start_date, end_date)
        query = query.filter(models.WorkLog.overnight_stays > 0).options(joinedload(models.WorkLog.project))
        if company_id:
            query = query.filter(models.WorkLog.accommodation_company_id == company_id)
        worklogs = query.all()
        stream = _generate_excel_from_worklogs(worklogs, "Noclegi")

    elif type == ReportType.CATERING:
        query = _build_user_worklog_query(db, current_user, None, start_date, end_date)
        query = query.filter(models.WorkLog.meals_served > 0).options(joinedload(models.WorkLog.project))
        if company_id:
            query = query.filter(models.WorkLog.catering_company_id == company_id)
        worklogs = query.all()
        stream = _generate_excel_from_worklogs(worklogs, "Posiłki")

    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

def calculate_easter_date(year):
    """Calculate date of Catholic Easter Sunday."""
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return datetime(year, month, day).date()

def get_polish_holidays(year):
    """Return a set of Polish public holidays for a given year."""
    from datetime import timedelta, date
    
    easter = calculate_easter_date(year)
    easter_monday = easter + timedelta(days=1)
    corpus_christi = easter + timedelta(days=60)
    
    fixed_holidays = {
        (1, 1),   # New Year
        (1, 6),   # Epiphany
        (5, 1),   # Labor Day
        (5, 3),   # Constitution Day
        (8, 15),  # Assumption of Mary
        (11, 1),  # All Saints' Day
        (11, 11), # Independence Day
        (12, 25), # Christmas Day
        (12, 26), # Second Day of Christmas
    }
    
    holidays = {date(year, m, d) for m, d in fixed_holidays}
    holidays.add(easter)
    holidays.add(easter_monday)
    holidays.add(corpus_christi)
    
    return holidays

@router.get("/monthly-excel")
async def export_monthly_excel(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(auth.get_current_active_user)],
    year: int = Query(..., description="Year of the report"),
    month: int = Query(..., description="Month of the report"),
    project_id: int | None = Query(default=None, description="Project ID filter"),
):
    # Calculate date range
    try:
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid year or month")
        
    # Query Data using shared logic from worklogs.py
    base_query = _build_user_worklog_query(db, current_user, project_id, start_date, end_date)
    
    query = (
        base_query
        .options(joinedload(models.WorkLog.user).joinedload(models.User.team))
        .options(joinedload(models.WorkLog.team_member).joinedload(models.TeamMember.team))
    )
    
    worklogs = query.all()
    
    # Organize data
    user_data = {}
    
    for log in worklogs:
        if log.team_member_id:
            key = f"tm_{log.team_member_id}"
            worker_name = log.team_member.name
            team_obj = log.team_member.team
            rate = 0.0 
        else:
            key = f"u_{log.user_id}"
            worker_name = log.user.full_name or log.user.email
            team_obj = log.user.team
            rate = log.user.hourly_rate or 0.0

        if key not in user_data:
            user_data[key] = {
                "name": worker_name,
                "team": team_obj,
                "rate": rate,
                "days": {},
                "meals": {},
                "accommodation": {}
            }
        
        day = log.date.day
        if log.absences > 0:
            user_data[key]["days"][day] = log.notes or "Nieobecność"
        else:
            current_val = user_data[key]["days"].get(day, 0)
            if isinstance(current_val, (int, float)):
                user_data[key]["days"][day] = current_val + log.hours_worked
        
        user_data[key]["meals"][day] = user_data[key]["meals"].get(day, 0) + log.meals_served
        user_data[key]["accommodation"][day] = user_data[key]["accommodation"].get(day, 0) + log.overnight_stays

    # Create Workbook In-Memory
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
    from openpyxl.utils import get_column_letter

    wb = Workbook()
    ws = wb.active
    ws.title = "Lista"

    # Set Header (Month/Year) - Cell B1
    polish_months = {
        1: "STYCZEŃ", 2: "LUTY", 3: "MARZEC", 4: "KWIECIEŃ", 5: "MAJ", 6: "CZERWIEC",
        7: "LIPIEC", 8: "SIERPIEŃ", 9: "WRZESIEŃ", 10: "PAŹDZIERNIK", 11: "LISTOPAD", 12: "GRUDZIEŃ"
    }
    month_name = polish_months.get(month, "").upper()
    ws["B1"] = f"{month_name} {year}"
    ws["B1"].font = Font(bold=True, size=14)

    # Styles
    thin_side = Side(style='thin')
    medium_border = Border(left=thin_side, right=thin_side, top=thin_side, bottom=thin_side)
    center_align = Alignment(horizontal='center', vertical='center')
    left_align = Alignment(horizontal='left', vertical='center')

    # Fills
    fill_red = PatternFill(start_color="FFFF0000", end_color="FFFF0000", fill_type="solid")
    fill_yellow = PatternFill(start_color="FFFFFF00", end_color="FFFFFF00", fill_type="solid")
    
    holidays = get_polish_holidays(year)
    day_styles = {}
    
    # Pre-calculate day styles
    for day in range(1, 32):
        try:
            current_date = datetime(year, month, day).date()
            if current_date in holidays or current_date.weekday() == 6: # Sunday
                day_styles[day] = fill_red
            elif current_date.weekday() == 5: # Saturday
                day_styles[day] = fill_yellow
            else:
                day_styles[day] = None
        except ValueError:
             day_styles[day] = None

    # Base Columns (Fixed): Lp, Name, Rate, Buffer (4 cols)
    # Day Columns: 31 days * 3 cols = 93 cols
    # End columns: 4 cols
    
    # HEADERS ROW 1: Days merging
    ws.merge_cells(start_row=1, start_column=1, end_row=2, end_column=1)
    c = ws.cell(row=1, column=1, value="Lp")
    c.border = medium_border
    c.alignment = center_align

    ws.merge_cells(start_row=1, start_column=2, end_row=2, end_column=2)
    c = ws.cell(row=1, column=2, value="Nazwisko i Imię")
    c.border = medium_border
    c.alignment = left_align

    ws.merge_cells(start_row=1, start_column=3, end_row=2, end_column=3)
    ws.merge_cells(start_row=1, start_column=3, end_row=2, end_column=3)
    c = ws.cell(row=1, column=3, value="Liczba dni")
    c.border = medium_border
    c.alignment = center_align

    ws.merge_cells(start_row=1, start_column=4, end_row=2, end_column=4)
    c = ws.cell(row=1, column=4, value="Stawka")
    c.border = medium_border

    # Days Headers
    for day in range(1, 32):
        col_idx = 4 + day # 1=E(5), 31=AI(35)
        c = ws.cell(row=1, column=col_idx, value=day)
        c.border = medium_border
        c.alignment = center_align
        
        # Apply style to the day header
        if day_styles.get(day):
            c.fill = day_styles[day]
        
        # Merge row 1 and 2 for day headers since we don't have sub-headers anymore
        ws.merge_cells(start_row=1, start_column=col_idx, end_row=2, end_column=col_idx)
        
        # Set narrow width
        ws.column_dimensions[get_column_letter(col_idx)].width = 4

    # Summary Headers
    # AJ (36): ILOŚĆ GODZIN
    # AK (37): NALEŻNOŚĆ
    
    # ILOŚĆ GODZIN
    c = ws.cell(row=1, column=36, value="ILOŚĆ GODZIN")
    c.border = medium_border
    c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    ws.column_dimensions["AJ"].width = 10
    ws.merge_cells(start_row=1, start_column=36, end_row=2, end_column=36)
    
    # NALEŻNOŚĆ
    c = ws.cell(row=1, column=37, value="NALEŻNOŚĆ")
    c.border = medium_border
    c.alignment = center_align
    ws.column_dimensions["AK"].width = 12
    ws.merge_cells(start_row=1, start_column=37, end_row=2, end_column=37)
    
    # Payroll Headers - Start at AL (38)
    payroll_headers = [
        "premia (DODATEK GOTÓWKĄ DO WYPŁATY)", "PREMIA PRZELEW", "PŁACA NA KONTO", 
        "Komornik", "PPK", "ubezp. Pak. Med.sport.", 
        "PREMIA LISTA PŁAC GOTÓWKA", "PŁACA GOTÓWKA LISTA", "PREMIA GOTÓWKA", 
        "WYPŁATY DO POKRYCIA", "POTRĄCENIA", "DO WYPŁATY GOTÓWKĄ"
    ]
    payroll_start_col = 38
    for i, header in enumerate(payroll_headers):
        col_idx = payroll_start_col + i
        c = ws.cell(row=1, column=col_idx, value=header)
        c.border = medium_border
        # Wrap text for long headers
        c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        ws.merge_cells(start_row=1, start_column=col_idx, end_row=2, end_column=col_idx)

    users_sorted = sorted(user_data.values(), key=lambda x: (
        (x["team"].name if x["team"] else ""), 
        (x["name"] or "")
    ))
    


    current_row = 3
    for idx, item in enumerate(users_sorted):
        # A: LP
        c = ws.cell(row=current_row, column=1, value=idx + 1)
        c.border = medium_border
        c.alignment = center_align
        
        # B: Name
        c = ws.cell(row=current_row, column=2, value=item["name"])
        c.border = medium_border
        c.alignment = left_align
        
        # C: Working Days
        # Count days where value is number > 0
        working_days = sum(1 for val in item["days"].values() if isinstance(val, (int, float)) and val > 0)
        c = ws.cell(row=current_row, column=3, value=working_days)
        c.border = medium_border
        c.alignment = center_align

        # D: Rate
        c = ws.cell(row=current_row, column=4, value=item["rate"])
        c.border = medium_border

        # Days Data
        for day in range(1, 32):
            col_idx = 4 + day
            
            # Hours / Absence
            if day in item["days"]:
                val = item["days"][day]
                # If it's a string (absence), it will be text. If float/int, it's hours.
                c = ws.cell(row=current_row, column=col_idx, value=val)
            else:
                c = ws.cell(row=current_row, column=col_idx)
                
            c.border = medium_border
            c.alignment = center_align
            if day_styles.get(day): c.fill = day_styles[day]

        # Summary Columns
        # Total Hours = SUM(E3:AI3)
        row_range = f"E{current_row}:AI{current_row}"
        
        # ILOŚĆ GODZIN (AJ / 36)
        # formula_h = f'=SUMPRODUCT((MOD(COLUMN({row_range})-COLUMN($E$2),3)=0)*ISNUMBER({row_range}), {row_range})'
        # Simplified to SUM because we separate columns now. 
        # Excel SUM ignores text, so absences (strings) are safe.
        formula_h = f'=SUM({row_range})'
        c = ws.cell(row=current_row, column=36, value=formula_h)
        c.border = medium_border
        c.alignment = center_align
        
        # NALEŻNOŚĆ (AK / 37)
        # =AJ3 * D3
        formula_pay = f'=AJ{current_row}*D{current_row}'
        c = ws.cell(row=current_row, column=37, value=formula_pay)
        c.border = medium_border
        c.alignment = center_align

        # Payroll Columns (Empty cells with borders)
        payroll_start_col = 38
        for i in range(len(payroll_headers)):
             c = ws.cell(row=current_row, column=payroll_start_col + i)
             c.border = medium_border

        current_row += 1

    # Auto-fit columns
    for column_cells in ws.columns:
        length = max(len(str(cell.value) or "") for cell in column_cells)
        ws.column_dimensions[get_column_letter(column_cells[0].column)].width = length + 2

    # Save to buffer
    stream = BytesIO()
    wb.save(stream)
    stream.seek(0)
    
    filename = f"raport_{year}_{month:02d}.xlsx"
    
    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

@router.get("/participants", response_model=list[str])
async def get_project_participants(
    project_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(auth.get_current_active_user)],
):
    # Query distinct names from worklogs for a project
    # We prioritize TeamMember names, fallback to User names
    # Effectively we want unique names of people who worked on the project
    
    # Using specific query to get distinct names
    query = (
        db.query(models.WorkLog)
        .options(joinedload(models.WorkLog.team_member), joinedload(models.WorkLog.user))
        .filter(models.WorkLog.project_id == project_id)
    )
    
    if current_user.role != "admin":
        # Non-admins restricted to their own logs
        query = query.filter(models.WorkLog.user_id == current_user.id)
        
    worklogs = query.all()
    
    names = set()
    for log in worklogs:
        if log.team_member and log.team_member.name:
            names.add(log.team_member.name)
        elif log.user.full_name:
            names.add(log.user.full_name)
        else:
            names.add(log.user.email)
            
    return sorted(list(names))

@router.get("/team-work", response_model=schemas.PaginatedResponse[schemas.WorkLogRead])
async def get_team_work_report(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(auth.get_current_active_user)],
    team_id: int,
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=50, ge=1, le=100),
):
    # Retrieve logs for a specific team. 
    # Logic: Log associated with a TeamMember of that team OR User of that team
    base_query = _build_user_worklog_query(db, current_user, None, start_date, end_date)
    
    # Join necessary tables to filter by team
    query = (
        base_query
        .join(models.WorkLog.team_member, isouter=True)
        .join(models.WorkLog.user, isouter=True)
        .filter(
            (models.TeamMember.team_id == team_id) | 
            ((models.WorkLog.team_member_id == None) & (models.User.team_id == team_id))
        )
    )
    
    total = query.count()
    pages = (total + size - 1) // size
    items = query.offset((page - 1) * size).limit(size).all()
    
    return schemas.PaginatedResponse(items=items, total=total, page=page, size=size, pages=pages)

@router.get("/accommodation", response_model=schemas.PaginatedResponse[schemas.WorkLogRead])
async def get_accommodation_report(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(auth.get_current_active_user)],
    company_id: int | None = Query(default=None),
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=50, ge=1, le=100),
):
    query = _build_user_worklog_query(db, current_user, None, start_date, end_date)
    
    # Filter for logs with accommodation
    query = query.filter(models.WorkLog.overnight_stays > 0)
    
    if company_id:
        query = query.filter(models.WorkLog.accommodation_company_id == company_id)
        
    total = query.count()
    pages = (total + size - 1) // size
    items = query.offset((page - 1) * size).limit(size).all()
    
    return schemas.PaginatedResponse(items=items, total=total, page=page, size=size, pages=pages)

@router.get("/catering", response_model=schemas.PaginatedResponse[schemas.WorkLogRead])
async def get_catering_report(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(auth.get_current_active_user)],
    company_id: int | None = Query(default=None),
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=50, ge=1, le=100),
):
    query = _build_user_worklog_query(db, current_user, None, start_date, end_date)
    
    # Filter for logs with meals
    query = query.filter(models.WorkLog.meals_served > 0)
    
    if company_id:
        query = query.filter(models.WorkLog.catering_company_id == company_id)
        
    total = query.count()
    pages = (total + size - 1) // size
    items = query.offset((page - 1) * size).limit(size).all()
    
    return schemas.PaginatedResponse(items=items, total=total, page=page, size=size, pages=pages)
