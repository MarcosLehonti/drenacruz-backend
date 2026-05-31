"""
Endpoint del Agente IA Conversacional.
Recibe el historial de chat y la nueva pregunta del operador,
orquesta el servicio con Function Calling y devuelve la respuesta.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.services.ai_agent import ejecutar_chat_con_agente

router = APIRouter()


# ============================================================
#  SCHEMAS DE ENTRADA Y SALIDA
# ============================================================

class MensajeHistorial(BaseModel):
    """Representa un mensaje anterior en el historial de la conversación."""
    role: str    # 'user' o 'model'
    content: str


class ChatRequest(BaseModel):
    """
    Cuerpo del request del chat.
    El frontend envía el historial completo + la nueva pregunta.
    """
    pregunta: str
    historial: list[MensajeHistorial] = []


class ChatResponse(BaseModel):
    """Respuesta del agente al frontend."""
    respuesta: str


# ============================================================
#  ENDPOINT PRINCIPAL
# ============================================================

@router.post("/chat", response_model=ChatResponse)
async def chat_con_agente(
    request: ChatRequest,
    db: Session = Depends(get_db),
):
    """
    Endpoint del Agente IA Conversacional.
    
    - Recibe la pregunta del operador y el historial de la conversación.
    - Usa Gemini con Function Calling para consultar datos reales de la BD.
    - Devuelve la respuesta textual del agente.
    """
    if not request.pregunta.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La pregunta no puede estar vacía.",
        )

    historial_serializado = [
        {"role": msg.role, "content": msg.content}
        for msg in request.historial
    ]

    respuesta_agente = await ejecutar_chat_con_agente(
        historial_mensajes=historial_serializado,
        pregunta_usuario=request.pregunta,
        db=db,
    )

    return ChatResponse(respuesta=respuesta_agente)
