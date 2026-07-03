#!/usr/bin/env python3
"""Figuras de la clase 1.5 (leen data/resultados_1_5.json)."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

aca = Path(__file__).resolve().parent
d = json.load(open(aca.parent / "data" / "resultados_1_5.json"))
S = np.array(d["serie"])
t_min = (S[:, 0] - S[0, 0]) / 60.0
E, N, U = S[:, 1], S[:, 2], S[:, 3]
rms = d["rms_enu"]

# fig1: error ENU durante 1 hora
fig, ax = plt.subplots(figsize=(8.5, 4.4))
ax.plot(t_min, E, label=f"Este (RMS {rms[0]:.2f} m)", lw=1.3)
ax.plot(t_min, N, label=f"Norte (RMS {rms[1]:.2f} m)", lw=1.3)
ax.plot(t_min, U, label=f"Vertical (RMS {rms[2]:.2f} m)", lw=1.3)
ax.axhline(0, color="k", lw=0.8)
ax.set_xlabel("minutos desde las 12:00 UTC")
ax.set_ylabel("error vs coordenada oficial (m)")
ax.set_title("Fix Galileo iono-free en LPGS: una hora, época por época")
ax.grid(alpha=0.3)
ax.legend(fontsize=9)
fig.tight_layout()
fig.savefig(aca / "fig1_serie_enu.svg")

# fig2: dispersion horizontal
fig, ax = plt.subplots(figsize=(5.6, 5.6))
ax.scatter(E, N, s=14, alpha=0.6, label="fixes (121 épocas)")
ax.plot(0, 0, "r+", ms=14, mew=2.5, label="coordenada oficial IGS")
for r in (1, 2):
    ax.add_patch(plt.Circle((0, 0), r, fill=False, ls="--", color="gray"))
    ax.annotate(f"{r} m", (r * 0.71, r * 0.71), fontsize=8, color="gray")
ax.set_xlabel("Este (m)")
ax.set_ylabel("Norte (m)")
ax.set_title(f"Horizontal: RMS {np.hypot(rms[0], rms[1]):.2f} m")
ax.set_aspect("equal")
ax.set_xlim(-2.6, 2.6)
ax.set_ylim(-2.6, 2.6)
ax.grid(alpha=0.3)
ax.legend(fontsize=8, loc="lower left")
fig.tight_layout()
fig.savefig(aca / "fig2_dispersion.svg")

# fig3: la cascada de correcciones (log)
c = d["cascada"]
nombres = ["sin reloj del satélite", "sin Sagnac", "sin troposfera",
           "sin relatividad", "completo"]
vals = [c["sin_reloj_sat"], c["sin_sagnac"], c["sin_tropo"],
        c["sin_relatividad"], c["completo"]]
fig, ax = plt.subplots(figsize=(8.5, 4.2))
colores = ["tab:red"] * 4 + ["tab:green"]
bars = ax.barh(nombres, vals, color=colores)
ax.set_xscale("log")
for b, v in zip(bars, vals):
    txt = f"{v/1000:.0f} km" if v > 1000 else f"{v:.2f} m"
    ax.annotate(txt, (v, b.get_y() + b.get_height() / 2),
                va="center", ha="left", fontsize=9, xytext=(4, 0),
                textcoords="offset points")
ax.set_xlabel("error 3D de la época 12:00 (m, escala log)")
ax.set_title("Qué pasa si 'olvidás' cada corrección")
ax.set_xlim(0.5, 5e6)
ax.grid(alpha=0.3, axis="x", which="both")
fig.tight_layout()
fig.savefig(aca / "fig3_cascada.svg")
print("figuras escritas:", sorted(p.name for p in aca.glob("*.svg")))
