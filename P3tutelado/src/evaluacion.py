"""
Módulo 4: Evaluación Comparativa de Robustez.

Ejecuta la **misma** batería de ataques contra ambos agentes
(vulnerable y defendido) y genera un informe comparativo con
métricas de seguridad que demuestran la eficacia de la capa de
defensa implementada con NeMo Guardrails.

Flujo de ejecución:
  FASE 1 → Ataques al agente SIN Guardrails  (agente_vulnerable)
  FASE 2 → Ataques al agente CON Guardrails  (agente_defendido)
  FASE 3 → Generación de tabla comparativa e informe JSON

Salida:
  - Tabla comparativa en consola.
  - ``informe_comparativo.json`` con el detalle completo.
"""

import asyncio
import datetime
import json
import time

from agente_defendido import crear_agente_defendido, enviar_mensaje_seguro
from agente_vulnerable import crear_agente_vulnerable, enviar_mensaje
from ataques import ATAQUES, evaluar_exito
from config import REQUEST_DELAY_SECONDS


# ═══════════════════════════════════════════════════════════════════════════
# FUNCIÓN PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════

async def ejecutar_evaluacion_comparativa():
    """Ejecuta todos los ataques contra ambos agentes y compara resultados.

    La evaluación utiliza los mismos prompts y los mismos indicadores
    de éxito para ambos agentes, garantizando una comparación justa.
    """
    print("=" * 70)
    print("  EVALUACIÓN COMPARATIVA DE ROBUSTEZ")
    print("  Agente Vulnerable vs. Agente Defendido (NeMo Guardrails)")
    print("=" * 70)

    resultados_vulnerable = []
    resultados_defendido = []

    # ---------------------------------------------------------------
    # FASE 1: Ataques al Agente Vulnerable (SIN Guardrails)
    # ---------------------------------------------------------------
    print("\n\n[*] FASE 1: Ataques al Agente SIN Guardrails")
    print("-" * 70)

    for i, ataque in enumerate(ATAQUES):
        print(f"\n  [{ataque['id']}] {ataque['nombre']}...")

        try:
            chat = crear_agente_vulnerable()
            respuesta = enviar_mensaje(chat, ataque["prompt"])
        except Exception as e:
            respuesta = f"[ERROR] No se pudo obtener respuesta: {e}"

        evaluacion = evaluar_exito(respuesta, ataque["indicadores_exito"])

        resultados_vulnerable.append({
            "id": ataque["id"],
            "nombre": ataque["nombre"],
            "categoria": ataque["categoria"],
            "respuesta": respuesta[:500],
            "evaluacion": evaluacion,
        })
        print(f"     Resultado: {evaluacion['veredicto']} "
              f"({evaluacion['tasa_exito']}%)")

        if i < len(ATAQUES) - 1:
            time.sleep(REQUEST_DELAY_SECONDS)

    # ---------------------------------------------------------------
    # FASE 2: Ataques al Agente Defendido (CON Guardrails)
    # ---------------------------------------------------------------
    print("\n\n[*] FASE 2: Ataques al Agente CON Guardrails")
    print("-" * 70)

    rails = await crear_agente_defendido()

    for i, ataque in enumerate(ATAQUES):
        print(f"\n  [{ataque['id']}] {ataque['nombre']}...")

        try:
            resultado = await enviar_mensaje_seguro(rails, ataque["prompt"])
            respuesta_texto = resultado["respuesta"]
        except Exception as e:
            respuesta_texto = f"[ERROR] No se pudo obtener respuesta: {e}"
            resultado = {"bloqueado": False, "rails_activadas": []}

        evaluacion = evaluar_exito(respuesta_texto, ataque["indicadores_exito"])

        resultados_defendido.append({
            "id": ataque["id"],
            "nombre": ataque["nombre"],
            "categoria": ataque["categoria"],
            "respuesta": respuesta_texto[:500],
            "evaluacion": evaluacion,
            "rail_activada": resultado["bloqueado"],
        })
        estado = "[BLOQUEADO POR RAIL]" if resultado["bloqueado"] else evaluacion["veredicto"]
        print(f"     Resultado: {estado} ({evaluacion['tasa_exito']}%)")

        if i < len(ATAQUES) - 1:
            time.sleep(REQUEST_DELAY_SECONDS)

    # ---------------------------------------------------------------
    # FASE 3: Informe Comparativo
    # ---------------------------------------------------------------
    mostrar_tabla_comparativa(resultados_vulnerable, resultados_defendido)
    guardar_informe_comparativo(resultados_vulnerable, resultados_defendido)


# ═══════════════════════════════════════════════════════════════════════════
# VISUALIZACIÓN DE RESULTADOS
# ═══════════════════════════════════════════════════════════════════════════

