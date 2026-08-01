#!/usr/bin/env python3
"""Figuras 5.3 (leen data/resultados_5_3.json)."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

aca = Path(__file__).resolve().parent
d = json.load(open(aca.parent / "data" / "resultados_5_3.json"))

# fig1: el "triángulo de Stanford" simplificado — PL vs AL
fig, ax = plt.subplots(figsize=(5.5, 5.5))
AL = d["VAL"]
ax.axhspan(0, AL, xmin=0, xmax=AL/60, color="#d8ecd8", alpha=0.6)
ax.axhline(AL, color="#c44", ls="--", lw=1)
ax.axvline(AL, color="#c44", ls="--", lw=1)
ax.text(AL/2, AL*0.5, "DISPONIBLE\n(PL < AL)", ha="center", va="center", fontsize=9, color="#2a6")
ax.text(AL*1.25, AL*0.5, "no disponible", ha="center", va="center", fontsize=8, color="#a44")
# nuestra operación: VPL mediana y máx como puntos
ax.scatter([d["vpl_med"]], [1], s=60, color="#205080", zorder=5, label=f"VPL mediana {d['vpl_med']:.1f} m")
ax.scatter([d["vpl_max"]], [1], s=60, marker="x", color="#205080", zorder=5, label=f"VPL máx {d['vpl_max']:.1f} m")
ax.set_xlabel("Vertical Protection Level (m)")
ax.set_ylabel("(operación LPV-200)")
ax.set_title(f"VPL vs VAL={AL:.0f} m — disponibilidad {d['disponibilidad']:.0f}%")
ax.set_xlim(0, 60); ax.set_ylim(0, 3); ax.set_yticks([])
ax.legend(fontsize=8, loc="upper right")
fig.tight_layout(); fig.savefig(aca / "fig1_stanford.svg")

# fig2: HPL vs VPL con sus alert limits
fig, ax = plt.subplots(figsize=(6, 4))
ax.bar(["HPL\nmediana", "HAL", "VPL\nmediana", "VAL"],
       [d["hpl_med"], d["HAL"], d["vpl_med"], d["VAL"]],
       color=["#4878cf", "#c44e52", "#55a868", "#c44e52"])
ax.set_ylabel("metros")
ax.set_title("Protection levels vs alert limits (LPV-200)")
ax.grid(axis="y", alpha=0.3)
fig.tight_layout(); fig.savefig(aca / "fig2_pl_vs_al.svg")
print("figuras escritas: ['fig1_stanford.svg', 'fig2_pl_vs_al.svg']")
