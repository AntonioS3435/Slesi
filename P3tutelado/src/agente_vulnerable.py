"""
Módulo 1: Agente LLM Vulnerable.

Implementa un chatbot de atención al cliente SIN ninguna capa de
protección externa. Demuestra cómo un agente con información
sensible en su System Prompt puede ser explotado mediante Prompt Injection.
"""

from google import genai
from config import GOOGLE_API_KEY, LLM_MODEL, LLM_TEMPERATURE, VULNERABLE_SYSTEM_PROMPT

client = genai.Client(api_key=GOOGLE_API_KEY)


def crear_agente_vulnerable():
    """Inicializa una sesión de chat con el modelo Gemini vulnerable."""
    chat = client.chats.create(
        model=LLM_MODEL,
        config=genai.types.GenerateContentConfig(
            system_instruction=VULNERABLE_SYSTEM_PROMPT,
            temperature=LLM_TEMPERATURE,
        ),
    )
    return chat


from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=2, min=4, max=30))
def enviar_mensaje(chat, mensaje_usuario: str) -> str:
    """
    Envía un mensaje al agente vulnerable y devuelve la respuesta.

    Args:
        chat: Sesión de chat de Gemini.
        mensaje_usuario: Texto del usuario.

    Returns:
        Respuesta generada por el LLM.
    """
    respuesta = chat.send_message(mensaje_usuario)
    return respuesta.text


def ejecutar_demo_interactiva():
    """Ejecuta una sesión interactiva con el agente vulnerable."""
    print("=" * 60)
    print("  AGENTE VULNERABLE - AsistenteCompra (SIN Guardrails)")
    print("=" * 60)
    print("  Escribe 'salir' para terminar la sesion.")
    print("-" * 60)

    chat = crear_agente_vulnerable()

    while True:
        user_input = input("\nTu: ").strip()
        if user_input.lower() in ("salir", "exit", "quit"):
            print("\n[Sesion finalizada]")
            break
        if not user_input:
            continue

        respuesta = enviar_mensaje(chat, user_input)
        print(f"\nAsistenteCompra: {respuesta}")


if __name__ == "__main__":
    ejecutar_demo_interactiva()
