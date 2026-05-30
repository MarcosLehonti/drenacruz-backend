import uuid
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional

class ReportBase(BaseModel):
    """
    Schema base con atributos comunes de un Reporte.
    """
    photo_url: str = Field(..., description="URL pública de la foto en Supabase Storage")
    latitude: Optional[float] = Field(None, description="Latitud GPS", ge=-90, le=90)
    longitude: Optional[float] = Field(None, description="Longitud GPS", ge=-180, le=180)
    status: str = Field("PENDIENTE", description="Estado del reporte (PENDIENTE, LIMPIADO, INVALIDO)")
    risk_score: Optional[int] = Field(None, description="Puntuación de riesgo calculada por Gemini (0-10)", ge=0, le=10)
    category: Optional[str] = Field(None, description="Categoría de obstrucción detectada")
    ai_description: Optional[str] = Field(None, max_length=80, description="Descripción corta de la IA (máx 80 caracteres)")
    reported_by: Optional[uuid.UUID] = Field(None, description="ID del usuario anónimo que reportó")

class ReportCreate(BaseModel):
    """
    Schema para validar la creación de un nuevo reporte por parte de un ciudadano.
    Sólo requiere la foto y coordenadas opcionales.
    """
    photo_url: str = Field(..., description="URL pública de la foto en el storage de Supabase")
    latitude: Optional[float] = Field(None, description="Latitud GPS del dispositivo", ge=-90, le=90)
    longitude: Optional[float] = Field(None, description="Longitud GPS del dispositivo", ge=-180, le=180)
    reported_by: Optional[uuid.UUID] = Field(None, description="ID opcional del ciudadano (anónimo)")

class ReportUpdate(BaseModel):
    """
    Schema para actualizar un reporte existente (por ejemplo, cuando la IA lo enriquece o cuando se limpia).
    """
    status: Optional[str] = Field(None, description="Cambiar estado: PENDIENTE, LIMPIADO, INVALIDO")
    risk_score: Optional[int] = Field(None, ge=0, le=10)
    category: Optional[str] = Field(None)
    ai_description: Optional[str] = Field(None, max_length=80)
    cleaned_by: Optional[uuid.UUID] = Field(None, description="ID del operador que cierra la tarea")

class ReportResponse(ReportBase):
    """
    Schema de respuesta que incluye campos automáticos generados por el servidor o base de datos.
    """
    id: uuid.UUID
    created_at: datetime
    cleaned_at: Optional[datetime] = None
    cleaned_by: Optional[uuid.UUID] = None

    class Config:
        # En Pydantic v2 se usa from_attributes en lugar de orm_mode para compatibilidad ORM
        from_attributes = True
