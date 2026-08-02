#!/usr/bin/env python3
"""Figuras 7.4 (leen data/resultados_7_4.json)."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
aca = Path(__file__).resolve().parent
d = json.load(open(aca.parent/"data"/"resultados_7_4.json"))
# fig1: RMS vs ZWD (la parábola de estimación)
fig, ax = plt.subplots(figsize=(6.5, 4))
ax.plot(np.array(d["grid_zwd"])*100, d["grid_rms"], "-o", ms=3, color="#205080")
zb = d["zwd_cm"]; ax.axvline(zb, color="#c44", ls="--", label=f"ZWD óptimo {zb:.0f} cm")
ax.axhline(d["ref_broadcast"], color="#888", ls=":", label="broadcast 1.95 m")
ax.set_xlabel("ZWD (cm)"); ax.set_ylabel("RMS 3D (m)")
ax.set_title("PPP-lite: RMS vs retardo húmedo estimado (batch)")
ax.legend(fontsize=8); ax.grid(alpha=0.3); fig.tight_layout()
fig.savefig(aca/"fig1_zwd.svg")
# fig2: comparación de barras
fig, ax = plt.subplots(figsize=(6, 4))
vals = [d["ref_broadcast"], d["rms_zwd0"], d["rms_best"]]
b = ax.bar(["broadcast\n(1.5)", "PPP-lite\nZWD=0", "PPP-lite\nZWD óptimo"], vals,
           color=["#888", "#4878cf", "#55a868"])
for bi, v in zip(b, vals):
    ax.annotate(f"{v:.2f}", (bi.get_x()+bi.get_width()/2, v), ha="center", va="bottom")
ax.set_ylabel("RMS 3D (m)"); ax.set_title("Productos precisos vs broadcast (solo código)")
ax.grid(axis="y", alpha=0.3); fig.tight_layout(); fig.savefig(aca/"fig2_barras.svg")
print("figuras escritas: ['fig1_zwd.svg', 'fig2_barras.svg']")
