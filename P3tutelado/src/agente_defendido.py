"""
Módulo 3: Agente LLM Defendido con NeMo Guardrails.

Implementa el mismo chatbot "AsistenteCompra" pero protegido con una
capa externa de NeMo Guardrails que intercepta y filtra las entradas
y salidas del modelo, actuando como un firewall semántico.
"""

import asyncio
from nemoguardrails import RailsConfig, LLMRails
from config import GOOGLE_API_KEY
import os

# Asegurar que la API key este disponible para NeMo Guardrails
os.environ["GEMINI_API_KEY"] = GOOGLE_API_KEY or ""
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY or ""


async def crear_agente_defendido() -> LLMRails:
    """
    Inicializa el agente con NeMo Guardrails.
    La configuración se carga desde el directorio guardrails_config/
    que contiene config.yml (modelo e instrucciones) y rails.co (reglas).

    Returns:
        Instancia de LLMRails configurada con las defensas activas.
    """
    config = RailsConfig.from_path("./guardrails_config")
    rails = LLMRails(config)
    return rails


from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=2, min=4, max=30))
async def enviar_mensaje_seguro(rails: LLMRails, mensaje_usuario: str) -> dict:
    """
    Envía un mensaje al agente defendido y devuelve la respuesta
    junto con información sobre las rails activadas.

    Args:
        rails: Instancia de LLMRails.
        mensaje_usuario: Texto del usuario.

    Returns:
        Diccionario con la respuesta y metadatos de seguridad.
    """
    respuesta = await rails.generate_async(
        messages=[{"role": "user", "content": mensaje_usuario}]
    )

    # Obtener información sobre qué rails se activaron
    info = rails.explain()
    rails_activadas = []
    if info and hasattr(info, "colang_history"):
        rails_activadas = [
            step for step in str(info.colang_history).split("\n")
            if "refuse" in step.lower() or "block" in step.lower()
        ]

    return {
        "respuesta": respuesta.get("content", str(respuesta)),
        "rails_activadas": rails_activadas,
        "bloqueado": any(
            kw in str(respuesta).lower()
            for kw in ["no puedo", "⛔", "🔒", "ℹ️"]
        ),
    }


async def ejecutar_demo_interactiva():
    """Ejecuta una sesión interactiva con el agente defendido."""
    print("=" * 60)
    print("  AGENTE DEFENDIDO - AsistenteCompra (CON Guardrails)")
    print("=" * 60)
    print("  Escribe 'salir' para terminar la sesión.")
    print("-" * 60)

    rails = await crear_agente_defendido()

    while True:
        user_input = input("\n🧑 Tú: ").strip()
        if user_input.lower() in ("salir", "exit", "quit"):
            print("\n[Sesión finalizada]")
            break
        if not user_input:
            continue

        resultado = await enviar_mensaje_seguro(rails, user_input)

        if resultado["bloqueado"]:
            print(f"\n🛡️  [RAIL ACTIVADA - Mensaje filtrado]")
        print(f"🤖 AsistenteCompra: {resultado['respuesta']}")


if __name__ == "__main__":
    asyncio.run(ejecutar_demo_interactiva())
