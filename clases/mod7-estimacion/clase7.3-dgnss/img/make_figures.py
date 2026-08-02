#!/usr/bin/env python3
"""Figuras 7.3 (leen data/resultados_7_3.json)."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

aca = Path(__file__).resolve().parent
d = json.load(open(aca.parent / "data" / "resultados_7_3.json"))

fig, ax = plt.subplots(figsize=(6, 4))
b = ax.bar(["standalone\n(E1 solo)", "DGNSS\n(PRC de LPGS)"],
           [d["rms_solo"], d["rms_dgnss"]], color=["#c44e52", "#55a868"])
for bi, v in zip(b, [d["rms_solo"], d["rms_dgnss"]]):
    ax.annotate(f"{v:.2f} m", (bi.get_x()+bi.get_width()/2, v), ha="center", va="bottom")
ax.set_ylabel("RMS 3D del rover (CORD)")
ax.set_title(f"DGNSS baseline {d['baseline_km']:.0f} km — mejora {d['mejora_pct']:.0f}%")
ax.grid(axis="y", alpha=0.3)
fig.tight_layout(); fig.savefig(aca / "fig1_dgnss_mejora.svg")

fig, ax = plt.subplots(figsize=(7, 3))
ax.plot([0, 7.15], [0, 0], "o-", color="#333", lw=1.5)
ax.annotate("LPGS\n(base, coords conocidas)", (0, 0), textcoords="offset points",
            xytext=(0, 12), ha="center", fontsize=9, color="#205080")
ax.annotate("CORD\n(rover)", (7.15, 0), textcoords="offset points",
            xytext=(0, 12), ha="center", fontsize=9, color="#a44")
ax.annotate("715 km", (3.57, 0), textcoords="offset points", xytext=(0, -22),
            ha="center", fontsize=10, weight="bold")
ax.text(3.57, -0.6, "reloj/orbita: se cancelan (comunes)\niono/tropo: decorrelacionan -> residual ~1 m",
        ha="center", fontsize=8, color="#555")
ax.set_xlim(-1.5, 8.5); ax.set_ylim(-1.2, 1); ax.axis("off")
ax.set_title("Baseline largo: por que DGNSS operativo usa distancias cortas")
fig.tight_layout(); fig.savefig(aca / "fig2_baseline.svg")
print("figuras escritas: ['fig1_dgnss_mejora.svg', 'fig2_baseline.svg']")
