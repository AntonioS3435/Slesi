"""
Módulo 1: Agente LLM Vulnerable.

Implementa un chatbot de atención al cliente SIN ninguna capa de
protección externa. Este módulo demuestra cómo un agente con información
sensible en su System Prompt puede ser explotado mediante Prompt Injection.
"""

from openai import OpenAI
from config import OPENAI_API_KEY, LLM_MODEL, LLM_TEMPERATURE, VULNERABLE_SYSTEM_PROMPT


def crear_agente_vulnerable() -> tuple[OpenAI, list[dict]]:
    """Inicializa el cliente OpenAI y el historial de conversación."""
    client = OpenAI(api_key=OPENAI_API_KEY)
    historial = [{"role": "system", "content": VULNERABLE_SYSTEM_PROMPT}]
    return client, historial


def enviar_mensaje(client: OpenAI, historial: list[dict], mensaje_usuario: str) -> str:
    """
    Envía un mensaje al agente vulnerable y devuelve la respuesta.

    Args:
        client: Cliente OpenAI configurado.
        historial: Lista de mensajes de la conversación.
        mensaje_usuario: Texto del usuario.

    Returns:
        Respuesta generada por el LLM.
    """
    historial.append({"role": "user", "content": mensaje_usuario})

    respuesta = client.chat.completions.create(
        model=LLM_MODEL,
        messages=historial,
        temperature=LLM_TEMPERATURE,
    )

    contenido = respuesta.choices[0].message.content
    historial.append({"role": "assistant", "content": contenido})
    return contenido


def ejecutar_demo_interactiva():
    """Ejecuta una sesión interactiva con el agente vulnerable."""
    print("=" * 60)
    print("  AGENTE VULNERABLE - AsistenteCompra (SIN Guardrails)")
    print("=" * 60)
    print("  Escribe 'salir' para terminar la sesión.")
    print("-" * 60)

    client, historial = crear_agente_vulnerable()

    while True:
        user_input = input("\n🧑 Tú: ").strip()
        if user_input.lower() in ("salir", "exit", "quit"):
            print("\n[Sesión finalizada]")
            break
        if not user_input:
            continue

        respuesta = enviar_mensaje(client, historial, user_input)
        print(f"\n🤖 AsistenteCompra: {respuesta}")


if __name__ == "__main__":
    ejecutar_demo_interactiva()
