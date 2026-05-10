"""
Módulo 1: Agente LLM Vulnerable.

Implementa un chatbot de atención al cliente SIN ninguna capa de
protección externa.  Demuestra cómo un agente con información
sensible incrustada en su System Prompt puede ser explotado
mediante técnicas de Prompt Injection (OWASP LLM01, LLM02, LLM07).

Dependencias:
    - google-genai >= 1.0
    - tenacity
"""

import time

from google import genai
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from config import (
    GOOGLE_API_KEY,
    LLM_MODEL,
    LLM_TEMPERATURE,
    MAX_RETRIES,
    REQUEST_DELAY_SECONDS,
    VULNERABLE_SYSTEM_PROMPT,
)

# ---------------------------------------------------------------------------
# Inicialización del cliente de Google GenAI
# ---------------------------------------------------------------------------
client = genai.Client(api_key=GOOGLE_API_KEY)


def crear_agente_vulnerable():
    """Inicializa una sesión de chat con el modelo Gemini **sin defensas**.

    Cada llamada crea una sesión nueva para evitar que el contexto
    acumulado de una conversación anterior influya en los resultados
    de los ataques.

    Returns:
        Sesión de chat de ``google.genai`` configurada con el
        System Prompt vulnerable.
    """
    chat = client.chats.create(
        model=LLM_MODEL,
        config=genai.types.GenerateContentConfig(
            system_instruction=VULNERABLE_SYSTEM_PROMPT,
            temperature=LLM_TEMPERATURE,
        ),
    )
    return chat


@retry(
    stop=stop_after_attempt(MAX_RETRIES),
    wait=wait_exponential(multiplier=2, min=4, max=60),
    retry=retry_if_exception_type(Exception),
)
def enviar_mensaje(chat, mensaje_usuario: str) -> str:
    """Envía un mensaje al agente vulnerable y devuelve la respuesta.

    Implementa reintentos con *exponential backoff* para gestionar
    los errores 429 (RESOURCE_EXHAUSTED) del tier gratuito de la API.

    Args:
        chat: Sesión de chat de Gemini.
        mensaje_usuario: Texto del payload de ataque o consulta.

    Returns:
        Texto de la respuesta generada por el LLM.

    Raises:
        tenacity.RetryError: Si se agotan todos los reintentos.
    """
    respuesta = chat.send_message(mensaje_usuario)
    return respuesta.text


# ---------------------------------------------------------------------------
# Modo interactivo (ejecución directa)
# ---------------------------------------------------------------------------
def ejecutar_demo_interactiva():
    """Ejecuta una sesión interactiva con el agente vulnerable."""
    print("=" * 60)
    print("  AGENTE VULNERABLE — AsistenteCompra (SIN Guardrails)")
    print("=" * 60)
    print("  Escribe 'salir' para terminar la sesión.")
    print("-" * 60)

    chat = crear_agente_vulnerable()

    while True:
        user_input = input("\nTú: ").strip()
        if user_input.lower() in ("salir", "exit", "quit"):
            print("\n[Sesión finalizada]")
            break
        if not user_input:
            continue

        respuesta = enviar_mensaje(chat, user_input)
        print(f"\nAsistenteCompra: {respuesta}")


if __name__ == "__main__":
    ejecutar_demo_interactiva()
