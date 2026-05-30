from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.settings import settings

# Crear motor de base de datos
# Para PostgreSQL en entornos de producción, es recomendable habilitar pool_pre_ping
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600
)

# Fábrica de sesiones de base de datos
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Clase base declarativa (Estilo SQLAlchemy 2.0)
class Base(DeclarativeBase):
    pass

# Generador de sesiones para Inyección de Dependencias en FastAPI (Dependency Injection)
def get_db():
    """
    Dependency generator that yields a database session.
    Guarantees the session is closed after the request completes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
