#!/usr/bin/env python3
"""Figuras de la clase 3.1 (leen data/resultados_3_1.json)."""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

aca = Path(__file__).resolve().parent
d = json.load(open(aca.parent / "data" / "resultados_3_1.json"))

# reusar el modelo de la solucion para curvas a otras elevaciones
sys.path.insert(0, str(aca.parent / "lab" / "soluciones"))
from lab_klobuchar_solucion import klobuchar, oblicuidad, LAT, LON

alpha, beta = d["coef"]["GPSA"], d["coef"]["GPSB"]
h_utc = np.array(d["curva_horas_utc"])
h_loc = (h_utc + LON / 15.0) % 24
orden = np.argsort(h_loc)

# fig1: curva diurna a varias elevaciones, en hora LOCAL
fig, ax = plt.subplots(figsize=(9, 4.5))
for e, color in [(90, "tab:blue"), (30, "tab:orange"), (15, "tab:red")]:
    v = np.array([klobuchar(LAT, LON, e, 0, h * 3600, alpha, beta)
                  for h in h_utc])
    ax.plot(h_loc[orden], v[orden], lw=1.6, color=color,
            label=f"elevacion {e} grados")
ax.axvline(14, color="gray", ls="--", lw=1, label="14:00 local (pico)")
ax.set_xlabel("hora local")
ax.set_ylabel("retardo ionosferico L1/E1 (m)")
ax.set_title("Klobuchar con coeficientes reales (dia 166/2026, La Plata): "
             "coseno diurno + piso nocturno de 5 ns")
ax.set_xlim(0, 24)
ax.set_xticks(range(0, 25, 2))
ax.legend(fontsize=8)
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(aca / "fig1_curva_diurna.svg")

# fig2: factor de oblicuidad + satelites reales de la 1.5
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
ee = np.linspace(5, 90, 200)
a1.plot(ee, oblicuidad(ee), lw=1.8, color="tab:purple")
for e in (90, 30, 15, 5):
    a1.plot(e, oblicuidad(e), "o", color="tab:red", ms=5)
    a1.annotate(f"F={oblicuidad(e):.2f}", (e, oblicuidad(e)),
                textcoords="offset points", xytext=(6, 6), fontsize=8)
a1.set_xlabel("elevacion (grados)")
a1.set_ylabel("factor de oblicuidad F")
a1.set_title("El rayo oblicuo atraviesa mas ionosfera:\nF(5 grados) ~ 3x el retardo cenital")
a1.grid(alpha=0.3)

sats = d["iono_sats_1_5"]
nombres = [s["sv"] for s in sats]
elevs = [s["elev"] for s in sats]
ionos = [s["iono_m"] for s in sats]
idx = np.argsort(elevs)
a2.bar(range(len(sats)), [ionos[i] for i in idx], color="tab:green")
a2.set_xticks(range(len(sats)))
a2.set_xticklabels([f"{nombres[i]}\n{elevs[i]:.0f}" for i in idx], fontsize=8)
a2.set_xlabel("satelite (elevacion en grados)")
a2.set_ylabel("retardo iono estimado (m)")
a2.set_title("Los 8 Galileo de la clase 1.5 (12:00 UTC):\nlo que iono-free elimino por construccion")
for j, i in enumerate(idx):
    a2.text(j, ionos[i], f"{ionos[i]:.1f}", ha="center", va="bottom", fontsize=8)
a2.grid(alpha=0.3, axis="y")
fig.tight_layout()
fig.savefig(aca / "fig2_oblicuidad_sats.svg")

# fig3: mapa hora local x elevacion del retardo (estructura completa)
fig, ax = plt.subplots(figsize=(9, 4.5))
hh = np.arange(0, 24.1, 0.25)
eg = np.arange(5, 91, 2)
M = np.zeros((eg.size, hh.size))
for i, e in enumerate(eg):
    for j, h in enumerate(hh):
        # hh es hora LOCAL: convertir a UTC para el modelo
        h_utc_ij = (h - LON / 15.0) % 24
        M[i, j] = klobuchar(LAT, LON, e, 0, h_utc_ij * 3600, alpha, beta)
im = ax.pcolormesh(hh, eg, M, shading="auto", cmap="viridis")
fig.colorbar(im, ax=ax, label="retardo (m)")
ax.set_xlabel("hora local")
ax.set_ylabel("elevacion (grados)")
ax.set_title("Retardo Klobuchar (m): lo peor es baja elevacion "
             "a primera hora de la tarde")
fig.tight_layout()
fig.savefig(aca / "fig3_mapa_hora_elev.svg")
print("figuras escritas:", sorted(p.name for p in aca.glob("*.svg")))
