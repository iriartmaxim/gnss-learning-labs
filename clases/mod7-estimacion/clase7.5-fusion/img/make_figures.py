#!/usr/bin/env python3
"""Figuras 7.5 (leen data/resultados_7_5.json)."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
aca = Path(__file__).resolve().parent
d = json.load(open(aca.parent/"data"/"resultados_7_5.json"))
t = np.array(d["t"])
# fig1: error vs tiempo con el corte sombreado
fig, ax = plt.subplots(figsize=(8, 4))
ax.axvspan(d["corte"][0], d["corte"][1], color="#f2d0d0", alpha=0.6, label="corte GNSS")
ax.plot(t, d["err_ins"], color="#c44e52", lw=1, label="INS solo (deriva)")
ax.plot(t, d["err_kf"], color="#55a868", lw=1.3, label="fusión KF")
ax.set_xlabel("tiempo (s)"); ax.set_ylabel("error de posición (m)")
ax.set_title("El INS deriva; el KF lo acota — sobre todo durante el corte")
ax.set_ylim(0, min(150, max(d["err_ins"])*1.05)); ax.legend(fontsize=8); ax.grid(alpha=0.3)
fig.tight_layout(); fig.savefig(aca/"fig1_error_tiempo.svg")
# fig2: trayectoria
fig, ax = plt.subplots(figsize=(7, 5))
ax.plot(d["px"], d["py"], color="#333", lw=2, label="verdad")
ax.plot(d["insx"], d["insy"], color="#c44e52", lw=1, ls="--", label="INS solo")
ax.plot(d["kfx"], d["kfy"], color="#55a868", lw=1.2, label="fusión KF")
ax.set_xlabel("Este (m)"); ax.set_ylabel("Norte (m)")
ax.set_title("Trayectoria: la fusión sigue la verdad; el INS se va")
ax.legend(fontsize=8); ax.axis("equal"); ax.grid(alpha=0.3)
fig.tight_layout(); fig.savefig(aca/"fig2_trayectoria.svg")
print("figuras escritas: ['fig1_error_tiempo.svg', 'fig2_trayectoria.svg']")
