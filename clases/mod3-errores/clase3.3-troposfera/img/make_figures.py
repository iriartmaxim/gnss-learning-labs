#!/usr/bin/env python3
"""Figuras de la clase 3.3 (leen data/resultados_3_3.json)."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

aca = Path(__file__).resolve().parent
d = json.load(open(aca.parent / "data" / "resultados_3_3.json"))
zt = d["zhd_m"] + d["zwd_m"]

# fig1: retardo oblicuo vs elevacion + tropo vs iono en amplificacion
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.3))
ee = np.linspace(5, 90, 300)
m = 1.0 / np.sin(np.radians(ee))
a1.plot(ee, zt * m, lw=1.8, color="tab:blue",
        label=f"Saastamoinen (cenital {zt:.2f} m)")
a1.plot(ee, d["minimo_15_m"] * m, lw=1.4, ls="--", color="tab:gray",
        label=f"mínimo 1.5 (cenital {d['minimo_15_m']:.2f} m)")
for fila in d["tabla_mapeo"]:
    a1.plot(fila["elev"], fila["saas_m"], "o", color="tab:red", ms=4)
    a1.annotate(f"{fila['saas_m']:.1f}", (fila["elev"], fila["saas_m"]),
                textcoords="offset points", xytext=(6, 4), fontsize=8)
a1.set_xlabel("elevación (grados)")
a1.set_ylabel("retardo troposférico oblicuo (m)")
a1.set_title("El retardo tropo con mapeo 1/sin(el):\n2.4 m cenitales, 27 m a 5°")
a1.legend(fontsize=8)
a1.grid(alpha=0.3)

F_iono = 1.0 + 16.0 * (0.53 - ee / 180.0) ** 3
a2.plot(ee, m, lw=1.8, color="tab:blue", label="tropo: 1/sin(el)")
a2.plot(ee, F_iono, lw=1.8, color="tab:orange", label="iono: F Klobuchar (3.1)")
a2.annotate("×11.5", (5, m[0]), textcoords="offset points",
            xytext=(8, 0), fontsize=9, color="tab:blue")
a2.annotate("×3.0", (5, F_iono[0]), textcoords="offset points",
            xytext=(8, 4), fontsize=9, color="tab:orange")
a2.set_xlabel("elevación (grados)")
a2.set_ylabel("factor de amplificación")
a2.set_title("Tropo vs iono a baja elevación:\nla capa pegada al suelo amplifica mucho más")
a2.legend(fontsize=8)
a2.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(aca / "fig1_mapeo_oblicuo.svg")

# fig2: PVT con tres troposferas
sab = [("sin", "sin\ntroposfera", "tab:red"),
       ("min", "mínimo 1.5\n(2.3·exp/sin)", "tab:gray"),
       ("saas", "Saastamoinen\nZHD+ZWD", "tab:blue")]
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
a1.set_title("PVT iono-free con tres troposferas (60 fixes):\n"
             "sin modelo, la vertical explota ×4.7")
a1.legend(fontsize=8)
a1.grid(alpha=0.3, axis="y")

rr = d["res_rms"]
a2.bar(range(3), [rr[k] for k, _, _ in sab], color=[c for _, _, c in sab])
a2.set_xticks(range(3))
a2.set_xticklabels([lab for _, lab, _ in sab], fontsize=8)
a2.set_ylabel("RMS de los residuos post-fit (m)")
a2.set_title("Los residuos delatan el modelo que falta\n"
             "(mínimo y Saastamoinen: empate al nivel del ruido)")
for j, (k, _, _) in enumerate(sab):
    a2.text(j, rr[k], f"{rr[k]:.2f}", ha="center", va="bottom", fontsize=8)
a2.grid(alpha=0.3, axis="y")
fig.tight_layout()
fig.savefig(aca / "fig2_tres_tropos.svg")

# fig3: descomposicion ZHD/ZWD + sensibilidad
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.3),
                             gridspec_kw={"width_ratios": [1, 2]})
a1.bar([0], [d["zhd_m"]], 0.5, label=f"ZHD (seco) {d['zhd_m']:.2f} m",
       color="tab:blue")
a1.bar([0], [d["zwd_m"]], 0.5, bottom=[d["zhd_m"]],
       label=f"ZWD (húmedo) {d['zwd_m']:.2f} m", color="tab:cyan")
a1.set_xticks([0])
a1.set_xticklabels(["cenital LPGS\n(invierno)"])
a1.set_ylabel("retardo (m)")
a1.set_title(f"96% hidrostático (exacto con P)\n4% húmedo (el difícil)")
a1.legend(fontsize=8, loc="lower center")
a1.grid(alpha=0.3, axis="y")

PP = np.linspace(960, 1040, 100)
den = 1 - 0.00266 * np.cos(2 * np.radians(-34.9)) - 0.00028e-3 * d["h_m"]
a2.plot(PP, 0.0022768 * PP / den, lw=1.8, color="tab:blue")
a2.axvline(d["P_hPa"], color="gray", ls="--", lw=1)
a2.annotate(f"hoy: {d['P_hPa']:.0f} hPa\nZHD {d['zhd_m']:.3f} m",
            (d["P_hPa"], d["zhd_m"]), textcoords="offset points",
            xytext=(10, -25), fontsize=8)
a2.set_xlabel("presión en superficie (hPa)")
a2.set_ylabel("ZHD (m)")
a2.set_title("La sensibilidad del seco: 2.28 mm/hPa —\n"
             "de tormenta (960) a anticiclón (1040): ±9 cm")
a2.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(aca / "fig3_zhd_zwd.svg")
print("figuras escritas:", sorted(p.name for p in aca.glob("*.svg")))
