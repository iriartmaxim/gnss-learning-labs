#!/usr/bin/env python3
"""Figura 5.4 (lee data/resultados_5_4.json)."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
aca = Path(__file__).resolve().parent
d = json.load(open(aca.parent/"data"/"resultados_5_4.json"))
solo = d["cobertura_por_capa"]; n = d["n"]
capas = sorted(solo, key=solo.get)
vals = [solo[c] for c in capas]
fig, ax = plt.subplots(figsize=(8, 4))
ax.barh(capas, vals, color="#4878cf", label="capa sola")
ax.axvline(d["combinada"], color="#55a868", lw=2, label=f"combinadas: {d['combinada']}/{n}")
ax.axvline(d["solo_usuario"], color="#c48", ls="--", lw=1.5, label=f"solo usuario: {d['solo_usuario']}/{n}")
ax.set_xlabel(f"escenarios detectados (de {n})")
ax.set_title("Cadena de integridad: ninguna capa sola cubre todo; la combinación sí")
ax.legend(fontsize=8); ax.set_xlim(0, n+0.3)
fig.tight_layout(); fig.savefig(aca/"fig1_capas.svg")
print("figuras escritas: ['fig1_capas.svg']")
