import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Numeric, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.config.database import Base

class Report(Base):
    """
    Modelo SQLAlchemy que representa la tabla 'reports' de la base de datos Supabase.
    Almacena reportes ciudadanos de canales de drenaje obstruidos enriquecidos por Gemini.
    """
    __tablename__ = "reports"

    # Identificador único de reporte
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4,
        index=True
    )
    
    # Marca de tiempo de creación
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc), 
        nullable=False
    )
    
    # URL pública de la foto en Supabase Storage
    photo_url: Mapped[str] = mapped_column(
        String, 
        nullable=False
    )
    
    # Coordenadas geográficas
    latitude: Mapped[float | None] = mapped_column(
        Numeric(precision=10, scale=8), 
        nullable=True
    )
    longitude: Mapped[float | None] = mapped_column(
        Numeric(precision=11, scale=8), 
        nullable=True
    )
    
    # Estado del reporte: PENDIENTE, LIMPIADO, INVALIDO
    status: Mapped[str] = mapped_column(
        String, 
        default="PENDIENTE", 
        nullable=False,
        index=True
    )
    
    # Análisis de la Inteligencia Artificial (Gemini)
    risk_score: Mapped[int | None] = mapped_column(
        Integer, 
        nullable=True,
        index=True
    )
    category: Mapped[str | None] = mapped_column(
        String, 
        nullable=True
    )
    ai_description: Mapped[str | None] = mapped_column(
        String(80), 
        nullable=True
    )
    
    # Trazabilidad de usuarios
    reported_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), 
        nullable=True
    )
    
    # Cierre de tareas por el operador
    cleaned_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), 
        nullable=True
    )
    cleaned_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), 
        nullable=True
    )

    def __repr__(self) -> str:
        return f"<Report {self.id} | Status: {self.status} | Risk Score: {self.risk_score}>"
