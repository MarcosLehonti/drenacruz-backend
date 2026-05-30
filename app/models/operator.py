import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.config.database import Base


class Operator(Base):
    """
    Modelo SQLAlchemy que representa la tabla 'operators'.

    Almacena información adicional de los operadores municipales
    autorizados para acceder al panel administrativo.
    """

    __tablename__ = "operators"

    # Mismo UUID del usuario en Supabase Auth
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True
    )

    # Nombre completo del funcionario
    full_name: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    # Número de legajo o credencial municipal
    badge_id: Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )

    # Operador activo o deshabilitado
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    # Fecha de creación
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    def __repr__(self) -> str:
        return f"<Operator {self.full_name}>"