#!/usr/bin/env python3
"""Figuras de la clase 1.3 (leen data/resultados_1_3.json de la solucion)."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

aca = Path(__file__).resolve().parent
d = json.load(open(aca.parent / "data" / "resultados_1_3.json"))
dt = np.array([p[0] for p in d["curva"]])
err = np.array([p[1] for p in d["curva"]])
sv = d["sv"]

# fig1: la efemeride que envejece (escala log, +-12 h)
fig, ax = plt.subplots(figsize=(8, 4.6))
ax.semilogy(dt, err, lw=1.4)
ax.axvspan(-1, 1, alpha=0.18, color="tab:green", label="±1 h (validez nominal)")
ax.axvspan(-2, 2, alpha=0.10, color="tab:orange", label="±2 h")
for h, v in ((1, 1.9), (2, 13.7), (6, 405.9), (12, 569.2)):
    ax.annotate(f"{v:g} m", xy=(h, v), xytext=(h + 0.4, v * 1.8), fontsize=9)
ax.set_xlabel("t − Toe (horas)")
ax.set_ylabel(f"|error broadcast − SP3| de {sv} (m)")
ax.set_title("Una efemérides no es para siempre: error al envejecer")
ax.grid(alpha=0.3, which="both")
ax.legend(loc="upper left", fontsize=9)
fig.tight_layout()
fig.savefig(aca / "fig1_envejecimiento.svg")

# fig2: zoom al intervalo de ajuste (lineal)
m = np.abs(dt) <= 2.2
fig, ax = plt.subplots(figsize=(8, 4.2))
ax.plot(dt[m], err[m], "o-", ms=3.5, lw=1.2)
ax.axhline(0.91, ls="--", color="tab:green", lw=1,
           label="RMS ±1 h = 0.91 m")
ax.set_xlabel("t − Toe (horas)")
ax.set_ylabel("|error| (m)")
ax.set_title(f"Dentro del ajuste, el broadcast de {sv} es métrico")
ax.grid(alpha=0.3)
ax.legend(fontsize=9)
fig.tight_layout()
fig.savefig(aca / "fig2_intervalo_ajuste.svg")

# fig3: RMS por satelite (toda la constelacion, +-1 h)
svs = sorted(d["tabla"])
rms = [d["tabla"][s] for s in svs]
med = float(np.median(rms))
fig, ax = plt.subplots(figsize=(9.5, 4.2))
colores = ["tab:red" if r == max(rms) else "tab:blue" for r in rms]
ax.bar(svs, rms, color=colores)
ax.axhline(med, ls="--", color="k", lw=1, label=f"mediana {med:.2f} m")
ax.set_ylabel("RMS 3D vs SP3, ±1 h (m)")
ax.set_title("Los 30 Galileo activos: broadcast metro-nivel en toda la constelación")
ax.tick_params(axis="x", rotation=60, labelsize=8)
ax.grid(alpha=0.3, axis="y")
ax.legend(fontsize=9)
fig.tight_layout()
fig.savefig(aca / "fig3_constelacion.svg")
print("figuras escritas:", sorted(p.name for p in aca.glob("*.svg")))
