#!/usr/bin/env python3
"""Figuras 5.1 (leen data/resultados_5_1.json)."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

aca = Path(__file__).resolve().parent
d = json.load(open(aca.parent / "data" / "resultados_5_1.json"))
T = np.array(d["T_serie"]); u = d["umbral"]

fig, ax = plt.subplots(figsize=(9, 3.4))
t = np.arange(len(T)) * 0.5
ax.plot(t, T, ".-", ms=3, lw=0.7, color="#205080")
ax.axhline(u, color="#b03030", lw=1.2)
ax.annotate(f"umbral {u:.1f} (Pfa=1e-3)", (1, u * 1.15), color="#b03030", fontsize=8)
ax.set_yscale("log")
ax.set_xlabel("minutos desde 12:00"); ax.set_ylabel("T (log)")
ax.set_title("El estadístico en la hora real: vive en ~3 (=dof), y las épocas\nque asoman no son falsas alarmas — son épocas sucias")
ax.grid(alpha=0.3, which="both")
fig.tight_layout()
fig.savefig(aca / "fig1_T_serie.svg")

bs = np.array(d["barrido_b"]); Tc = np.array(d["barrido_T"])
fig, ax = plt.subplots(figsize=(7.5, 3.6))
ax.plot(bs, Tc, "o-", ms=3, color="#205080")
ax.axhline(u, color="#b03030", lw=1.2)
ax.axvline(d["b_min"], ls="--", color="gray", lw=0.9)
ax.annotate(f"zona ciega ≤ {d['b_min']:.0f} m", (d["b_min"] + 0.7, 3), fontsize=8, color="gray")
ax.set_yscale("log")
ax.set_xlabel("bias inyectado [m]"); ax.set_ylabel("T (log)")
ax.set_title("T crece con b²: lo que cabe en el ruido, no dispara")
ax.grid(alpha=0.3, which="both")
fig.tight_layout()
fig.savefig(aca / "fig2_barrido_bias.svg")
print("figuras escritas: ['fig1_T_serie.svg', 'fig2_barrido_bias.svg']")
