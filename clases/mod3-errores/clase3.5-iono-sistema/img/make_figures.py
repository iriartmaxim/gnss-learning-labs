#!/usr/bin/env python3
"""Figura 3.5 (lee data/resultados_3_5.json)."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
aca = Path(__file__).resolve().parent
d = json.load(open(aca.parent/"data"/"resultados_3_5.json"))
fig, ax = plt.subplots(figsize=(7, 4))
ax.hist(d["vtecs"], bins=25, color="#4878cf", edgecolor="white")
ax.axvline(d["vtec_med"], color="#c44", ls="--", label=f"mediana {d['vtec_med']:.1f} TECU")
ax.set_xlabel("VTEC (TECU)"); ax.set_ylabel("nº muestras")
ax.set_title("VTEC sobre LPGS desde doble frecuencia — la semilla del mapa TEC")
ax.legend(fontsize=8); fig.tight_layout(); fig.savefig(aca/"fig1_vtec.svg")
print("figuras escritas: ['fig1_vtec.svg']")
