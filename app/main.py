from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.health import router as health_router
from app.core.settings import settings

# Inicialización de la aplicación FastAPI con metadatos descriptivos
app = FastAPI(
    title="DrenaCruz AI — API de Alerta Temprana de Inundaciones",
    description="Backend oficial del sistema DrenaCruz AI. Gestiona reportes de canales obstruidos con triage de IA.",
    version="3.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc" # ReDoc
)

# Configuración de CORS (Cross-Origin Resource Sharing)
# Necesario para que la aplicación Flutter Web y los simuladores móviles puedan consumir la API sin bloqueos
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, restringir a los dominios del frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusión de Routers (Monta los endpoints bajo el prefijo /api)
app.include_router(health_router, prefix="/api", tags=["Salud & Diagnóstico"])

# Endpoint de bienvenida básico
@app.get("/", tags=["General"])
def read_root():
    return {
        "message": "Bienvenido al API de DrenaCruz AI",
        "docs": "/docs",
        "status": "active",
        "version": "3.0.0"
    }
