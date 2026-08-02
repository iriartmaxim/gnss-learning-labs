#!/usr/bin/env python3
"""Figuras 6.3 (leen data/resultados_6_3.json)."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
aca = Path(__file__).resolve().parent
d = json.load(open(aca.parent/"data"/"resultados_6_3.json"))
fig, ax = plt.subplots(figsize=(9, 4))
ax.plot(d["caf_limpio"], color="#55a868", lw=1, label="limpio (1 pico)")
ax.plot(d["caf_atacado"], color="#c44e52", lw=1.2, label="atacado (2 picos)")
for p in d["picos_atacado"]:
    ax.annotate("", xy=(p, d["caf_atacado"][p]), xytext=(p, d["caf_atacado"][p]+0.3),
                arrowprops=dict(arrowstyle="->", color="#333"))
ax.text(d["picos_atacado"][0], max(d["caf_atacado"])*0.6, "auténtico", fontsize=8, ha="center")
ax.text(d["picos_atacado"][1], max(d["caf_atacado"])*0.95, "FALSO\n(más fuerte)", fontsize=8, ha="center", color="#c44")
ax.set_xlabel("desfase de código (chips)"); ax.set_ylabel("correlación")
ax.set_title(f"Firma del spoofing: doble pico en la CAF (falso {d['razon']:.2f}× el auténtico)")
ax.legend(fontsize=8); ax.set_xlim(60, 200); fig.tight_layout()
fig.savefig(aca/"fig1_doble_pico.svg")
print("figuras escritas: ['fig1_doble_pico.svg']")
