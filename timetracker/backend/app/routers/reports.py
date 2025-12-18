from datetime import datetime
from io import BytesIO
from typing import Annotated
import os

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

from .. import auth, models, schemas
from ..db import get_db

router = APIRouter(prefix="/reports", tags=["reports"])

def get_template_path():
    # Try multiple locations
    possible_paths = [
        "backend/templates/lista.xlsx",
        "templates/lista.xlsx",
        "../lista.xlsx",
        "/home/konrad/Dokumenty/Testing/timetracker/backend/templates/lista.xlsx"
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    # Fallback to absolute check based on app root if possible
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__))) # should be app root
    path = os.path.join(base_dir, "templates", "lista.xlsx")
    if os.path.exists(path):
        return path
    raise FileNotFoundError("Could not find lista.xlsx template")

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

    # Load Template
    try:
        template_path = get_template_path()
        wb = load_workbook(template_path)
        ws = wb.active
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading template: {str(e)}")

    # Update Sheet Header (Month/Year) - Cell B1 based on inspection
    # B1 was "MARZEC 2025" in example
    polish_months = {
        1: "STYCZEŃ", 2: "LUTY", 3: "MARZEC", 4: "KWIECIEŃ", 5: "MAJ", 6: "CZERWIEC",
        7: "LIPIEC", 8: "SIERPIEŃ", 9: "WRZESIEŃ", 10: "PAŹDZIERNIK", 11: "LISTOPAD", 12: "GRUDZIEŃ"
    }
    month_name = polish_months.get(month, "").upper()
    ws["B1"] = f"{month_name} {year}"

    # Row 2 is the template row with formulas. We will retain it for the first user, 
    # and copy it for subsequent users.
    # Start filling from Row 2.
    
    start_row = 2
    users_sorted = sorted(user_data.values(), key=lambda x: x["user"].full_name or "")
    
    # If no users, return empty?
    if not users_sorted:
         # Just return template
         pass
    else:
        # We need to duplicate styles and formulas for row 2 to N
        # OpenPyXL copying rows is manual.
        # But wait, if there are multiple users, we populate row 2, then row 3, etc.
        # Ideally we iterate.
        
        for idx, item in enumerate(users_sorted):
            row = start_row + idx
            user = item["user"]
            days = item["days"]
            
            # A: Index
            ws.cell(row=row, column=1, value=idx + 1)
            
            # B: Name
            ws.cell(row=row, column=2, value=user.full_name or user.email)
            
            # C: Rate
            rate = user.hourly_rate if user.hourly_rate else 0.0
            ws.cell(row=row, column=3, value=rate)
            
            # E (5) to AI (35): Days 1-31
            for day_curr in range(1, 32):
                col_idx = 4 + day_curr # E is 5. 5 = 4 + 1. Correct.
                val = days.get(day_curr, None)
                if val is not None:
                     ws.cell(row=row, column=col_idx, value=val)
            
            # AJ: Hours Sum
            # If we write raw value, we lose dynamic calculation if they edit it manually later.
            # Ideally write formula.
            # Template row 2 has =SUM(E2:AI2)
            # We construct formula: =SUM(E{row}:AI{row})
            ws.cell(row=row, column=36, value=f"=SUM(E{row}:AI{row})")
            
            # AK: Payment
            # Template row 2 has =AJ2*C2
            # Formula: =AJ{row}*C{row}
            ws.cell(row=row, column=37, value=f"=AJ{row}*C{row}")
            
            # Styles: Copy styles from Row 2 if row > 2
            if row > 2:
                for col in range(1, 38):
                    source_cell = ws.cell(row=2, column=col)
                    target_cell = ws.cell(row=row, column=col)
                    if source_cell.has_style:
                        target_cell.font = source_cell.font.copy()
                        target_cell.border = source_cell.border.copy()
                        target_cell.fill = source_cell.fill.copy()
                        target_cell.number_format = source_cell.number_format
                        target_cell.alignment = source_cell.alignment.copy()

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
