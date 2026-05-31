import uuid
from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.models.report import Report
from app.schemas.report import ReportCreate, ReportResponse, ReportUpdate

router = APIRouter()

@router.get("/reports", response_model=List[ReportResponse])
def get_reports(db: Session = Depends(get_db)):
    """
    Lista todos los reportes, ordenados por 'risk_score' de forma descendente (los más críticos primero).
    Los que no tienen risk_score (None) van al final.
    """
    reports = db.query(Report).order_by(Report.risk_score.desc().nullslast()).all()
    return reports

@router.post("/reports", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
def create_report(report_in: ReportCreate, db: Session = Depends(get_db)):
    """
    Crea un nuevo reporte (Desde Flutter Móvil).
    Se guarda con status='PENDIENTE'. (La IA no se procesa aquí según Fase 3).
    """
    new_report = Report(
        photo_url=report_in.photo_url,
        latitude=report_in.latitude,
        longitude=report_in.longitude,
        reported_by=report_in.reported_by,
        status="PENDIENTE" # Valor asegurado
    )
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    return new_report

@router.get("/reports/{report_id}", response_model=ReportResponse)
def get_report(report_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Obtiene el detalle de un reporte específico por su ID (UUID).
    """
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    return report

@router.patch("/reports/{report_id}/limpiar", response_model=ReportResponse)
def clean_report(report_id: uuid.UUID, update_data: ReportUpdate, db: Session = Depends(get_db)):
    """
    Cambia el estado del reporte a 'LIMPIADO' y registra la fecha de limpieza.
    Se espera recibir el 'cleaned_by' en el body (opcional).
    """
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
        
    report.status = "LIMPIADO"
    report.cleaned_at = datetime.now(timezone.utc)
    if update_data.cleaned_by:
        report.cleaned_by = update_data.cleaned_by
        
    db.commit()
    db.refresh(report)
    return report
