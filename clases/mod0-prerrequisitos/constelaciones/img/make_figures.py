#!/usr/bin/env python3
"""Figuras de constelaciones (leen data/resultados_const.json)."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

aca = Path(__file__).resolve().parent
d = json.load(open(aca.parent / "data" / "resultados_const.json"))

# fig1: alturas y períodos medidos
tabla = {f[0]: f for f in d["tabla"]}
orden = ["GLONASS", "GPS", "BeiDou", "Galileo"]
alturas = [tabla[n][4] for n in orden]
periodos = [tabla[n][3] for n in orden]
fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.5, 3.8))
a1.bar(orden, alturas, color=["#d65f5f", "#4878cf", "#ee854a", "#6acc65"])
a1.set_ylabel("altura [km]")
a1.set_title("Cuatro respuestas al mismo problema\n(alturas medidas del BRDC)")
for i, v in enumerate(alturas):
    a1.annotate(f"{v:,.0f}".replace(",", " "), (i, v), ha="center", va="bottom", fontsize=8)
a2.bar(orden, periodos, color=["#d65f5f", "#4878cf", "#ee854a", "#6acc65"])
a2.set_ylabel("período [h]")
a2.axhline(11.967, ls="--", lw=0.8, color="gray")
a2.annotate("½ día sidéreo", (2.4, 12.05), fontsize=7, color="gray")
a2.set_title("Períodos: resonancias elegidas\na propósito")
for a in (a1, a2):
    a.tick_params(axis="x", labelsize=8)
fig.tight_layout()
fig.savefig(aca / "fig1_alturas_periodos.svg")

# fig2: censo del BRDC vs SP3
censo = d["censo"]
nombres = ["GPS", "Galileo", "GLONASS", "BeiDou", "QZSS", "NavIC", "SBAS"]
nav = [censo.get(n, 0) for n in nombres]
sp3 = {"GPS": 32, "Galileo": 30, "GLONASS": 21, "BeiDou": 30, "QZSS": 3,
       "NavIC": 0, "SBAS": 0}
fig, ax = plt.subplots(figsize=(8.5, 3.6))
x = range(len(nombres))
ax.bar([i - 0.2 for i in x], nav, 0.4, label="BRDC (todo lo emitido)", color="#4878cf")
ax.bar([i + 0.2 for i in x], [sp3[n] for n in nombres], 0.4,
       label="SP3 MGEX (lo ajustado)", color="#6acc65")
ax.set_xticks(list(x)); ax.set_xticklabels(nombres, fontsize=8)
ax.set_ylabel("satélites (día 166)")
ax.set_title("Emitir no es lo mismo que estar ajustado")
ax.legend(fontsize=8)
fig.tight_layout()
fig.savefig(aca / "fig2_censo_nav_vs_sp3.svg")
print("figuras escritas: ['fig1_alturas_periodos.svg', 'fig2_censo_nav_vs_sp3.svg']")
