"""
Wrapper del servicio de análisis de imágenes con Gemini.
Usa el nuevo SDK google-genai para analizar fotos de canales de drenaje.
"""
import json
import logging
import httpx
from google import genai
from google.genai import types

from app.core.settings import settings

logger = logging.getLogger(__name__)

# Cliente único reutilizable del nuevo SDK
_client = genai.Client(api_key=settings.GEMINI_API_KEY)

MODELO_ANALISIS = "gemini-flash-lite-latest"

SYSTEM_PROMPT = """
Eres "DrenaCruz Engine", un experto en ingeniería hidráulica urbana
especializado en gestión de riesgos de inundación para Santa Cruz de la Sierra, Bolivia.

TU MISIÓN ÚNICA: Analizar fotografías de canales de drenaje urbano.

REGLA 1: Si la foto NO muestra un canal -> risk_score: 0, category: "no_valido".
REGLA 2: Categorizar: basura | maleza | sedimento | escombros | despejado.
REGLA 3: Score: 1-3 flujo normal. 4-7 obstrucción parcial. 8-10 riesgo inminente.
REGLA 4: Descripción en español, máximo 80 caracteres, solo hechos objetivos.

FORMATO: Responder ÚNICAMENTE con JSON válido. Sin texto adicional.
"""


async def analizar_imagen(photo_url: str) -> dict:
    """
    Descarga la imagen desde Supabase Storage, la envía a Gemini y
    devuelve el análisis en formato diccionario Python.

    Args:
        photo_url: URL pública de la imagen en Supabase Storage.

    Returns:
        dict con: risk_score (int), category (str), ai_description (str)
    """
    try:
        # 1. Descargar la imagen en memoria (sin guardar en disco)
        async with httpx.AsyncClient(timeout=15.0) as http:
            img_response = await http.get(photo_url)
            img_response.raise_for_status()
            image_bytes = img_response.content
            mime_type = img_response.headers.get("Content-Type", "image/jpeg").split(";")[0]

        # 2. Enviar a Gemini con la imagen inline
        response = await _client.aio.models.generate_content(
            model=MODELO_ANALISIS,
            contents=[
                types.Part(
                    inline_data=types.Blob(mime_type=mime_type, data=image_bytes)
                ),
                types.Part(text="Analiza esta imagen y devuelve el JSON solicitado."),
            ],
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                response_mime_type="application/json",
            ),
        )

        # 3. Parsear el JSON de la respuesta
        result_text = response.text.strip()

        # Limpiar bloques markdown si Gemini los incluyó (por seguridad)
        if result_text.startswith("```"):
            result_text = result_text.split("```")[1]
            if result_text.startswith("json"):
                result_text = result_text[4:]

        return json.loads(result_text)

    except Exception as e:
        logger.error(f"[GeminiService] Error analizando imagen: {str(e)}")
        # Fallback seguro — el reporte se guarda para revisión manual
        return {
            "risk_score": 0,
            "category": "error_ia",
            "ai_description": "Fallo en análisis de IA. Requiere revisión humana.",
        }
