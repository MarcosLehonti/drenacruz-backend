"""
Servicio del Agente IA Conversacional para operadores municipales.
Usa el nuevo SDK google-genai con Function Calling para consultar
datos reales de la BD y responder preguntas del administrador.
"""
import json
import logging
from google import genai
from google.genai import types

from app.core.settings import settings

logger = logging.getLogger(__name__)

# Cliente único del nuevo SDK
_client = genai.Client(api_key=settings.GEMINI_API_KEY)

# Modelo disponible en Google AI Studio
MODELO_AGENTE = "gemini-3.1-flash-lite"

# ============================================================
#  DEFINICIÓN DE HERRAMIENTAS (Function Declarations)
#  Gemini las recibe como Python callables con docstrings.
#  La firma y el docstring son suficientes para que Gemini
#  entienda cuándo y cómo invocar cada herramienta.
# ============================================================

def get_critical_reports(limit: int = 5) -> str:
    """
    Obtiene los reportes de canales más críticos del sistema con riesgo alto (8-10).
    Úsala cuando el operador pregunte qué canales atender primero, cuáles son los más
    urgentes, las prioridades del día, o situaciones de riesgo inminente.

    Args:
        limit: Cuántos reportes críticos retornar. Por defecto 5.

    Returns:
        JSON con los reportes críticos ordenados por riesgo descendente.
    """
    # Implementación real se inyecta en el dispatcher en tiempo de ejecución
    pass


def get_summary_stats() -> str:
    """
    Obtiene estadísticas generales del sistema: total de reportes, cuántos están
    pendientes, limpiados, inválidos, y el desglose por nivel de riesgo
    (crítico 8-10, moderado 5-7, bajo 1-4).
    Úsala cuando el operador pregunte por el estado general del sistema.

    Returns:
        JSON con el resumen estadístico del sistema.
    """
    pass


def get_recent_reports(limit: int = 10) -> str:
    """
    Obtiene los reportes pendientes más recientes del sistema.
    Úsala cuando el operador pregunte por novedades, reportes nuevos,
    o qué llegó recientemente.

    Args:
        limit: Cuántos reportes recientes retornar. Por defecto 10.

    Returns:
        JSON con los reportes más recientes ordenados por fecha descendente.
    """
    pass


def get_report_details(report_id: str) -> str:
    """
    Obtiene todos los detalles de un reporte específico dado su ID UUID.
    Úsala solo si el operador menciona un ID concreto de reporte.

    Args:
        report_id: El UUID del reporte a consultar.

    Returns:
        JSON con todos los campos del reporte, o null si no existe.
    """
    pass


HERRAMIENTAS_AGENTE = [
    get_critical_reports,
    get_summary_stats,
    get_recent_reports,
    get_report_details,
]

SYSTEM_PROMPT_AGENTE = """
Eres "DrenaCruz Agente", el asistente inteligente del Sistema de Alerta Temprana de Inundaciones
para Santa Cruz de la Sierra, Bolivia. Estás hablando con un OPERADOR MUNICIPAL que gestiona
cuadrillas de limpieza de canales de drenaje.

TU MISIÓN: Ayudar al operador a tomar decisiones rápidas y bien informadas sobre qué canales
atender, basándote siempre en datos reales del sistema.

REGLAS DE COMPORTAMIENTO:
1. SIEMPRE usa tus herramientas para obtener datos reales antes de responder sobre canales o estadísticas.
2. Responde en español, de forma clara y directa. Eres un asistente profesional, no un chatbot genérico.
3. Usa formato Markdown: **negritas** para resaltar, listas para enumeraciones, tablas si hay muchos datos.
4. El sistema de semáforo de riesgo es: 🔴 Crítico (8-10), 🟡 Moderado (5-7), 🟢 Bajo (1-4).
5. Si el operador saluda o hace preguntas generales, responde amablemente pero recuérdale que puedes
   consultar datos reales del sistema de drenaje.
6. Si el operador pregunta algo que no está en tus herramientas, responde con lo que sabes sobre gestión
   de canales de drenaje urbano. Nunca inventes datos del sistema.
7. Sé conciso. El operador está en campo o bajo presión. Ve directo al punto.
"""


