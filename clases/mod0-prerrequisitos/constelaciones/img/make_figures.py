#!/usr/bin/env python3
"""Figuras de la clase constelaciones. Regenerar: python3 make_figures.py"""
import matplotlib
matplotlib.use("Agg")
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

aca = Path(__file__).resolve().parent

# datos reales del censo BRDC 2026-06-15 (día 166)
sist = ["GPS", "GLONASS", "Galileo", "BeiDou"]
svs = [32, 27, 30, 37]
alt_km = {"GPS": 20180, "GLONASS": 19130, "Galileo": 23222, "BeiDou": 21528}

# fig1: censo por sistema global
fig, ax = plt.subplots(figsize=(7, 3.6))
col = ["#4878cf", "#c44e52", "#55a868", "#d9a441"]
b = ax.bar(sist, svs, color=col)
for bi, v in zip(b, svs):
    ax.annotate(str(v), (bi.get_x() + bi.get_width()/2, v), ha="center", va="bottom")
ax.set_ylabel("SVs únicos en el BRDC (día 166)")
ax.set_title("Los cuatro GNSS globales: satélites emitiendo el 2026-06-15")
ax.set_ylim(0, 42); ax.grid(axis="y", alpha=0.3)
fig.tight_layout(); fig.savefig(aca / "fig1_censo_constelaciones.svg")

# fig2: altitud orbital comparada (MEO)
fig, ax = plt.subplots(figsize=(7, 3.6))
alts = [alt_km[s] for s in sist]
b = ax.barh(sist, alts, color=col)
for bi, v in zip(b, alts):
    ax.annotate(f"{v:,} km".replace(",", " "), (v, bi.get_y()+bi.get_height()/2),
                va="center", ha="right", color="white", fontsize=8)
ax.axvline(20180, ls="--", c="#333", lw=0.8)
ax.set_xlabel("altitud orbital (km)")
ax.set_title("Todas MEO, pero a distinta altura → distinto período y ground track")
ax.set_xlim(0, 26000); fig.tight_layout()
fig.savefig(aca / "fig2_altitudes.svg")
print("figuras escritas: ['fig1_censo_constelaciones.svg', 'fig2_altitudes.svg']")
