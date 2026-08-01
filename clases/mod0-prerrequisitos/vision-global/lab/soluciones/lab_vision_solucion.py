#!/usr/bin/env python3
"""Lab visión global — el arco GNSS en tu disco (SOLUCION).

Recorre lo que el path ya descargó/produjo y lo ubica en el arco
    señal -> observables -> mensaje/órbitas -> verdad precisa -> solución
Si cada etapa tiene archivos reales, el arco completo está en tu máquina.
Correr desde la raíz del repo (requiere 0.4 hecho y labs corridos).
"""
import sys
from pathlib import Path

ETAPAS = [
    ("SEÑAL (muestras IQ crudas)",        "clase 2.2",  ["data/raw/iq/*.dat"]),
    ("OBSERVABLES (RINEX obs)",           "clase 1.5",  ["data/raw/*/*/[LC]*_MO.rnx"]),
    ("MENSAJE / ÓRBITAS broadcast",       "clase 1.3",  ["data/raw/*/*/BRDC*_MN.rnx"]),
    ("VERDAD PRECISA (SP3 + CLK)",        "clases 1.3/4.x", ["data/raw/*/*/*ORB.SP3", "data/raw/*/*/*CLK.CLK"]),
    ("SOLUCIÓN Y ERRORES (productos)",    "labs 1.5/3.x/4.1", ["clases/*/*/data/resultados_*.json"]),
]


def inventario():
    filas = []
    for nombre, clase, patrones in ETAPAS:
        archivos = []
        for p in patrones:
            archivos += sorted(Path(".").glob(p))
        mb = sum(a.stat().st_size for a in archivos) / 1e6
        filas.append((nombre, clase, archivos, mb))
    return filas


def main():
    print("== el arco GNSS, etapa por etapa, con TUS archivos ==\n")
    total = 0.0
    for nombre, clase, archivos, mb in inventario():
        total += mb
        print(f"[{nombre}]  <- {clase}  ({len(archivos)} archivos, {mb:,.1f} MB)")
        for a in archivos[:4]:
            print(f"    {a.name}")
        if len(archivos) > 4:
            print(f"    ... y {len(archivos) - 4} más")
        print()
    filas = inventario()
    vacias = [n for n, _, arch, _ in filas if not arch]
    assert not vacias, f"etapas sin archivos: {vacias} (¿corriste 0.4 y los labs?)"
    assert sum(len(a) for _, _, a, _ in filas) >= 15, "esperaba ≥15 artefactos"
    print(f"total en disco: {total:,.0f} MB")
    print("ARCO COMPLETO: las 5 etapas tienen datos reales en tu máquina")
    return 0


if __name__ == "__main__":
    sys.exit(main())
