#!/usr/bin/env python3
"""Figuras 4.2 (leen data/resultados_4_2.json)."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
aca = Path(__file__).resolve().parent
d = json.load(open(aca.parent/"data"/"resultados_4_2.json"))
sis = list(d.keys())
comp = ["R", "A", "C"]
x = np.arange(len(comp)); w = 0.35
fig, ax = plt.subplots(figsize=(7, 4))
for i, s in enumerate(sis):
    ax.bar(x + i*w, [d[s][c] for c in comp], w, label=f"{s} (3D {d[s]['3D']:.2f} m)")
ax.set_xticks(x + w/2); ax.set_xticklabels(["Radial", "Along-track", "Cross-track"])
ax.set_ylabel("RMS broadcast − SP3 (m)")
ax.set_title("Error de la efeméride broadcast por componente RTN")
ax.legend(fontsize=9); ax.grid(axis="y", alpha=0.3)
fig.tight_layout(); fig.savefig(aca/"fig1_rtn.svg")

fig, ax = plt.subplots(figsize=(6, 4))
b = ax.bar(sis, [d[s]["3D"] for s in sis], color=["#55a868", "#4878cf"])
for bi, s in zip(b, sis):
    ax.annotate(f"{d[s]['3D']:.2f} m", (bi.get_x()+bi.get_width()/2, d[s]["3D"]), ha="center", va="bottom")
ax.set_ylabel("diferencia 3D broadcast−SP3 (m)")
ax.set_title("Calidad de la órbita broadcast: Galileo vs GPS (día 166)")
ax.grid(axis="y", alpha=0.3); fig.tight_layout(); fig.savefig(aca/"fig2_galileo_vs_gps.svg")
print("figuras escritas: ['fig1_rtn.svg', 'fig2_galileo_vs_gps.svg']")
