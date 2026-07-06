#!/usr/bin/env python3
"""Figuras de la clase 4.1 (leen data/resultados_4_1.json)."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

aca = Path(__file__).resolve().parent
d = json.load(open(aca.parent / "data" / "resultados_4_1.json"))
t = np.array(d["tks_min"])

# fig1: residuo de cada correccion en el arco +-2 h
fig, ax = plt.subplots(figsize=(9, 5))
estilos = {
    "sin_deltan": ("corrección Δn (movimiento medio)", "tab:red", "-"),
    "sin_armonicos": ("armónicos Cxx (J2 y período corto)", "tab:blue", "-"),
    "sin_idot": ("deriva de inclinación (luni-solar)", "tab:green", "-"),
    "solo_2cuerpos": ("elipse pura (todo apagado)", "black", "--"),
}
for k, (lab, col, ls) in estilos.items():
    ax.plot(t, d["series"][k], color=col, ls=ls, lw=1.8, label=lab)
ax.axvline(0, color="gray", lw=0.6)
ax.annotate("Toe", (0, ax.get_ylim()[1]*0.94), fontsize=8, color="gray")
ax.set_xlabel("tiempo desde Toe (minutos)")
ax.set_ylabel("residuo posicional vs broadcast completa (m)")
ax.set_title(f"Qué corrige cada parche del ICD — {d['sv']}, órbita Galileo\n"
             f"(a={d['a_km']:.0f} km, i={d['inc_deg']:.1f}°): "
             "cada término tiene su firma temporal")
ax.legend(fontsize=8)
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(aca / "fig1_correcciones.svg")

# fig2: el salto en Toe (armonicos no se anulan) vs los que si
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.3),
                             gridspec_kw={"width_ratios": [3, 2]})
pa = d["parte_a"]
nombres = ["Δn\n(mov. medio)", "armónicos\n(J2, Cxx)", "IDOT\n(luni-solar)",
           "elipse pura\n(todo)"]
claves = ["sin_deltan", "sin_armonicos", "sin_idot", "solo_2cuerpos"]
maxv = [pa[k]["max_m"] for k in claves]
toev = [pa[k]["en_toe_m"] for k in claves]
xx = np.arange(4)
a1.bar(xx - 0.19, maxv, 0.38, label="máximo en el arco ±2 h", color="tab:blue")
a1.bar(xx + 0.19, toev, 0.38, label="en el instante Toe", color="tab:orange")
for i in range(4):
    a1.text(xx[i]-0.19, maxv[i], f"{maxv[i]:.0f}", ha="center", va="bottom",
            fontsize=8)
    a1.text(xx[i]+0.19, toev[i], f"{toev[i]:.0f}", ha="center", va="bottom",
            fontsize=8)
a1.set_xticks(xx)
a1.set_xticklabels(nombres, fontsize=8)
a1.set_ylabel("residuo posicional (m)")
a1.set_title("En Toe, Δn e IDOT se anulan (dependen de tk);\n"
             "los armónicos NO (el achatamiento actúa siempre)")
a1.legend(fontsize=8)
a1.grid(alpha=0.3, axis="y")

a2.bar([0], [d["empalme_medio_m"]], 0.5, color="tab:green",
       label=f"medio {d['empalme_medio_m']:.2f} m")
a2.bar([1], [d["empalme_max_m"]], 0.5, color="tab:olive",
       label=f"máximo {d['empalme_max_m']:.2f} m")
a2.set_xticks([0, 1])
a2.set_xticklabels(["salto medio", "salto máx"])
a2.set_ylabel("discontinuidad en el empalme (m)")
a2.set_title(f"El salto entre efemérides consecutivas\n"
             f"({d['n_empalmes']} empalmes de {d['sv']}): sub-métrico")
a2.legend(fontsize=8)
a2.grid(alpha=0.3, axis="y")
fig.tight_layout()
fig.savefig(aca / "fig2_toe_empalme.svg")

# fig3: extrapolacion del kepleriano puro a 12 h
h = np.array(d["extrap_h"])
dp = np.array(d["extrap_puro_m"])
fig, ax = plt.subplots(figsize=(9, 5))
ax.plot(h, dp / 1000, lw=2, color="tab:red")
ax.fill_between(h, 0, dp / 1000, alpha=0.1, color="tab:red")
for hh in (2, 6, 12):
    v = np.interp(hh, h, dp)
    ax.plot(hh, v/1000, "o", color="tab:red", ms=5)
    ax.annotate(f"{v:.0f} m", (hh, v/1000), textcoords="offset points",
                xytext=(6, 6), fontsize=9)
ax.axhspan(0, 0.01, color="tab:green", alpha=0.2)
ax.annotate("validez broadcast (~3 h)", (3, 0.3), fontsize=8, color="gray")
ax.axvline(3, color="gray", ls=":", lw=1)
ax.set_xlabel("horas extrapoladas desde Toe")
ax.set_ylabel("error del kepleriano puro (km)")
ax.set_title("Por qué la broadcast se re-emite cada ~3 h:\n"
             "la elipse de dos cuerpos acumula kilómetros en medio día")
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(aca / "fig3_extrapolacion.svg")
print("figuras escritas:", sorted(p.name for p in aca.glob("*.svg")))
