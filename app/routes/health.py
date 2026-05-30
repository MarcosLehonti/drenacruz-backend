from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from app.config.database import get_db

router = APIRouter()

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """
    Endpoint de salud del backend de DrenaCruz AI.
    Realiza una consulta SELECT 1 en la base de datos de Supabase para validar la conectividad en tiempo real.
    """
    try:
        # Consulta de ping rápida para validar la conexión con PostgreSQL
        db.execute(text("SELECT 1"))
        return {
            "status": "ok",
            "database": "connected"
        }
    except Exception as e:
        # Si falla la conexión con la base de datos, lanzamos 500
        raise HTTPException(
            status_code=500,
            detail=f"Database connection error: {str(e)}"
        )
