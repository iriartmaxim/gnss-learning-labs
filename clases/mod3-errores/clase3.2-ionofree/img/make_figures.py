#!/usr/bin/env python3
"""Figuras de la clase 3.2 (leen data/resultados_3_2.json)."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

aca = Path(__file__).resolve().parent
d = json.load(open(aca.parent / "data" / "resultados_3_2.json"))

# fig1: iono medida (divergencia) vs Klobuchar, por satelite
t = d["tabla_12"]
x = np.arange(len(t))
fig, ax = plt.subplots(figsize=(9, 4.5))
ax.bar(x - 0.2, [s["iono_med_m"] for s in t], 0.4,
       label="medida: (P5$-$P1)/($\\gamma$$-$1) $-$ c·BGD", color="tab:blue")
ax.bar(x + 0.2, [s["iono_klo_m"] for s in t], 0.4,
       label="modelo Klobuchar (3.1)", color="tab:orange")
ax.set_xticks(x)
ax.set_xticklabels([f"{s['sv']}\n{s['elev']:.0f}°" for s in t], fontsize=8)
ax.set_xlabel("satélite (elevación) — ordenados de más bajo a más alto")
ax.set_ylabel("retardo iono en E1 (m)")
ax.set_title("12:00 UTC: la ionosfera MEDIDA con doble frecuencia vs el "
             f"modelo\n(offset común DCB rx ≈ {d['dcb_rx_m']:+.2f} m; "
             "residual RMS 1.27 m = lo que Klobuchar no ve)")
ax.legend(fontsize=9)
ax.grid(alpha=0.3, axis="y")
fig.tight_layout()
fig.savefig(aca / "fig1_medida_vs_klobuchar.svg")

# fig2: PVT en tres sabores — RMS por componente
sab = [("e1", "E1 crudo\n(sin iono)", "tab:red"),
       ("e1klo", "E1 +\nKlobuchar", "tab:orange"),
       ("if", "iono-free\nE1/E5a", "tab:blue")]
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.3),
                             gridspec_kw={"width_ratios": [3, 2]})
xx = np.arange(3)
for i, (k, lab, col) in enumerate(sab):
    r = d["rms_enu"][k]
    a1.bar(xx + (i - 1) * 0.25, r, 0.25, label=lab.replace("\n", " "),
           color=col)
    for j, v in enumerate(r):
        a1.text(xx[j] + (i - 1) * 0.25, v, f"{v:.2f}", ha="center",
                va="bottom", fontsize=7)
a1.set_xticks(xx)
a1.set_xticklabels(["Este", "Norte", "Vertical"])
a1.set_ylabel("RMS del error (m)")
a1.set_title("El PVT en tres sabores (60 fixes, 12:00–13:00):\n"
             "la ionosfera pega casi toda en la VERTICAL")
a1.legend(fontsize=8)
a1.grid(alpha=0.3, axis="y")

rr = d["res_rms"]
a2.bar(range(3), [rr["e1"], rr["e1klo"], rr["if"]],
       color=[c for _, _, c in sab])
a2.set_xticks(range(3))
a2.set_xticklabels([lab for _, lab, _ in sab], fontsize=8)
a2.set_ylabel("RMS de los residuos post-fit (m)")
k_emp = rr["if"] / rr["e1"]
a2.set_title(f"El precio del iono-free: ruido\n×{d['k_teorico']:.2f} teórico, "
             f"×{k_emp:.2f} en los residuos")
for j, v in enumerate([rr["e1"], rr["e1klo"], rr["if"]]):
    a2.text(j, v, f"{v:.2f}", ha="center", va="bottom", fontsize=8)
a2.grid(alpha=0.3, axis="y")
fig.tight_layout()
fig.savefig(aca / "fig2_tres_sabores.svg")

# fig3: la serie I1(t) por satelite (solo si el JSON trae las series)
if "serie_iono" in d:
    fig, ax = plt.subplots(figsize=(9, 4.5))
    tt = (np.array(d["serie_t_sod"]) / 3600.0)
    for sv, vals in sorted(d["serie_iono"].items()):
        v = np.array(vals, dtype=float)
        ax.plot(tt, v, lw=1.1, label=sv)
    ax.set_xlabel("hora UTC (≈ hora local + 4)")
    ax.set_ylabel("retardo iono medido en E1 (m)")
    ax.set_title("I$_1$(t) por la divergencia de código, 12:00–13:00 UTC:\n"
                 "tendencias suaves (la iono) + ruido ~1 m (el código) — "
                 "E33 se dispara al caer al horizonte")
    ax.legend(fontsize=7, ncol=4)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(aca / "fig3_serie_iono.svg")

print("figuras escritas:", sorted(p.name for p in aca.glob("*.svg")))
