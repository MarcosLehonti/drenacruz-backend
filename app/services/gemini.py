import json
import logging
import httpx
import google.generativeai as genai
from app.core.settings import settings

logger = logging.getLogger(__name__)

# Configurar API de Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)

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
    Descarga la imagen desde Supabase, la envía a Gemini y devuelve el análisis en formato JSON.
    """
    try:
        # 1. Descargar la imagen
        async with httpx.AsyncClient() as client:
            response = await client.get(photo_url)
            response.raise_for_status()
            image_data = response.content
            mime_type = response.headers.get("Content-Type", "image/jpeg")

        # 2. Configurar el modelo (usamos gemini-3.1-flash-lite según requerimiento)
        model = genai.GenerativeModel(
            model_name="gemini-3.1-flash-lite",
            system_instruction=SYSTEM_PROMPT,
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json",
            )
        )

        # 3. Enviar a Gemini
        prompt_parts = [
            {"mime_type": mime_type, "data": image_data},
            "Analiza esta imagen y devuelve el JSON solicitado."
        ]
        
        # Generar contenido
        ai_response = await model.generate_content_async(prompt_parts)
        
        # 4. Parsear el resultado
        result_text = ai_response.text.strip()
        
        # Por seguridad, si el modelo incluye bloques de markdown (ej. ```json ... ```), los limpiamos
        if result_text.startswith("```json"):
            result_text = result_text.replace("```json", "", 1)
            if result_text.endswith("```"):
                result_text = result_text[:-3]
            
        data = json.loads(result_text)
        return data

    except Exception as e:
        logger.error(f"Error analizando imagen con Gemini: {str(e)}")
        # Manejo de error según SRS Sección 10.4
        return {
            "risk_score": 0,
            "category": "error_ia",
            "ai_description": "Fallo en análisis de IA. Requiere revisión humana."
        }
