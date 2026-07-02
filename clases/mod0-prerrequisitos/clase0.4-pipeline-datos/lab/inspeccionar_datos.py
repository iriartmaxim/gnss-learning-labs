#!/usr/bin/env python3
"""inspeccionar_datos.py — sanity check de lo bajado por tools/fetch_data.py.

Uso (desde la raiz del repo):
    python clases/mod0-prerrequisitos/clase0.4-pipeline-datos/lab/inspeccionar_datos.py data/raw/2026/166
"""
import sys
from collections import Counter
from pathlib import Path

carpeta = Path(sys.argv[1] if len(sys.argv) > 1 else "data/raw/2026/166")
nav = next(carpeta.glob("BRDC*_MN.rnx"))
sp3 = next(carpeta.glob("*ORB.SP3"))
nombres = {"G": "GPS", "E": "Galileo", "R": "GLONASS", "C": "BeiDou",
           "J": "QZSS", "I": "NavIC", "S": "SBAS"}

# 1) censo del RINEX nav crudo (sin librerias): 1 linea de cabecera por efemeride
print(f"== {nav.name}")
con = Counter()
with open(nav) as f:
    for linea in f:
        if linea[:1] in nombres and linea[1:3].isdigit():
            con[linea[0]] += 1
for c in sorted(con):
    print(f"  {nombres[c]:8s} {con[c]:6d} efemerides")

# 2) censo del SP3: satelites declarados en las lineas '+ ' del header
print(f"== {sp3.name}")
sats = []
for linea in open(sp3):
    if linea.startswith("+ "):
        campo = linea[9:60]
        sats += [campo[i:i + 3] for i in range(0, len(campo), 3)]
    if linea.startswith("++"):
        break
sats = [s for s in sats if s[:1] in nombres]
csp3 = Counter(s[0] for s in sats)
print(f"  {len(sats)} satelites: "
      + ", ".join(f"{nombres[c]} {n}" for c, n in sorted(csp3.items())))

# 3) georinex: parsear SOLO Galileo del nav y listar SVs unicos
import georinex as gr
print("== georinex (solo Galileo; puede tardar ~1 min)")
ds = gr.load(nav, use="E")
svs = sorted({str(s) for s in ds.sv.values})
base = sorted({s.split("_")[0] for s in svs})
print(f"  {len(base)} satelites Galileo unicos ({len(svs)} registros; los sufijos")
print("  _N que agrega georinex son mensajes duplicados del mismo sv/epoca,")
print("  p.ej. I/NAV vs F/NAV -- ojo con esto en la clase 1.3):")
print("  " + " ".join(base))
print(f"  ventana: {str(ds.time.values.min())[:19]} .. {str(ds.time.values.max())[:19]}")
print("\nLISTO: datos reales verificados, pipeline 0.4 OK")
