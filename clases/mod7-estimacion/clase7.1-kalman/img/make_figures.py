#!/usr/bin/env python3
"""Figuras 7.1 (leen data/resultados_7_1.json)."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

aca = Path(__file__).resolve().parent
d = json.load(open(aca.parent / "data" / "resultados_7_1.json"))
t = (np.array(d["series"]["t"]) - d["series"]["t"][0]) / 60.0
raw = np.array(d["series"]["serie_raw"])
kf = np.array(d["series"]["serie_kf"])

fig, axs = plt.subplots(3, 1, figsize=(9, 6), sharex=True)
for i, (ax, nombre) in enumerate(zip(axs, "ENU")):
    ax.plot(t, raw[:, i], ".", ms=3, color="#aaaaaa", label="LSQ crudo (1.5)")
    ax.plot(t, kf[:, i], "-", lw=1.4, color="#b03030", label="KF")
    ax.axhline(0, lw=0.6, color="k")
    ax.set_ylabel(f"{nombre} [m]")
    ax.grid(alpha=0.3)
axs[0].legend(fontsize=8, loc="upper right")
axs[0].set_title("La serie real del 1.5, cruda vs filtrada: el KF calma el ruido\ny confiesa el sesgo (lo que no vuelve a cero no era ruido)")
axs[2].set_xlabel("minutos desde 12:00")
fig.tight_layout()
fig.savefig(aca / "fig1_serie_kf.svg")

fig, ax = plt.subplots(figsize=(5.2, 5))
ax.plot(raw[:, 0], raw[:, 1], ".", ms=4, color="#aaaaaa", label="crudo")
ax.plot(kf[40:, 0], kf[40:, 1], ".", ms=4, color="#b03030", label="KF (convergido)")
ax.axhline(0, lw=0.6, color="k"); ax.axvline(0, lw=0.6, color="k")
ax.set_xlabel("E [m]"); ax.set_ylabel("N [m]"); ax.set_aspect("equal")
ax.grid(alpha=0.3); ax.legend(fontsize=8)
ax.set_title("Planta E-N: la nube se encoge ~×2\n(y queda corrida: el sesgo sobrevive)")
fig.tight_layout()
fig.savefig(aca / "fig2_nube_en.svg")
print("figuras escritas: ['fig1_serie_kf.svg', 'fig2_nube_en.svg']")
