#!/usr/bin/env python3
"""Figura 8.1 (lee data/resultados_8_1.json)."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
aca = Path(__file__).resolve().parent
d = json.load(open(aca.parent/"data"/"resultados_8_1.json"))
meo = d["MEO (Galileo)"]; leo = d["LEO-PNT"]
fig, axs = plt.subplots(1, 3, figsize=(11, 3.4))
for ax, key, tit, unit in [(axs[0],"periodo_h","Período orbital","h"),
                           (axs[1],"vel_kms","Velocidad","km/s"),
                           (axs[2],"doppler_khz","Doppler máx L1","kHz")]:
    ax.bar(["MEO","LEO"], [meo[key], leo[key]], color=["#4878cf","#c44e52"])
    ax.set_title(tit); ax.set_ylabel(unit)
    for i,v in enumerate([meo[key], leo[key]]):
        ax.annotate(f"{v:.1f}", (i, v), ha="center", va="bottom", fontsize=8)
fig.suptitle(f"LEO-PNT vs MEO: +{d['ganancia_potencia_db']:.0f} dB de potencia, "
             f"pero Doppler y hand-over mucho peores", fontsize=11)
fig.tight_layout(); fig.savefig(aca/"fig1_leo_vs_meo.svg")
print("figuras escritas: ['fig1_leo_vs_meo.svg']")
