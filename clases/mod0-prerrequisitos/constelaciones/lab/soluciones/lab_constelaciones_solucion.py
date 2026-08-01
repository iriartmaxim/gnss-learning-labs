#!/usr/bin/env python3
"""Lab constelaciones — censo y comparación orbital multi-GNSS (SOLUCION).

Del BRDC mixto del día 166: cuántos satélites emite cada constelación y
a qué altura/período vuela cada una — medido de las efemérides reales,
sin librerías. GLONASS de yapa: su nav no trae keplerianos sino vectores
de estado (posición/velocidad) — el formato lo delata.
Correr desde la raíz del repo. Requiere data/raw/2026/166 (clase 0.4).
"""
import sys
from collections import Counter, defaultdict
from pathlib import Path

MU = 3.986004418e14          # m^3/s^2
RE = 6371.0                  # km, radio medio
NAV = Path("data/raw/2026/166/BRDC00IGS_R_20261660000_01D_MN.rnx")
NOMBRES = {"G": "GPS", "E": "Galileo", "R": "GLONASS", "C": "BeiDou",
           "J": "QZSS", "I": "NavIC", "S": "SBAS"}


def parsear(nav):
    """Censo por constelación + sqrtA de la 1ª efeméride de cada SV.

    En RINEX 3 nav, para G/E/C/J/I el campo sqrtA es el 3er valor de la
    línea 3 del registro (17 chars por campo desde la col 4). Para R/S el
    registro son vectores de estado: guardamos |r| de la línea 1.
    """
    svs = defaultdict(set)
    sqrta = {}
    rglo = {}
    lineas = nav.read_text().splitlines()
    i = 0
    while i < len(lineas):
        l = lineas[i]
        if l[:1] in NOMBRES and l[1:3].isdigit():
            sv = l[:3]
            svs[l[0]].add(sv)
            def campo(fila, k):
                s = lineas[i + fila][4 + 19 * k: 4 + 19 * (k + 1)]
                return float(s.replace("D", "E").replace("d", "e"))
            try:
                if l[0] in "GECJI" and sv not in sqrta:
                    sqrta[sv] = campo(2, 3)          # línea 3, campo 4: sqrtA
                if l[0] == "R" and sv not in rglo:
                    x = campo(1, 0); y = campo(2, 0); z = campo(3, 0)
                    rglo[sv] = (x * x + y * y + z * z) ** 0.5   # km
            except (ValueError, IndexError):
                pass
        i += 1
    return svs, sqrta, rglo


def resumen(svs, sqrta, rglo):
    import math
    filas = []
    for c in "GERC":
        n = len(svs.get(c, ()))
        if c == "R":
            rs = [r for sv, r in rglo.items()]
            a_km = sorted(rs)[len(rs) // 2] if rs else float("nan")
        else:
            aes = sorted(sqrta[sv] ** 2 / 1e3 for sv in svs[c] if sv in sqrta)
            a_km = aes[len(aes) // 2]                # mediana (BDS mezcla MEO/IGSO/GEO)
        T_h = 2 * 3.141592653589793 * ((a_km * 1e3) ** 3 / MU) ** 0.5 / 3600
        filas.append((NOMBRES[c], n, a_km, T_h, a_km - RE))
    return filas


def main():
    svs, sqrta, rglo = parsear(NAV)
    print("== censo del BRDC (satélites únicos con efemérides, día 166) ==")
    for c in sorted(svs):
        print(f"  {NOMBRES[c]:8s} {len(svs[c]):3d} satélites")
    print("\n== órbitas medidas de las efemérides (mediana por constelación) ==")
    print(f"  {'':8s} {'a [km]':>9s} {'T [h]':>7s} {'altura [km]':>12s}")
    for nombre, n, a, T, h in resumen(svs, sqrta, rglo):
        print(f"  {nombre:8s} {a:9.0f} {T:7.2f} {h:12.0f}")
    filas = dict((f[0], f) for f in resumen(svs, sqrta, rglo))
    # -- validación de referencia (día 166) --
    assert len(svs["G"]) == 32 and len(svs["E"]) == 30, "censo G/E"
    assert abs(filas["GPS"][2] - 26560) < 30, filas["GPS"]
    assert abs(filas["Galileo"][2] - 29600) < 30, filas["Galileo"]
    assert abs(filas["GLONASS"][2] - 25500) < 150, filas["GLONASS"]
    assert 27800 < filas["BeiDou"][2] < 28000, filas["BeiDou"]   # mediana = MEO
    assert abs(filas["GPS"][3] - 11.97) < 0.05
    assert abs(filas["Galileo"][3] - 14.08) < 0.05
    # GLONASS: formato distinto = diseño distinto (FDMA, vectores de estado)
    print("\n  GLONASS no transmite keplerianos: su efeméride son vectores de")
    print("  estado (x,y,z,v) + aceleraciones lunisolares — integrás, no propagás.")
    print("VALIDACION 2026/166: OK")
    import json
    base = Path("clases/mod0-prerrequisitos/constelaciones")
    json.dump({"censo": {NOMBRES[c]: len(svs[c]) for c in sorted(svs)},
               "tabla": [list(f) for f in resumen(svs, sqrta, rglo)]},
              open(base / "data" / "resultados_const.json", "w"), indent=1)
    print("exportado -> resultados_const.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
