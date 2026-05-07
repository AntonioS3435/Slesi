"""
Módulo 4: Evaluación Comparativa de Robustez.

Ejecuta la misma batería de ataques contra ambos agentes (vulnerable
y defendido) y genera un informe comparativo con métricas de seguridad.
"""

import asyncio
import json
import time
import datetime
from agente_vulnerable import crear_agente_vulnerable, enviar_mensaje
from agente_defendido import crear_agente_defendido, enviar_mensaje_seguro
from ataques import ATAQUES, evaluar_exito


async def ejecutar_evaluacion_comparativa():
    """
    Ejecuta todos los ataques contra ambos agentes y compara resultados.
    """
    print("=" * 70)
    print("  EVALUACIÓN COMPARATIVA DE ROBUSTEZ")
    print("  Agente Vulnerable vs. Agente Defendido (NeMo Guardrails)")
    print("=" * 70)

    resultados_vulnerable = []
    resultados_defendido = []

    # --- Fase 1: Ataques al Agente Vulnerable ---
    print("\n\n[*] FASE 1: Ataques al Agente SIN Guardrails")
    print("-" * 70)

    for ataque in ATAQUES:
        print(f"\n  [{ataque['id']}] {ataque['nombre']}...")
        chat = crear_agente_vulnerable()
        respuesta = enviar_mensaje(chat, ataque["prompt"])
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
              
        if ataque != ATAQUES[-1]:
            time.sleep(10)

    # --- Fase 2: Ataques al Agente Defendido ---
    print("\n\n[*] FASE 2: Ataques al Agente CON Guardrails")
    print("-" * 70)

    rails = await crear_agente_defendido()

    for ataque in ATAQUES:
        print(f"\n  [{ataque['id']}] {ataque['nombre']}...")
        resultado = await enviar_mensaje_seguro(rails, ataque["prompt"])
        respuesta_texto = resultado["respuesta"]
        evaluacion = evaluar_exito(respuesta_texto, ataque["indicadores_exito"])

        resultados_defendido.append({
            "id": ataque["id"],
            "nombre": ataque["nombre"],
            "categoria": ataque["categoria"],
            "respuesta": respuesta_texto[:500],
            "evaluacion": evaluacion,
            "rail_activada": resultado["bloqueado"],
        })
        estado = "[BLOQUEADO]" if resultado["bloqueado"] else evaluacion["veredicto"]
        print(f"     Resultado: {estado} ({evaluacion['tasa_exito']}%)")
        
        if ataque != ATAQUES[-1]:
            time.sleep(10)

    # --- Fase 3: Informe Comparativo ---
    mostrar_tabla_comparativa(resultados_vulnerable, resultados_defendido)
    guardar_informe_comparativo(resultados_vulnerable, resultados_defendido)


def mostrar_tabla_comparativa(vuln: list[dict], defe: list[dict]):
    """Imprime una tabla comparativa de resultados."""
    print("\n\n" + "=" * 80)
    print("  TABLA COMPARATIVA DE RESULTADOS")
    print("=" * 80)
    print(f"  {'ID':<8} {'Ataque':<30} {'Sin Guardrails':<18} {'Con Guardrails':<18}")
    print("-" * 80)

    exitos_vuln = 0
    exitos_defe = 0

    for v, d in zip(vuln, defe):
        estado_v = "ÉXITO" if "ÉXITO" in v["evaluacion"]["veredicto"] else (
            "PARCIAL" if "PARCIAL" in v["evaluacion"]["veredicto"] else "FALLIDO"
        )
        estado_d = "BLOQUEADO" if d.get("rail_activada") else (
            "ÉXITO" if "ÉXITO" in d["evaluacion"]["veredicto"] else "FALLIDO"
        )

        if "ÉXITO" in estado_v:
            exitos_vuln += 1
        if "ÉXITO" in estado_d:
            exitos_defe += 1

        print(f"  {v['id']:<8} {v['nombre'][:28]:<30} {estado_v:<18} {estado_d:<18}")

    total = len(vuln)
    print("-" * 80)
    print(f"  {'TOTAL':<8} {'Tasa de compromiso':<30} "
          f"{exitos_vuln}/{total} ({round(exitos_vuln/total*100)}%)     "
          f"{exitos_defe}/{total} ({round(exitos_defe/total*100)}%)")

    reduccion = ((exitos_vuln - exitos_defe) / exitos_vuln * 100) if exitos_vuln > 0 else 0
    print(f"\n  [*] Reducción de vulnerabilidad con Guardrails: {round(reduccion)}%")
    print("=" * 80)


def guardar_informe_comparativo(vuln: list[dict], defe: list[dict]):
    """Guarda el informe comparativo en JSON."""
    informe = {
        "fecha": datetime.datetime.now().isoformat(),
        "total_ataques": len(vuln),
        "agente_vulnerable": {
            "exitosos": sum(1 for r in vuln if "ÉXITO" in r["evaluacion"]["veredicto"]),
            "detalle": vuln,
        },
        "agente_defendido": {
            "exitosos": sum(1 for r in defe if "ÉXITO" in r["evaluacion"]["veredicto"]),
            "bloqueados": sum(1 for r in defe if r.get("rail_activada")),
            "detalle": defe,
        },
    }

    filename = "informe_comparativo.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(informe, f, ensure_ascii=False, indent=2)
    print(f"\n[*] Informe comparativo guardado en: {filename}")


if __name__ == "__main__":
    asyncio.run(ejecutar_evaluacion_comparativa())
