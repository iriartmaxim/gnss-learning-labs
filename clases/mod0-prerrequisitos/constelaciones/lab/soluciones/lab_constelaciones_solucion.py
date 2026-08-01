#!/usr/bin/env python3
"""Solución — censo comparado de constelaciones sobre el BRDC real.

Cuenta SVs únicos por constelación en el RINEX nav mixto del día 166 y
los contrasta con la capacidad nominal de cada sistema. Correr desde la
raíz del repo (requiere data/raw/2026/166 de la clase 0.4).
"""
import sys
from collections import defaultdict
from pathlib import Path

NAV = "data/raw/2026/166/BRDC00IGS_R_20261660000_01D_MN.rnx"

# nombre, órbita, nº nominal de satélites operativos, banda abierta principal
FICHA = {
    "G": ("GPS",     "EE.UU.",     "MEO", 31, "L1 C/A"),
    "R": ("GLONASS", "Rusia",      "MEO", 24, "L1OF (FDMA)"),
    "E": ("Galileo", "UE",         "MEO", 28, "E1 (OSNMA)"),
    "C": ("BeiDou",  "China",      "MEO+IGSO+GEO", 35, "B1I/B1C"),
    "J": ("QZSS",    "Japón",      "IGSO+GEO (regional)", 4, "L1 C/A"),
    "I": ("NavIC",   "India",      "GEO+IGSO (regional)", 7, "L5/S"),
    "S": ("SBAS",    "aumentación","GEO", 0, "L1"),
}


def svs_por_constelacion(nav: Path):
    """SVs únicos por letra de constelación (cabeceras 'Xnn ...')."""
    vistos = defaultdict(set)
    with open(nav) as f:
        for linea in f:
            if linea[:1] in FICHA and linea[1:3].isdigit():
                vistos[linea[0]].add(linea[:3])
    return vistos


def main() -> int:
    nav = Path(NAV)
    if not nav.exists():
        print(f"No encuentro {NAV} — corré tools/fetch_data.py (clase 0.4)")
        return 1
    vistos = svs_por_constelacion(nav)

    print(f"{'Sistema':9s} {'País':11s} {'Órbita':22s} {'SVs BRDC':9s} {'nominal':8s} {'banda'}")
    globales = 0
    for c in ("G", "R", "E", "C", "J", "I", "S"):
        nombre, pais, orbita, nominal, banda = FICHA[c]
        n = len(vistos.get(c, ()))
        if c in ("G", "R", "E", "C"):
            globales += n
        print(f"{nombre:9s} {pais:11s} {orbita:22s} {n:<9d} {nominal:<8d} {banda}")

    print(f"\nSVs de sistemas GLOBALES (G+R+E+C) en el BRDC: {globales}")
    print("Galileo primaria del path (E1/E5a, OSNMA); GPS de contraste (Klobuchar, C/A).")

    # auto-tests contra el día 166 real
    n = {c: len(vistos.get(c, ())) for c in FICHA}
    assert n["G"] == 32, f"GPS: {n['G']} != 32"
    assert n["E"] == 30, f"Galileo: {n['E']} != 30"
    assert n["C"] == 37, f"BeiDou: {n['C']} != 37"
    assert n["R"] == 27, f"GLONASS: {n['R']} != 27"
    assert globales == 126, f"globales: {globales} != 126"
    print("\nVALIDACION 2026/166: OK (G32 · R27 · E30 · C37 · globales 126)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
