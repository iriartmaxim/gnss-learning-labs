#!/usr/bin/env python3
"""Figuras 4.3 (leen data/resultados_4_3.json)."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
aca = Path(__file__).resolve().parent
d = json.load(open(aca.parent/"data"/"resultados_4_3.json"))
allan = d["allan"]
svs = sorted(allan, key=allan.get)
vals = [allan[s] for s in svs]
fig, ax = plt.subplots(figsize=(9, 4))
col = ["#55a868" if v < 3e-11 else "#c44e52" for v in vals]
ax.bar(range(len(svs)), vals, color=col)
ax.set_yscale("log"); ax.set_xticks(range(len(svs))); ax.set_xticklabels(svs, rotation=90, fontsize=6)
ax.set_ylabel("estabilidad σy a 300 s (log)")
ax.set_title("Estabilidad de reloj por satélite Galileo: más estables (verde, ~PHM) vs menos (rojo, ~RAFS)")
ax.grid(axis="y", alpha=0.3, which="both")
fig.tight_layout(); fig.savefig(aca/"fig1_estabilidad.svg")

rms = d["rms_bc"]
fig, ax = plt.subplots(figsize=(6, 4))
ax.hist(list(rms.values()), bins=12, color="#4878cf", edgecolor="white")
ax.axvline(d["rms_med_m"], color="#c44", ls="--", label=f"mediana {d['rms_med_m']:.2f} m")
ax.set_xlabel("error broadcast−preciso (m, en rango)"); ax.set_ylabel("nº satélites")
ax.set_title("Cuán bien corrige el reloj broadcast (vs CLK preciso)")
ax.legend(fontsize=8); fig.tight_layout(); fig.savefig(aca/"fig2_error_reloj.svg")
print("figuras escritas: ['fig1_estabilidad.svg', 'fig2_error_reloj.svg']")