async def ejecutar_chat_con_agente(
    historial_mensajes: list[dict],
    pregunta_usuario: str,
    db,  # Session de SQLAlchemy inyectada desde el endpoint
) -> str:
    """
    Ejecuta una conversación con el Agente IA usando Function Calling del nuevo SDK.

    Flujo:
    1. Envía la pregunta + historial a Gemini con las herramientas disponibles.
    2. Si Gemini decide usar una herramienta, la ejecutamos con datos reales de la BD.
    3. Devolvemos el resultado a Gemini para que redacte la respuesta final.

    Args:
        historial_mensajes: Lista de {'role': 'user'|'model', 'content': texto}
        pregunta_usuario: El último mensaje del operador.
        db: La sesión de base de datos para ejecutar las consultas.

    Returns:
        La respuesta textual del agente en Markdown.
    """
    from app.services.ai_chat_tools import (
        get_critical_reports as _get_critical_reports,
        get_summary_stats as _get_summary_stats,
        get_recent_reports as _get_recent_reports,
        get_report_details as _get_report_details,
    )

    # Dispatcher: mapea nombre de función → implementación real con DB
    dispatcher = {
        "get_critical_reports": lambda args: _get_critical_reports(db, **args),
        "get_summary_stats":    lambda args: _get_summary_stats(db),
        "get_recent_reports":   lambda args: _get_recent_reports(db, **args),
        "get_report_details":   lambda args: _get_report_details(db, **args),
    }

    try:
        # Construir el historial en el formato del nuevo SDK
        historial_genai = []
        for msg in historial_mensajes:
            role = "user" if msg["role"] == "user" else "model"
            historial_genai.append(
                types.Content(role=role, parts=[types.Part(text=msg["content"])])
            )

        # Añadir el nuevo mensaje del usuario al historial
        historial_genai.append(
            types.Content(role="user", parts=[types.Part(text=pregunta_usuario)])
        )

        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT_AGENTE,
            tools=HERRAMIENTAS_AGENTE,
        )

        # Bucle de Function Calling: máximo 5 iteraciones de herramientas
        max_iteraciones = 5
        for _ in range(max_iteraciones):
            response = await _client.aio.models.generate_content(
                model=MODELO_AGENTE,
                contents=historial_genai,
                config=config,
            )

            # Verificar si Gemini quiere ejecutar alguna herramienta
            tiene_tool_call = any(
                part.function_call is not None
                for candidate in response.candidates
                for part in candidate.content.parts
                if hasattr(part, "function_call")
            )

            if not tiene_tool_call:
                # Gemini tiene su respuesta final — salir del bucle
                break

            # Añadir la respuesta del modelo (con tool calls) al historial
            historial_genai.append(response.candidates[0].content)

            # Ejecutar todas las herramientas solicitadas y recoger resultados
            parts_resultado = []
            for part in response.candidates[0].content.parts:
                if part.function_call is None:
                    continue

                nombre_fn = part.function_call.name
                args = dict(part.function_call.args) if part.function_call.args else {}

                logger.info(f"[AgenteIA] Ejecutando herramienta: {nombre_fn}({args})")

                if nombre_fn in dispatcher:
                    resultado = dispatcher[nombre_fn](args)
                else:
                    resultado = {"error": f"Herramienta '{nombre_fn}' no encontrada"}

                resultado_json = json.dumps(resultado, ensure_ascii=False, default=str)

                parts_resultado.append(
                    types.Part(
                        function_response=types.FunctionResponse(
                            name=nombre_fn,
                            response={"result": resultado_json},
                        )
                    )
                )

            # Devolver los resultados al modelo para que redacte la respuesta
            historial_genai.append(
                types.Content(role="user", parts=parts_resultado)
            )

        # Extraer el texto final
        texto_final = response.text if hasattr(response, "text") and response.text else \
            "Lo siento, no pude procesar tu consulta en este momento."

        return texto_final

    except Exception as e:
        logger.error(f"[AgenteIA] Error inesperado: {str(e)}")
        return (
            "⚠️ Ocurrió un error al procesar tu consulta. "
            "Por favor, intenta nuevamente en unos segundos."
        )
