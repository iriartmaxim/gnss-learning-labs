#!/usr/bin/env python3
"""Solución 6.6 — Threat model de OSNMA/SAS como matriz verificable.

El "lab" de esta clase es un análisis estructurado (estilo ADR): una matriz
ataque × defensa que codifica qué mitiga cada capa (OSNMA, SAS/ACAS,
detectores de consistencia 6.4, sanidad física de efeméride 4.1) y qué
queda afuera. El script valida que la matriz es coherente: no hay ataque
sin ninguna defensa, y OSNMA sola NO cubre los ataques de rango.

Correr:  python3 lab_threat_solucion.py   → "THREAT MODEL OK".
"""
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[4].parent

# capas de defensa
CAPAS = ["OSNMA", "SAS/ACAS", "detectores_6.4", "fisica_4.1"]

# matriz ataque -> qué capa lo mitiga (True) y nivel de residuo
# (lo que sigue siendo posible pese a las defensas)
AMENAZAS = {
    "falsificar efeméride/reloj (datos)": {
        "OSNMA": True, "SAS/ACAS": False, "detectores_6.4": True, "fisica_4.1": True,
        "residuo": "bajo: OSNMA autentica los datos; física valida coherencia orbital",
    },
    "spoofing de rango (señal falsa alineada)": {
        "OSNMA": False, "SAS/ACAS": True, "detectores_6.4": True, "fisica_4.1": False,
        "residuo": "medio: OSNMA NO ve el rango; SAS y detectores (C/N0, salto) ayudan",
    },
    "replay / meaconing (dentro de la ventana)": {
        "OSNMA": False, "SAS/ACAS": True, "detectores_6.4": True, "fisica_4.1": False,
        "residuo": "medio: re-emitir señal auténtica con retardo evade OSNMA; SAS/tiempo lo acotan",
    },
    "jamming (negación)": {
        "OSNMA": False, "SAS/ACAS": False, "detectores_6.4": True, "fisica_4.1": False,
        "residuo": "alto: no se puede autenticar lo que no llega; se detecta (AGC) y se puentea (INS)",
    },
    "captura de lazo (lift-off gradual)": {
        "OSNMA": False, "SAS/ACAS": True, "detectores_6.4": True, "fisica_4.1": True,
        "residuo": "medio: la sanidad física (salto de posición/efeméride) y SAS lo delatan",
    },
}


def validar_matriz(amenazas):
    """Chequeos de coherencia del threat model."""
    problemas = []
    for ataque, fila in amenazas.items():
        cubierto = any(fila.get(c, False) for c in CAPAS)
        if not cubierto:
            problemas.append(f"'{ataque}' no tiene NINGUNA defensa")
        if "residuo" not in fila or not fila["residuo"]:
            problemas.append(f"'{ataque}' sin análisis de residuo")
    # aserción clave del dominio: OSNMA NO cubre los ataques de rango
    rango = ["spoofing de rango (señal falsa alineada)",
             "replay / meaconing (dentro de la ventana)"]
    for a in rango:
        if amenazas[a]["OSNMA"]:
            problemas.append(f"ERROR conceptual: OSNMA no debería 'cubrir' {a}")
    return problemas


def cobertura(amenazas):
    """Cuántos ataques cubre cada capa (para priorizar)."""
    return {c: sum(1 for f in amenazas.values() if f.get(c)) for c in CAPAS}


def main() -> int:
    problemas = validar_matriz(AMENAZAS)
    cob = cobertura(AMENAZAS)

    print("== Matriz de amenazas × defensas ==")
    for ataque, fila in AMENAZAS.items():
        capas = [c for c in CAPAS if fila.get(c)]
        print(f"\n• {ataque}")
        print(f"    mitigan: {', '.join(capas) if capas else 'NINGUNA'}")
        print(f"    residuo: {fila['residuo']}")

    print("\n== cobertura por capa (nº de ataques que toca) ==")
    for c, n in sorted(cob.items(), key=lambda x: -x[1]):
        print(f"    {c:16s} {n}/{len(AMENAZAS)}")

    print("\n== hallazgos clave ==")
    print("  - OSNMA autentica DATOS, no RANGO: sola no frena spoofing de rango ni replay.")
    print("  - Ninguna capa cubre todo: la defensa es EN CAPAS (cripto + señal + física).")
    print("  - El jamming no se autentica: se detecta y se sobrevive (INS, 7.5).")

    dest = RAIZ / "clases/mod6-seguridad/clase6.6-threat-model/data"
    dest.mkdir(parents=True, exist_ok=True)
    json.dump({"amenazas": AMENAZAS, "cobertura": cob, "problemas": problemas},
              open(dest / "resultados_6_6.json", "w"), indent=1, ensure_ascii=False)

    assert not problemas, f"matriz incoherente: {problemas}"
    assert cob["detectores_6.4"] == len(AMENAZAS), "los detectores deberían tocar todos los ataques"
    assert not AMENAZAS["spoofing de rango (señal falsa alineada)"]["OSNMA"]
    print("\nTHREAT MODEL OK: matriz coherente, defensa en capas justificada")
    return 0


if __name__ == "__main__":
    sys.exit(main())
