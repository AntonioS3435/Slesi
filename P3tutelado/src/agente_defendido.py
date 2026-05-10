"""
Módulo 3: Agente LLM Defendido con NeMo Guardrails.

Implementa el mismo chatbot "AsistenteCompra" pero protegido con una
capa externa de NeMo Guardrails (NVIDIA) que intercepta y filtra las
entradas y salidas del modelo, actuando como un **firewall semántico**.

Arquitectura de defensa en profundidad:
  1. Input Rails  → filtrado de prompts maliciosos ANTES de llegar al LLM.
  2. Output Rails → verificación de la respuesta ANTES de entregarla al usuario.

Referencia:
  - NeMo Guardrails: https://github.com/NVIDIA/NeMo-Guardrails
  - Colang 1.0: lenguaje declarativo para definir flujos de seguridad.

Dependencias:
    - nemoguardrails >= 0.10.0
    - langchain-google-genai >= 2.0.0
    - google-genai >= 1.0
"""

import asyncio
import os

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from config import GOOGLE_API_KEY, MAX_RETRIES

# ---------------------------------------------------------------------------
# Exportar la API Key para que NeMo Guardrails la detecte internamente
# (utiliza LangChain como backend, que busca estas variables de entorno).
# ---------------------------------------------------------------------------
os.environ["GEMINI_API_KEY"] = GOOGLE_API_KEY or ""
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY or ""

# Importar NeMo Guardrails DESPUÉS de configurar las variables de entorno
from nemoguardrails import LLMRails, RailsConfig  # noqa: E402


async def crear_agente_defendido() -> LLMRails:
    """Inicializa el agente con NeMo Guardrails.

    La configuración se carga desde el directorio ``guardrails_config/``
    que contiene:
      - ``config.yml``: modelo e instrucciones del sistema.
      - ``rails.co``:  reglas Colang de entrada/salida.

    Returns:
        Instancia de ``LLMRails`` configurada con las defensas activas.
    """
    config = RailsConfig.from_path("./guardrails_config")
    rails = LLMRails(config)
    return rails


@retry(
    stop=stop_after_attempt(MAX_RETRIES),
    wait=wait_exponential(multiplier=2, min=4, max=60),
    retry=retry_if_exception_type(Exception),
)
async def enviar_mensaje_seguro(rails: LLMRails, mensaje_usuario: str) -> dict:
    """Envía un mensaje al agente defendido y devuelve la respuesta.

    Además de la respuesta textual, devuelve metadatos sobre qué
    rails de seguridad se activaron durante el procesamiento.

    Args:
        rails: Instancia de LLMRails con las defensas configuradas.
        mensaje_usuario: Texto del payload de ataque o consulta.

    Returns:
        Diccionario con las claves:
          - ``respuesta`` (str): texto de la respuesta.
          - ``rails_activadas`` (list): rails que se dispararon.
          - ``bloqueado`` (bool): True si el mensaje fue filtrado.
    """
    respuesta = await rails.generate_async(
        messages=[{"role": "user", "content": mensaje_usuario}]
    )

    # Obtener información de trazabilidad del pipeline de Guardrails
    info = rails.explain()
    rails_activadas = []
    colang_trace = ""
    if info and hasattr(info, "colang_history"):
        colang_trace = str(info.colang_history)
        rails_activadas = [
            step for step in colang_trace.split("\n")
            if "refuse" in step.lower() or "block" in step.lower()
        ]

    # Extraer texto de la respuesta (puede ser dict o string)
    if isinstance(respuesta, dict):
        texto_respuesta = respuesta.get("content", "") or ""
    elif isinstance(respuesta, str):
        texto_respuesta = respuesta
    else:
        texto_respuesta = str(respuesta)

    # Detectar bloqueo: respuesta vacía O keywords de bloqueo O rails activadas
    bloqueado_por_keywords = any(
        kw in texto_respuesta.lower()
        for kw in ["no puedo", "⛔", "🔒", "ℹ️", "no estoy autorizado"]
    )
    bloqueado_por_trace = bool(rails_activadas) or "refuse" in colang_trace.lower()
    bloqueado_por_vacio = texto_respuesta.strip() == ""

    es_bloqueado = bloqueado_por_keywords or bloqueado_por_trace or bloqueado_por_vacio

    # Si fue bloqueado pero la respuesta está vacía, asignar mensaje informativo
    if es_bloqueado and not texto_respuesta.strip():
        texto_respuesta = (
            "[RAIL ACTIVADA] El mensaje fue interceptado por NeMo Guardrails "
            "antes de alcanzar el LLM."
        )

    return {
        "respuesta": texto_respuesta,
        "rails_activadas": rails_activadas,
        "bloqueado": es_bloqueado,
    }


# ---------------------------------------------------------------------------
# Modo interactivo (ejecución directa)
# ---------------------------------------------------------------------------
async def ejecutar_demo_interactiva():
    """Ejecuta una sesión interactiva con el agente defendido."""
    print("=" * 60)
    print("  AGENTE DEFENDIDO — AsistenteCompra (CON Guardrails)")
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
            print("\n🛡️  [RAIL ACTIVADA — Mensaje filtrado]")
        print(f"🤖 AsistenteCompra: {resultado['respuesta']}")


if __name__ == "__main__":
    asyncio.run(ejecutar_demo_interactiva())
