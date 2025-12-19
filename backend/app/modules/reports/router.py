"""Reports API router."""
from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta

from app.core.dependencies import get_db
from .service import ReportGenerator

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/compliance/pdf")
def generate_compliance_report_pdf(
    date_from: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    Generate a comprehensive compliance report in PDF format.
    
    Query Parameters:
    - date_from: Start date (default: 30 days ago)
    - date_to: End date (default: today)
    
    Returns PDF file for download.
    """
    # Parse dates
    df = datetime.strptime(date_from, '%Y-%m-%d') if date_from else datetime.now() - timedelta(days=30)
    dt = datetime.strptime(date_to, '%Y-%m-%d') if date_to else datetime.now()
    
    # Generate report
    pdf_bytes = ReportGenerator.generate_compliance_pdf(db, df, dt)
    
    # Return PDF response
    filename = f"compliance_report_{df.strftime('%Y%m%d')}_{dt.strftime('%Y%m%d')}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.get("/violations/csv")
def export_violations_csv(
    date_from: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    resolved: Optional[bool] = Query(None, description="Filter by resolved status"),
    db: Session = Depends(get_db)
):
    """
    Export violations to CSV format.
    
    Query Parameters:
    - date_from: Start date (default: 30 days ago)
    - date_to: End date (default: today)
    - severity: Filter by severity (critical, high, medium, low)
    - resolved: Filter by resolution status (true/false)
    
    Returns CSV file for download.
    """
    # Parse dates
    df = datetime.strptime(date_from, '%Y-%m-%d') if date_from else datetime.now() - timedelta(days=30)
    dt = datetime.strptime(date_to, '%Y-%m-%d') if date_to else datetime.now()
    
    # Generate CSV
    csv_bytes = ReportGenerator.generate_violations_csv(db, df, dt, severity, resolved)
    
    # Return CSV response
    filename = f"violations_export_{df.strftime('%Y%m%d')}_{dt.strftime('%Y%m%d')}.csv"
    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.get("/violations/excel")
def export_violations_excel(
    date_from: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    resolved: Optional[bool] = Query(None, description="Filter by resolution status"),
    db: Session = Depends(get_db)
):
    """
    Export violations to Excel format.
    
    Query Parameters:
    - date_from: Start date (default: 30 days ago)
    - date_to: End date (default: today)
    - severity: Filter by severity (critical, high, medium, low)
    - resolved: Filter by resolution status (true/false)
    
    Returns Excel file for download.
    """
    # Parse dates
    df = datetime.strptime(date_from, '%Y-%m-%d') if date_from else datetime.now() - timedelta(days=30)
    dt = datetime.strptime(date_to, '%Y-%m-%d') if date_to else datetime.now()
    
    # Generate Excel
    excel_bytes = ReportGenerator.generate_violations_excel(db, df, dt, severity, resolved)
    
    # Return Excel response
    filename = f"violations_export_{df.strftime('%Y%m%d')}_{dt.strftime('%Y%m%d')}.xlsx"
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )
