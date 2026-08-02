#!/usr/bin/env python3
"""Solución 5.4 — La cadena de integridad del sistema (capas combinadas).

Integra las defensas del path en un único monitor de integridad: RAIM por
residuos (5.1), detectores de consistencia (6.4), autenticación OSNMA (6.1)
y sanidad física de efeméride (4.1), más el concepto de monitoreo de tierra.
Muestra sobre escenarios sintéticos que la COMBINACIÓN cubre casos que
ninguna capa aislada detecta. Determinista. Correr: python3 ...solucion.py.
"""
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[4].parent

# capas de monitoreo (usuario + sistema) y qué detecta cada una
#   RAIM: fallo de rango con redundancia (5.1/5.2)
#   consistencia: C/N0, cruce, salto (6.4)
#   OSNMA: datos de navegación falsos (6.1/6.2)
#   fisica: efeméride implausible (4.1)
#   tierra: monitoreo del segmento de control (SISRE anómalo, salud)
CAPAS = ["RAIM", "consistencia", "OSNMA", "fisica", "tierra"]

# escenarios: qué capa(s) lo detectan (verdad de diseño)
ESCENARIOS = {
    "fallo de reloj en 1 satélite (bias de rango)": {
        "RAIM": True, "consistencia": True, "OSNMA": False, "fisica": False, "tierra": True},
    "efeméride falsa (datos manipulados)": {
        "RAIM": False, "consistencia": False, "OSNMA": True, "fisica": True, "tierra": True},
    "spoofing de rango (señal coherente)": {
        "RAIM": True, "consistencia": True, "OSNMA": False, "fisica": False, "tierra": False},
    "replay/meaconing (con retardo)": {
        "RAIM": False, "consistencia": True, "OSNMA": False, "fisica": False, "tierra": False},
    "mala salud de satélite (no señalada)": {
        "RAIM": True, "consistencia": False, "OSNMA": False, "fisica": True, "tierra": True},
}


def monitor(escenario_flags, capas_activas):
    """Decisión de integridad: alerta si ALGUNA capa activa detecta."""
    return any(escenario_flags.get(c, False) for c in capas_activas)


def main() -> int:
    print("== cobertura por capa aislada vs combinación ==")
    # cuántos escenarios cubre cada capa sola
    solo = {c: sum(1 for e in ESCENARIOS.values() if e[c]) for c in CAPAS}
    for c, n in sorted(solo.items(), key=lambda x: -x[1]):
        print(f"   {c:14s} sola: {n}/{len(ESCENARIOS)} escenarios")

    # combinación de todas las capas
    cubiertos = sum(1 for e in ESCENARIOS.values() if monitor(e, CAPAS))
    print(f"\n   TODAS combinadas: {cubiertos}/{len(ESCENARIOS)} escenarios")

    # solo usuario (sin tierra) vs con tierra
    usuario = ["RAIM", "consistencia", "OSNMA", "fisica"]
    cub_usuario = sum(1 for e in ESCENARIOS.values() if monitor(e, usuario))
    print(f"   solo capas de USUARIO (sin monitoreo de tierra): {cub_usuario}/{len(ESCENARIOS)}")

    print("\n== detalle por escenario ==")
    sin_cobertura = []
    for nombre, flags in ESCENARIOS.items():
        capas = [c for c in CAPAS if flags[c]]
        if not capas:
            sin_cobertura.append(nombre)
        print(f"  • {nombre}")
        print(f"      detectan: {', '.join(capas)}")

    print("\n== hallazgos ==")
    print("  - Ninguna capa sola cubre todo; la combinación (defensa en capas) sí.")
    print("  - El replay solo lo ve la consistencia (6.4): OSNMA no autentica rango.")
    print("  - El monitoreo de TIERRA agrega cobertura que el usuario no tiene "
          "(salud del segmento, SISRE), pero no ve el spoofing local del usuario.")

    dest = RAIZ / "clases/mod5-integridad/clase5.4-integridad-sistema/data"
    dest.mkdir(parents=True, exist_ok=True)
    json.dump({"cobertura_por_capa": solo, "combinada": cubiertos,
               "solo_usuario": cub_usuario, "n": len(ESCENARIOS),
               "sin_cobertura": sin_cobertura},
              open(dest / "resultados_5_4.json", "w"), indent=1, ensure_ascii=False)

    assert cubiertos == len(ESCENARIOS), "la combinación debería cubrir todo"
    assert max(solo.values()) < len(ESCENARIOS), "ninguna capa sola debería cubrir todo"
    assert cub_usuario >= 4, "las capas de usuario deberían cubrir la mayoría"
    print("\nOK: la cadena de integridad del sistema = capas usuario + tierra")
    return 0


if __name__ == "__main__":
    sys.exit(main())
