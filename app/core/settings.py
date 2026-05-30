import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Configuración global de la aplicación utilizando Pydantic v2.
    Lee las variables de entorno desde el archivo .env en la raíz del backend.
    """
    # Base de Datos
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/drenacruz"
    
    # Supabase Credentials
    SUPABASE_URL: str = "https://your-supabase-project.supabase.co"
    SUPABASE_ANON_KEY: str = "your-supabase-anon-key"
    
    # Gemini AI
    GEMINI_API_KEY: str = "your-gemini-api-key"
    
    # Configuración del entorno
    ENV: str = "development"
    
    # Configuración de Pydantic Settings
    # En Pydantic v2 se utiliza SettingsConfigDict para configurar el comportamiento de la carga
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Instancia única de la configuración
settings = Settings()
