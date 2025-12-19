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
    
    # Global Aggregators for Summary Sheet
    acc_global_summary = {} # Name -> count
    cat_global_summary = {} # Name -> count
    proj_global_summary = {} # Project Name -> {"meals": 0, "acc": 0}
    
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
                "days": {},         # day_int: hours (accumulated) or absence_note
                "projects": {},     # day_int: "Code Name"
                "meals_count": {},  # day_int: count
                "meals_info": {},   # day_int: "Company Name"
                "acc_count": {},    # day_int: count
                "acc_info": {},     # day_int: "Company Name"
            }
        
        day = log.date.day
        if log.absences > 0:
            user_data[key]["days"][day] = log.notes or "Nieobecność"
        else:
            current_val = user_data[key]["days"].get(day, 0)
            if isinstance(current_val, (int, float)):
                user_data[key]["days"][day] = current_val + log.hours_worked
        
        if log.project:
            proj_name = f"{log.project.code} {log.project.name}"
            # Init project summary if new
            if proj_name not in proj_global_summary:
                proj_global_summary[proj_name] = {"meals": 0, "acc": 0}

        # Project Info
        if log.project:
            proj_str = f"{log.project.code} {log.project.name}"
            # Keep existing if multiple, or overwrite? Overwrite for now as per layout.
            user_data[key]["projects"][day] = proj_str

        # Meals
        if log.meals_served > 0:
            user_data[key]["meals_count"][day] = user_data[key]["meals_count"].get(day, 0) + log.meals_served
            name = log.catering_company.name if log.catering_company else "Tak"
            user_data[key]["meals_info"][day] = name
            
            # Global Aggregation
            cat_global_summary[name] = cat_global_summary.get(name, 0) + log.meals_served
            if log.project:
                proj_global_summary[proj_name]["meals"] += log.meals_served

        # Accommodation
        if log.overnight_stays > 0:
            user_data[key]["acc_count"][day] = user_data[key]["acc_count"].get(day, 0) + log.overnight_stays
            name = log.accommodation_company.name if log.accommodation_company else "Tak"
            user_data[key]["acc_info"][day] = name
            
            # Global Aggregation
            acc_global_summary[name] = acc_global_summary.get(name, 0) + log.overnight_stays
            if log.project:
                proj_global_summary[proj_name]["acc"] += log.overnight_stays

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
    fill_gray = PatternFill(start_color="F2F2F2", end_color="F2F2F2", fill_type="solid")
    
    holidays = get_polish_holidays(year)
    day_styles = {}
    
    # Pre-calculate day styles and count working days
    total_working_days = 0
    for day in range(1, 32):
        try:
            current_date = datetime(year, month, day).date()
            if current_date in holidays or current_date.weekday() == 6: # Sunday
                day_styles[day] = fill_red
            elif current_date.weekday() == 5: # Saturday
                day_styles[day] = fill_yellow
            else:
                day_styles[day] = None
                total_working_days += 1
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

    # Days Headers: 2 Columns Per Day
    for day in range(1, 32):
        start_col = 5 + (day - 1) * 2  # E is 5. 2 cols per day.
        # Merge 2 cells for the day number
        ws.merge_cells(start_row=1, start_column=start_col, end_row=1, end_column=start_col + 1)
        c = ws.cell(row=1, column=start_col, value=day)
        c.border = medium_border
        c.alignment = center_align
        
        # Apply style to the day header
        if day_styles.get(day):
            for i in range(2):
                cell = ws.cell(row=1, column=start_col + i)
                cell.fill = day_styles[day]
                cell.border = medium_border

        # Sub-headers in Row 2: "G,P,N" | Empty
        # Col 1
        c = ws.cell(row=2, column=start_col, value="G,P,N")
        c.border = medium_border
        c.alignment = center_align
        if day_styles.get(day): c.fill = day_styles[day]
        
        # Col 2
        c = ws.cell(row=2, column=start_col + 1, value="")
        c.border = medium_border
        c.alignment = center_align
        if day_styles.get(day): c.fill = day_styles[day]

    # Summary Headers (After day 31 * 2 cols)
    # Start: 5. Width: 31*2 = 62. End: 5+62=67 (CO)
    summary_start_col = 5 + (31 * 2)
    
    # ILOŚĆ GODZIN
    c = ws.cell(row=1, column=summary_start_col, value="ILOŚĆ GODZIN")
    c.border = medium_border
    c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    ws.column_dimensions[get_column_letter(summary_start_col)].width = 10
    ws.merge_cells(start_row=1, start_column=summary_start_col, end_row=2, end_column=summary_start_col)
    
    # Razem Posiłki
    c = ws.cell(row=1, column=summary_start_col + 1, value="Posiłki")
    c.border = medium_border
    c.alignment = center_align
    ws.merge_cells(start_row=1, start_column=summary_start_col + 1, end_row=2, end_column=summary_start_col + 1)

    # Razem Noclegi
    c = ws.cell(row=1, column=summary_start_col + 2, value="Noclegi")
    c.border = medium_border
    c.alignment = center_align
    ws.merge_cells(start_row=1, start_column=summary_start_col + 2, end_row=2, end_column=summary_start_col + 2)

    # NALEŻNOŚĆ
    c = ws.cell(row=1, column=summary_start_col + 3, value="NALEŻNOŚĆ")
    c.border = medium_border
    c.alignment = center_align
    ws.column_dimensions[get_column_letter(summary_start_col + 3)].width = 12
    ws.merge_cells(start_row=1, start_column=summary_start_col + 3, end_row=2, end_column=summary_start_col + 3)
    
    # Payroll Headers - Append after Summary
    payroll_headers = [
        "premia (DODATEK GOTÓWKĄ DO WYPŁATY)", "PREMIA PRZELEW", "PŁACA NA KONTO", 
        "Komornik", "PPK", "ubezp. Pak. Med.sport.", 
        "PREMIA LISTA PŁAC GOTÓWKA", "PŁACA GOTÓWKA LISTA", "PREMIA GOTÓWKA", 
        "WYPŁATY DO POKRYCIA", "POTRĄCENIA", "DO WYPŁATY GOTÓWKĄ"
    ]
    payroll_start_col = summary_start_col + 4
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
        is_gray = (idx % 2 == 1)
        base_fill = fill_gray if is_gray else None
        
        # Merge columns A, B, C, D vertically for the 3 rows
        for col_idx in range(1, 5):
            ws.merge_cells(start_row=current_row, start_column=col_idx, end_row=current_row + 2, end_column=col_idx)
            # Apply border to merged range
            for r in range(current_row, current_row + 3):
                c = ws.cell(row=r, column=col_idx)
                c.border = medium_border
                c.alignment = center_align if col_idx != 2 else left_align
                if base_fill: c.fill = base_fill

        # A: Lp
        c = ws.cell(row=current_row, column=1, value=idx + 1)
        
        # B: Name
        c = ws.cell(row=current_row, column=2, value=item["name"])

        # C: Working Days (Total in month)
        c = ws.cell(row=current_row, column=3, value=total_working_days)

        # D: Rate
        c = ws.cell(row=current_row, column=4, value=item["rate"])

        # Data Rows
        # Row 1: Work (Hours | Project)
        # Row 2: Meals (Count | Company)
        # Row 3: Acc (Count | Company)
        
        for day in range(1, 32):
            start_col = 5 + (day - 1) * 2
            
            # Determine fill for this day: Priority: Weekend/Holiday -> Gray -> None
            day_fill = day_styles.get(day) or base_fill
            
            # --- ROW 1 (Work) ---
            # Col 1: Hours
            val = item["days"].get(day, 0)
            c = ws.cell(row=current_row, column=start_col, value=val)
            c.border = medium_border
            c.alignment = center_align
            if day_fill: c.fill = day_fill
            
            # Col 2: Project
            val_proj = item["projects"].get(day, None)
            c = ws.cell(row=current_row, column=start_col + 1, value=val_proj)
            c.border = medium_border
            c.alignment = center_align
            if day_fill: c.fill = day_fill

            # --- ROW 2 (Meals) ---
            # Col 1: Count
            val_mc = item["meals_count"].get(day, 0)
            c = ws.cell(row=current_row + 1, column=start_col, value=val_mc)
            c.border = medium_border
            c.alignment = center_align
            if day_fill: c.fill = day_fill
            
            # Col 2: Company
            val_mn = item["meals_info"].get(day, None)
            c = ws.cell(row=current_row + 1, column=start_col + 1, value=val_mn)
            c.border = medium_border
            c.alignment = center_align
            if day_fill: c.fill = day_fill

            # --- ROW 3 (Accom) ---
            # Col 1: Count
            val_ac = item["acc_count"].get(day, 0)
            c = ws.cell(row=current_row + 2, column=start_col, value=val_ac)
            c.border = medium_border
            c.alignment = center_align
            if day_fill: c.fill = day_fill
            
            # Col 2: Company
            val_an = item["acc_info"].get(day, None)
            c = ws.cell(row=current_row + 2, column=start_col + 1, value=val_an)
            c.border = medium_border
            c.alignment = center_align
            if day_fill: c.fill = day_fill


        # Summary Columns
        last_day_col_letter = get_column_letter(summary_start_col - 1)
        
        # Merge Summary and Payroll headers for the 3 rows as well?
        # Usually summary is single cell. Merge them vertically.
        for i in range(4): # 4 summary columns
            col_idx = summary_start_col + i
            ws.merge_cells(start_row=current_row, start_column=col_idx, end_row=current_row + 2, end_column=col_idx)
            for r in range(current_row, current_row + 3):
                c = ws.cell(row=r, column=col_idx)
                c.border = medium_border
                c.alignment = center_align
                if base_fill: c.fill = base_fill

        # Formula Range: Covers all day columns (Value & Description)
        # We need to sum only every other column (Value columns: E, G, I...)
        # Value columns are offsets 0, 2, 4 from E (5).
        # MOD(COLUMN - 5, 2) == 0
        
        row_range_1 = f"$E{current_row}:${last_day_col_letter}{current_row}" # Row 1 range
        row_range_2 = f"$E{current_row + 1}:${last_day_col_letter}{current_row + 1}" # Row 2 range
        row_range_3 = f"$E{current_row + 2}:${last_day_col_letter}{current_row + 2}" # Row 3 range

        # ILOŚĆ GODZIN (Row 1 sum of value cols)
        # ISNUMBER checks if it's a number (ignores project strings in adjacent cols if range was contiguous, 
        # but here we use MOD to be safe and target only Value columns).
        formula_h = f'=SUMPRODUCT((MOD(COLUMN({row_range_1})-COLUMN($E$2),2)=0)*ISNUMBER({row_range_1}), {row_range_1})'
        c = ws.cell(row=current_row, column=summary_start_col, value=formula_h)

        # Total Meals (Row 2 sum of value cols: Counts)
        formula_p = f'=SUMPRODUCT((MOD(COLUMN({row_range_2})-COLUMN($E$2),2)=0)*ISNUMBER({row_range_2}), {row_range_2})'
        c = ws.cell(row=current_row, column=summary_start_col + 1, value=formula_p)

        # Total Accommodation (Row 3 sum of value cols: Counts)
        formula_n = f'=SUMPRODUCT((MOD(COLUMN({row_range_3})-COLUMN($E$2),2)=0)*ISNUMBER({row_range_3}), {row_range_3})'
        c = ws.cell(row=current_row, column=summary_start_col + 2, value=formula_n)
        
        # NALEŻNOŚĆ
        # =TotalHours * Rate (D)
        total_hours_col_letter = get_column_letter(summary_start_col)
        # Rate is in D{current_row} (merged)
        formula_pay = f'={total_hours_col_letter}{current_row}*D{current_row}'
        c = ws.cell(row=current_row, column=summary_start_col + 3, value=formula_pay)

        # Payroll Columns (Empty cells with borders)
        payroll_start_col = summary_start_col + 4
        for i in range(len(payroll_headers)):
             col_idx = payroll_start_col + i
             ws.merge_cells(start_row=current_row, start_column=col_idx, end_row=current_row + 2, end_column=col_idx)
             for r in range(current_row, current_row + 3):
                 c = ws.cell(row=r, column=col_idx)
                 c.border = medium_border
                 if base_fill: c.fill = base_fill

        current_row += 3

    # Auto-fit columns for Main Sheet
    for column_cells in ws.columns:
        length = max(len(str(cell.value) or "") for cell in column_cells)
        ws.column_dimensions[get_column_letter(column_cells[0].column)].width = length + 2

    # --- SUMMARY SHEET ("Podsumowanie") ---
    ws_summary = wb.create_sheet("Podsumowanie")
    
    # helper for borders
    def set_border(cell):
        cell.border = medium_border
        cell.alignment = center_align

    # 1. Catering Summary
    row_idx = 2
    ws_summary.cell(row=row_idx, column=2, value="PODSUMOWANIE POSIŁKÓW").font = Font(bold=True)
    row_idx += 1
    
    ws_summary.cell(row=row_idx, column=2, value="Firma")
    set_border(ws_summary.cell(row=row_idx, column=2))
    ws_summary.cell(row=row_idx, column=3, value="Ilość")
    set_border(ws_summary.cell(row=row_idx, column=3))
    row_idx += 1
    
    total_meals = 0
    for company, count in cat_global_summary.items():
        ws_summary.cell(row=row_idx, column=2, value=company or "Brak firmy")
        set_border(ws_summary.cell(row=row_idx, column=2))
        
        ws_summary.cell(row=row_idx, column=3, value=count)
        set_border(ws_summary.cell(row=row_idx, column=3))
        total_meals += count
        row_idx += 1
        
    # Total row for catering
    ws_summary.cell(row=row_idx, column=2, value="RAZEM").font = Font(bold=True)
    set_border(ws_summary.cell(row=row_idx, column=2))
    ws_summary.cell(row=row_idx, column=3, value=total_meals).font = Font(bold=True)
    set_border(ws_summary.cell(row=row_idx, column=3))
    
    row_idx += 3 # Gap
    
    # 2. Accommodation Summary
    ws_summary.cell(row=row_idx, column=2, value="PODSUMOWANIE NOCLEGÓW").font = Font(bold=True)
    row_idx += 1
    
    ws_summary.cell(row=row_idx, column=2, value="Firma")
    set_border(ws_summary.cell(row=row_idx, column=2))
    ws_summary.cell(row=row_idx, column=3, value="Ilość")
    set_border(ws_summary.cell(row=row_idx, column=3))
    row_idx += 1
    
    total_acc = 0
    for company, count in acc_global_summary.items():
        ws_summary.cell(row=row_idx, column=2, value=company or "Brak firmy")
        set_border(ws_summary.cell(row=row_idx, column=2))
        
        ws_summary.cell(row=row_idx, column=3, value=count)
        set_border(ws_summary.cell(row=row_idx, column=3))
        total_acc += count
        row_idx += 1

    # Total row for accommodation
    ws_summary.cell(row=row_idx, column=2, value="RAZEM").font = Font(bold=True)
    set_border(ws_summary.cell(row=row_idx, column=2))
    ws_summary.cell(row=row_idx, column=3, value=total_acc).font = Font(bold=True)
    set_border(ws_summary.cell(row=row_idx, column=3))

    row_idx += 3 # Gap

    # 3. Project Summary
    ws_summary.cell(row=row_idx, column=2, value="PODSUMOWANIE PROJEKTÓW").font = Font(bold=True)
    row_idx += 1
    
    headers = ["Projekt", "Posiłki", "Noclegi"]
    for i, h in enumerate(headers):
        c = ws_summary.cell(row=row_idx, column=2+i, value=h)
        set_border(c)
        c.font = Font(bold=True)
    row_idx += 1
    
    for proj_name, data in proj_global_summary.items():
        c = ws_summary.cell(row=row_idx, column=2, value=proj_name)
        set_border(c)
        
        c = ws_summary.cell(row=row_idx, column=3, value=data["meals"])
        set_border(c)
        
        c = ws_summary.cell(row=row_idx, column=4, value=data["acc"])
        set_border(c)
        
        row_idx += 1

    # Auto-fit columns for Summary Sheet
    for column_cells in ws_summary.columns:
        length = max(len(str(cell.value) or "") for cell in column_cells)
        ws_summary.column_dimensions[get_column_letter(column_cells[0].column)].width = length + 2

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