def mostrar_tabla_comparativa(vuln: list[dict], defe: list[dict]):
    """Imprime una tabla comparativa de resultados en consola."""
    print("\n\n" + "=" * 85)
    print("  TABLA COMPARATIVA DE RESULTADOS")
    print("=" * 85)
    print(f"  {'ID':<8} {'Ataque':<35} {'Sin Guardrails':<18} {'Con Guardrails':<18}")
    print("-" * 85)

    exitos_vuln = 0
    exitos_defe = 0

    for v, d in zip(vuln, defe):
        estado_v = _clasificar_estado(v["evaluacion"]["veredicto"])
        estado_d = (
            "BLOQUEADO" if d.get("rail_activada")
            else _clasificar_estado(d["evaluacion"]["veredicto"])
        )

        if estado_v == "ÉXITO":
            exitos_vuln += 1
        if estado_d == "ÉXITO":
            exitos_defe += 1

        print(f"  {v['id']:<8} {v['nombre'][:33]:<35} {estado_v:<18} {estado_d:<18}")

    total = len(vuln)
    tasa_vuln = round(exitos_vuln / total * 100) if total else 0
    tasa_defe = round(exitos_defe / total * 100) if total else 0

    print("-" * 85)
    print(f"  {'TOTAL':<8} {'Tasa de compromiso':<35} "
          f"{exitos_vuln}/{total} ({tasa_vuln}%)      "
          f"{exitos_defe}/{total} ({tasa_defe}%)")

    if exitos_vuln > 0:
        reduccion = round((exitos_vuln - exitos_defe) / exitos_vuln * 100)
    else:
        reduccion = 0

    print(f"\n  [*] Reducción de vulnerabilidad con Guardrails: {reduccion}%")

    # Desglose por categoría OWASP
    _mostrar_desglose_categorias(vuln, defe)
    print("=" * 85)


def _clasificar_estado(veredicto: str) -> str:
    """Extrae un estado resumido del veredicto completo."""
    if "EXITO" in veredicto:
        return "ÉXITO"
    if "PARCIAL" in veredicto:
        return "PARCIAL"
    return "FALLIDO"


def _mostrar_desglose_categorias(vuln: list[dict], defe: list[dict]):
    """Muestra un desglose por categoría OWASP."""
    categorias: dict[str, dict] = {}
    for v, d in zip(vuln, defe):
        cat = v["categoria"]
        if cat not in categorias:
            categorias[cat] = {"vuln_exitos": 0, "defe_exitos": 0, "total": 0}
        categorias[cat]["total"] += 1
        if "EXITO" in v["evaluacion"]["veredicto"]:
            categorias[cat]["vuln_exitos"] += 1
        if "EXITO" in d["evaluacion"]["veredicto"] and not d.get("rail_activada"):
            categorias[cat]["defe_exitos"] += 1

    print(f"\n  {'-' * 77}")
    print(f"  DESGLOSE POR CATEGORIA OWASP")
    print(f"  {'-' * 77}")
    for cat, datos in categorias.items():
        v_pct = round(datos["vuln_exitos"] / datos["total"] * 100) if datos["total"] else 0
        d_pct = round(datos["defe_exitos"] / datos["total"] * 100) if datos["total"] else 0
        print(f"  {cat:<45} Vuln: {v_pct:>3}%  Def: {d_pct:>3}%")


# ═══════════════════════════════════════════════════════════════════════════
# PERSISTENCIA DEL INFORME
# ═══════════════════════════════════════════════════════════════════════════

def guardar_informe_comparativo(vuln: list[dict], defe: list[dict]):
    """Guarda el informe comparativo en formato JSON.

    Incluye metadatos del experimento, métricas agregadas y el detalle
    completo de cada ataque para ambos agentes.
    """
    total = len(vuln)
    exitos_vuln = sum(1 for r in vuln if "EXITO" in r["evaluacion"]["veredicto"])
    exitos_defe = sum(1 for r in defe if "EXITO" in r["evaluacion"]["veredicto"])
    bloqueados = sum(1 for r in defe if r.get("rail_activada"))

    informe = {
        "metadatos": {
            "fecha": datetime.datetime.now().isoformat(),
            "herramienta": "PoC Seguridad en LLMs — Trabajo Tutelado SLESI",
            "modelo_evaluado": "gemini-3.1-flash-lite",
            "framework_defensa": "NeMo Guardrails (NVIDIA)",
        },
        "total_ataques": total,
        "resumen": {
            "tasa_compromiso_vulnerable": round(exitos_vuln / total * 100, 1),
            "tasa_compromiso_defendido": round(exitos_defe / total * 100, 1),
            "ataques_bloqueados_por_rails": bloqueados,
            "reduccion_vulnerabilidad": (
                round((exitos_vuln - exitos_defe) / exitos_vuln * 100, 1)
                if exitos_vuln > 0 else 0.0
            ),
        },
        "agente_vulnerable": {
            "exitosos": exitos_vuln,
            "detalle": vuln,
        },
        "agente_defendido": {
            "exitosos": exitos_defe,
            "bloqueados": bloqueados,
            "detalle": defe,
        },
    }

    filename = "informe_comparativo.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(informe, f, ensure_ascii=False, indent=2)
    print(f"\n[*] Informe comparativo guardado en: {filename}")


# ═══════════════════════════════════════════════════════════════════════════
# PUNTO DE ENTRADA
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    asyncio.run(ejecutar_evaluacion_comparativa())
