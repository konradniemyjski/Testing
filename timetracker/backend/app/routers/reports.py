from datetime import datetime
from io import BytesIO
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from .. import auth, models, schemas
from ..db import get_db

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/monthly-excel")
async def export_monthly_excel(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(auth.get_current_active_user)],
    year: int = Query(..., description="Year of the report"),
    month: int = Query(..., description="Month of the report"),
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
        
    # Query Data
    query = (
        db.query(models.WorkLog)
        .options(joinedload(models.WorkLog.user))
        .filter(models.WorkLog.date >= start_date)
        .filter(models.WorkLog.date < end_date)
    )
    
    worklogs = query.all()
    
    # Organize data by User
    # Map user_id -> { user_obj, days: { day: hours } }
    user_data = {}
    
    for log in worklogs:
        uid = log.user_id
        if uid not in user_data:
            user_data[uid] = {
                "user": log.user,
                "days": {}
            }
        
        day = log.date.day
        # Sum hours if multiple logs per day?
        user_data[uid]["days"][day] = user_data[uid]["days"].get(day, 0) + log.hours_worked

    # Create Workbook In-Memory
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment, Border, Side

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

    # Headers Row 1
    ws.cell(row=1, column=1, value="Lp")
    ws.cell(row=1, column=2, value="Nazwisko i Imię")
    ws.cell(row=1, column=3, value="Stawka")
    ws.cell(row=1, column=4, value="") # Buffer column
    for day in range(1, 32):
        ws.cell(row=1, column=4+day, value=day)
    ws.cell(row=1, column=36, value="Razem") # AJ
    ws.cell(row=1, column=37, value="Kwota") # AK

    # Define Styles
    medium_border = Border(
        left=Side(style='thin'), 
        right=Side(style='thin'), 
        top=Side(style='thin'), 
        bottom=Side(style='thin')
    )
    center_align = Alignment(horizontal='center', vertical='center')
    left_align = Alignment(horizontal='left', vertical='center')

    start_row = 2
    users_sorted = sorted(user_data.values(), key=lambda x: x["user"].full_name or "")
    
    # Fill Data
    for idx, item in enumerate(users_sorted):
        row = start_row + idx
        user = item["user"]
        days = item["days"]
        
        # A: Index
        c = ws.cell(row=row, column=1, value=idx + 1)
        c.border = medium_border
        c.alignment = center_align
        
        # B: Name
        c = ws.cell(row=row, column=2, value=user.full_name or user.email)
        c.border = medium_border
        c.alignment = left_align
        
        # C: Rate
        rate = user.hourly_rate if user.hourly_rate else 0.0
        c = ws.cell(row=row, column=3, value=rate)
        c.border = medium_border
        c.alignment = center_align

        # D: Buffer (Empty)
        c = ws.cell(row=row, column=4, value="")
        c.border = medium_border
        c.alignment = center_align
        
        # E (5) to AI (35): Days 1-31
        for day_curr in range(1, 32):
            col_idx = 4 + day_curr
            val = days.get(day_curr, None)
            c = ws.cell(row=row, column=col_idx, value=val)
            c.border = medium_border
            c.alignment = center_align
        
        # AJ: Hours Sum
        c = ws.cell(row=row, column=36, value=f"=SUM(E{row}:AI{row})")
        c.border = medium_border
        c.alignment = center_align
        
        # AK: Payment
        c = ws.cell(row=row, column=37, value=f"=AJ{row}*C{row}")
        c.border = medium_border
        c.alignment = center_align

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
