"""
Herramientas (Tools) que el Agente IA puede ejecutar para consultar datos reales.
Cada función es una "capacidad" que Gemini puede invocar usando Function Calling.
La IA decide cuándo llamar a cada una según la pregunta del operador.
"""
from sqlalchemy.orm import Session
from app.models.report import Report


def get_critical_reports(db: Session, limit: int = 5) -> list[dict]:
    """
    Obtiene los reportes más críticos (risk_score >= 8), los canales en mayor riesgo de inundación.
    La IA usa esta herramienta cuando el operador pregunta por prioridades o urgencias.
    """
    reports = (
        db.query(Report)
        .filter(Report.status == "PENDIENTE", Report.risk_score >= 8)
        .order_by(Report.risk_score.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": str(r.id),
            "risk_score": r.risk_score,
            "category": r.category,
            "ai_description": r.ai_description,
            "latitude": float(r.latitude) if r.latitude else None,
            "longitude": float(r.longitude) if r.longitude else None,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in reports
    ]


def get_summary_stats(db: Session) -> dict:
    """
    Obtiene un resumen estadístico del sistema: total de reportes por estado.
    La IA usa esta herramienta para responder preguntas generales como
    '¿Cuántos reportes hay?' o '¿Cómo está el sistema?'.
    """
    total = db.query(Report).count()
    pending = db.query(Report).filter(Report.status == "PENDIENTE").count()
    cleaned = db.query(Report).filter(Report.status == "LIMPIADO").count()
    invalid = db.query(Report).filter(Report.status == "INVALIDO").count()
    critical = (
        db.query(Report)
        .filter(Report.status == "PENDIENTE", Report.risk_score >= 8)
        .count()
    )
    moderate = (
        db.query(Report)
        .filter(
            Report.status == "PENDIENTE",
            Report.risk_score >= 5,
            Report.risk_score <= 7,
        )
        .count()
    )
    low = (
        db.query(Report)
        .filter(Report.status == "PENDIENTE", Report.risk_score <= 4, Report.risk_score >= 1)
        .count()
    )

    return {
        "total_reportes": total,
        "pendientes": pending,
        "limpiados": cleaned,
        "invalidos": invalid,
        "criticos_riesgo_8_10": critical,
        "moderados_riesgo_5_7": moderate,
        "bajos_riesgo_1_4": low,
    }


def get_report_details(db: Session, report_id: str) -> dict | None:
    """
    Obtiene todos los detalles de un reporte específico por su ID.
    La IA usa esta herramienta cuando el operador pregunta por un canal específico.
    """
    try:
        import uuid
        report = db.query(Report).filter(Report.id == uuid.UUID(report_id)).first()
        if not report:
            return None
        return {
            "id": str(report.id),
            "status": report.status,
            "risk_score": report.risk_score,
            "category": report.category,
            "ai_description": report.ai_description,
            "latitude": float(report.latitude) if report.latitude else None,
            "longitude": float(report.longitude) if report.longitude else None,
            "photo_url": report.photo_url,
            "created_at": report.created_at.isoformat() if report.created_at else None,
            "cleaned_at": report.cleaned_at.isoformat() if report.cleaned_at else None,
        }
    except (ValueError, Exception):
        return None


def get_recent_reports(db: Session, limit: int = 10) -> list[dict]:
    """
    Obtiene los reportes más recientes del sistema.
    La IA usa esta herramienta cuando el operador pregunta por novedades recientes.
    """
    reports = (
        db.query(Report)
        .filter(Report.status == "PENDIENTE")
        .order_by(Report.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": str(r.id),
            "risk_score": r.risk_score,
            "category": r.category,
            "ai_description": r.ai_description,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in reports
    ]
