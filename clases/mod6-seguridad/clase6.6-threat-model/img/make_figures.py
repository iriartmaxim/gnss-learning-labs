#!/usr/bin/env python3
"""Figura 6.6 (lee data/resultados_6_6.json)."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
aca = Path(__file__).resolve().parent
d = json.load(open(aca.parent/"data"/"resultados_6_6.json"))
amen = d["amenazas"]; capas = ["OSNMA","SAS/ACAS","detectores_6.4","fisica_4.1"]
ataques = list(amen.keys())
M = np.array([[1 if amen[a].get(c) else 0 for c in capas] for a in ataques])
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.imshow(M, cmap="Greens", aspect="auto", vmin=0, vmax=1.4)
ax.set_xticks(range(len(capas))); ax.set_xticklabels(capas, fontsize=8)
ax.set_yticks(range(len(ataques)))
ax.set_yticklabels([a.split("(")[0].strip() for a in ataques], fontsize=7)
for i in range(len(ataques)):
    for j in range(len(capas)):
        ax.text(j, i, "✓" if M[i, j] else "·", ha="center", va="center",
                color="#155" if M[i, j] else "#bbb", fontsize=12)
ax.set_title("Threat model OSNMA/SAS: qué capa mitiga qué ataque\n(defensa en capas — ninguna cubre todo)")
fig.tight_layout(); fig.savefig(aca/"fig1_matriz.svg")
print("figuras escritas: ['fig1_matriz.svg']")
