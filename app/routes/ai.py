import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.config.database import get_db
from app.models.report import Report
from app.services.gemini import analizar_imagen

router = APIRouter()

class AIAnalyzeRequest(BaseModel):
    report_id: uuid.UUID

class AIAnalyzeResponse(BaseModel):
    report_id: uuid.UUID
    status: str
    risk_score: int | None
    category: str | None
    ai_description: str | None

@router.post("/analizar", response_model=AIAnalyzeResponse)
async def analyze_report_with_ai(request: AIAnalyzeRequest, db: Session = Depends(get_db)):
    """
    Toma un reporte PENDIENTE y envía su imagen a Gemini para clasificar el riesgo.
    """
    # 1. Buscar el reporte en la BD
    report = db.query(Report).filter(Report.id == request.report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
        
    # 3 & 4. Llamar al wrapper de Gemini
    # Como la función de Gemini es async, necesitamos hacer `await`
    ai_result = await analizar_imagen(report.photo_url)
    
    # Extraer resultados
    cat = ai_result.get("category")
    score = ai_result.get("risk_score")
    desc = ai_result.get("ai_description")

    # 5. Lógica de negocio de la Fase 4
    if cat == "no_valido":
        report.status = "INVALIDO"
        report.category = "no_valido"
        report.risk_score = 0
        report.ai_description = desc
    elif cat == "error_ia":
        # 7. Si Gemini falla (nuestro wrapper devuelve "error_ia" en el catch)
        # Dejar risk_score como nulo para revisión manual, mantener PENDIENTE
        report.ai_description = desc
    else:
        # 6. Datos válidos
        # Solo lo marcamos como PENDIENTE u otro estado.
        # El plan dice: Responde a Flutter con status: "ANALIZADO" (solo en la respuesta JSON o en BD?)
        # La BD no tiene estado "ANALIZADO" explícito (solo PENDIENTE, LIMPIADO, INVALIDO según el modelo).
        # Mantendremos status de BD como PENDIENTE, pero en la respuesta podemos mandar el estado del análisis.
        # O podemos simplemente devolver los datos. Actualizamos en BD:
        report.risk_score = score
        report.category = cat
        report.ai_description = desc
        
    db.commit()
    db.refresh(report)
    
    # 8. Responder a Flutter
    # Determinamos el status_str a responder basándonos en lo que pide el plan ("ANALIZADO" o "INVALIDO")
    status_response = "INVALIDO" if cat == "no_valido" else ("ERROR_IA" if cat == "error_ia" else "ANALIZADO")
    
    return AIAnalyzeResponse(
        report_id=report.id,
        status=status_response,
        risk_score=report.risk_score,
        category=report.category,
        ai_description=report.ai_description
    )
