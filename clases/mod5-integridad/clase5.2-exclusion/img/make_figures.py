#!/usr/bin/env python3
"""Figuras 5.2 (leen data/resultados_5_2.json)."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

aca = Path(__file__).resolve().parent
d = json.load(open(aca.parent / "data" / "resultados_5_2.json"))
subs = d["subconjuntos"]
noms = [s[0] for s in subs]; Ts = [s[1] for s in subs]; errs = [s[2] for s in subs]

fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 3.8))
cols = ["#b03030" if n == d["culpable"] else "#4878cf" for n in noms]
a1.bar(noms, Ts, color=cols)
a1.axhline(16.3, color="gray", ls="--", lw=0.9)
a1.set_yscale("log"); a1.set_ylabel("T del subconjunto (log)")
a1.set_title(f"Leave-one-out con bias {d['bias']:.0f} m en {d['culpable']}:\nsolo el subconjunto sin el culpable se desploma")
a2.bar(noms, errs, color=["#ee854a" if n == "E30" else "#999999" for n in noms])
a2.set_ylabel("error 3D del subconjunto [m]")
a2.set_title("La trampa del inocente: excluir a E30\nbaja T… y triplica el daño (83 m)")
for a in (a1, a2):
    a.tick_params(axis="x", labelsize=8, rotation=45)
    a.grid(alpha=0.3, axis="y")
fig.tight_layout()
fig.savefig(aca / "fig1_subconjuntos.svg")
print("figuras escritas: ['fig1_subconjuntos.svg']")
