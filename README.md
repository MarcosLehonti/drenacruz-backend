# DrenaCruz AI — API & Backend

Este directorio contiene el backend oficial de **DrenaCruz AI**, diseñado en **Python 3.12** utilizando **FastAPI**, **SQLAlchemy 2.0 (ORM)**, **Alembic (Migraciones)** y **Pydantic v2**. 

Está preparado profesionalmente para interactuar con la base de datos de **Supabase (PostgreSQL)** y el motor de IA de **Google Gemini 1.5 Flash**.

---

## 📂 Arquitectura del Proyecto (MVC)

El proyecto sigue una estructura limpia y modular:

*   **`app/core/`**: Configuraciones generales y carga segura de variables de entorno mediante `pydantic-settings`.
*   **`app/config/`**: Configuración de base de datos SQLAlchemy, inicialización de motor de red y generador de sesiones (`get_db`).
*   **`app/models/`**: Definición de entidades ORM SQLAlchemy (ej. `Report`).
*   **`app/schemas/`**: Modelos Pydantic v2 para validación estricta de peticiones de entrada y formatos de respuesta (serialización).
*   **`app/routes/`**: Controladores de endpoints REST (ej. `health.py` montado bajo `/api`).
*   **`app/main.py`**: Punto de entrada de FastAPI, middlewares de CORS y autodocumentación.
*   **`migrations/`**: Historial y scripts de migraciones de base de datos controlados por Alembic.

---

## 🛠️ Requisitos de Instalación (Entorno Local)

Sigue estos pasos para configurar tu entorno en **Windows** (PowerShell):

### 1. Clonar e inicializar el entorno virtual
Desde la carpeta `backend/`:

```powershell
# Crear el entorno virtual
python -m venv venv

# Activar el entorno virtual
.\venv\Scripts\Activate.ps1
```

### 2. Instalar dependencias
Instala los paquetes necesarios definidos en `requirements.txt`:

```powershell
pip install -r requirements.txt
```

### 3. Configurar variables de entorno
Crea tu archivo `.env` copiando el ejemplo:

```powershell
copy .env.example .env
```

Abre el archivo `.env` en tu editor de texto y rellena las credenciales con tu base de datos de Supabase y tu API Key de Gemini:
*   `DATABASE_URL`: URL de conexión directa PostgreSQL (Pooling de Supabase).
*   `SUPABASE_URL` y `SUPABASE_ANON_KEY`: Credenciales del SDK de Supabase.
*   `GEMINI_API_KEY`: API Key de Google AI Studio.

---

## 🔄 Ejecución de Migraciones de Base de Datos (Alembic)

Alembic está preconfigurado para leer la cadena de conexión dinámicamente de tu `.env`. Para aplicar el esquema de la tabla `reports` en Supabase, ejecuta:

```powershell
# Aplicar todas las migraciones pendientes en Supabase
alembic upgrade head
```

*Si realizas cambios en el modelo de SQLAlchemy en `app/models/report.py`, puedes autogenerar una nueva migración ejecutando:*
```powershell
alembic revision --autogenerate -m "nombre_de_los_cambios"
```

---

## 🚀 Iniciar el Servidor de Desarrollo

Una vez configuradas las variables de entorno y aplicadas las migraciones, inicia el servidor local de FastAPI:

```powershell
uvicorn app.main:app --reload
```

El servidor estará corriendo en: **`http://127.0.0.1:8000`**

### Documentación Interactiva
FastAPI autogenera documentación lista para probar. Puedes acceder en tu navegador a:
*   **Swagger UI (Recomendado):** `http://127.0.0.1:8000/docs`
*   **Redoc:** `http://127.0.0.1:8000/redoc`

---

## 🔍 Endpoints Disponibles en el Demo

### GET `/api/health`
Endpoint de diagnóstico técnico. Ejecuta una consulta `SELECT 1` real en tu instancia de Supabase conectada para verificar que las credenciales son 100% correctas.

**Respuesta de éxito (200 OK):**
```json
{
  "status": "ok",
  "database": "connected"
}
```
