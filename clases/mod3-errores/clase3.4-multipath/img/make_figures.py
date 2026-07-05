#!/usr/bin/env python3
"""Figuras de la clase 3.4 (leen data/resultados_3_4.json)."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

aca = Path(__file__).resolve().parent
d = json.load(open(aca.parent / "data" / "resultados_3_4.json"))


def arr(x):
    return np.array([np.nan if v is None else v for v in x], dtype=float)


def suave(v, k=5):
    """Media móvil que ignora NaN (solo para visualizar la parte lenta)."""
    out = np.full_like(v, np.nan)
    for i in range(len(v)):
        w = v[max(0, i - k // 2):i + k // 2 + 1]
        if np.isfinite(w).sum() >= 2:
            out[i] = np.nanmean(w)
    return out


# fig1: series MP1 de un satelite alto vs uno bajo
fig, axs = plt.subplots(2, 1, figsize=(11, 6), sharex=True)
for ax, key, col in ((axs[0], "sat_alto", "tab:blue"),
                     (axs[1], "sat_bajo", "tab:red")):
    s = d[key]
    t, mp, el = arr(s["t_min"]), arr(s["mp1_cm"]), arr(s["el"])
    ax.plot(t, mp, lw=0.7, color=col, alpha=0.5)
    ax.plot(t, suave(mp), lw=1.8, color=col,
            label=f"{s['sv']} (elev media {s['el_med']:.0f}°) — suavizado 2.5 min")
    ax.axhline(0, color="gray", lw=0.5)
    ax.set_ylabel("MP1 (cm)")
    ax.set_ylim(-110, 110)
    ax2 = ax.twinx()
    ax2.plot(t, el, lw=1, ls=":", color="gray")
    ax2.set_ylabel("elevación (°)", color="gray")
    ax.legend(loc="upper left", fontsize=8)
    ax.grid(alpha=0.3)
axs[0].set_title("El multipath vive cerca del horizonte:\n"
                 "arriba todo es ruido (±20 cm); abajo aparecen las "
                 "oscilaciones lentas del reflejo (±1 m)")
axs[1].set_xlabel("minutos desde las 12:00 UTC")
fig.tight_layout()
fig.savefig(aca / "fig1_series_elevacion.svg")

# fig2: RMS por bin de elevacion + globales
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.3),
                             gridspec_kw={"width_ratios": [3, 2]})
xx = np.arange(len(d["bins"]))
et = [f"{b['lo']}-{b['hi']}°" for b in d["bins"]]
a1.bar(xx - 0.19, [b["rms1_cm"] for b in d["bins"]], 0.38,
       label="MP1 (E1, chip 293 m)", color="tab:blue")
a1.bar(xx + 0.19, [b["rms5_cm"] for b in d["bins"]], 0.38,
       label="MP5 (E5a, chip 29 m)", color="tab:cyan")
for i, b in enumerate(d["bins"]):
    a1.text(xx[i] - 0.19, b["rms1_cm"], f"{b['rms1_cm']:.0f}", ha="center",
            va="bottom", fontsize=8)
    a1.text(xx[i] + 0.19, b["rms5_cm"], f"{b['rms5_cm']:.0f}", ha="center",
            va="bottom", fontsize=8)
a1.set_xticks(xx)
a1.set_xticklabels(et)
a1.set_xlabel("elevación")
a1.set_ylabel("RMS de MP (cm)")
a1.set_title("La firma en elevación (×3 del cenit al horizonte)\n"
             "y la ventaja del chip corto en elevaciones medias/altas")
a1.legend(fontsize=8)
a1.grid(alpha=0.3, axis="y")

nombres = ["RMS MP1", "RMS MP5", "σ ruido E1\n(dif/√2)", "σ ruido E5a\n(dif/√2)"]
vals = [d["rms1_cm"], d["rms5_cm"], d["sig1_cm"], d["sig5_cm"]]
cols = ["tab:blue", "tab:cyan", "tab:gray", "lightgray"]
a2.bar(range(4), vals, color=cols)
for i, v in enumerate(vals):
    a2.text(i, v, f"{v:.0f}", ha="center", va="bottom", fontsize=9)
a2.set_xticks(range(4))
a2.set_xticklabels(nombres, fontsize=7)
a2.set_ylabel("cm")
a2.set_title("El σ_P ≈ 0.3 m que asumimos desde la 1.5,\n"
             "por fin medido: 25 cm (choke ring mediante)")
a2.grid(alpha=0.3, axis="y")
fig.tight_layout()
fig.savefig(aca / "fig2_elevacion_rms.svg")

# fig3: la repeticion sideral Galileo (10 dias)
s = d["sideral"]
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.3),
                             gridspec_kw={"width_ratios": [3, 2]})
t166 = arr(s["t166_min"]) + 720.0                 # min del día 166
t176 = arr(s["t176_min"]) + 675.0 - s["lag_opt_s"] / 60.0   # alineada
a1.plot(t166, suave(arr(s["mp166_cm"])), lw=1.8, color="tab:blue",
        label=f"{s['sv']} día 166")
a1.plot(t176, suave(arr(s["mp176_cm"])), lw=1.8, color="tab:orange",
        label=f"{s['sv']} día 176, corrido {-s['lag_opt_s']/60:.1f} min")
a1.axhline(0, color="gray", lw=0.5)
a1.set_xlim(715, 815)
a1.set_xlabel("minutos del día (día 166) — series suavizadas 2.5 min")
a1.set_ylabel("MP1 (cm)")
a1.set_title(f"El mismo reflejo, 10 días después:\n"
             f"la geometría Galileo se repite (correlación {s['corr_opt']:.2f})")
a1.legend(fontsize=8)
a1.grid(alpha=0.3)

a2.plot(arr(s["lags_s"]), arr(s["corrs"]), "o-", ms=3, lw=1,
        color="tab:blue")
a2.axvline(s["lag_teorico_s"], color="tab:green", ls="--", lw=1.2,
           label=f"teórico {s['lag_teorico_s']:.0f} s\n(10 d sidéreos − 10 d solares)")
a2.plot([s["lag_opt_s"]], [s["corr_opt"]], "o", ms=8, color="tab:red",
        label=f"pico: {s['lag_opt_s']} s, r={s['corr_opt']:.2f}")
a2.plot([0], [s["corr_lag0"]], "s", ms=7, color="gray",
        label=f"sin corrimiento: r={s['corr_lag0']:.2f}")
a2.set_xlabel("corrimiento aplicado al día 176 (s)")
a2.set_ylabel("correlación")
a2.set_title("La correlación delata el ciclo de\nrepetición: 17 órbitas = 10 días")
a2.legend(fontsize=7, loc="upper right")
a2.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(aca / "fig3_sideral.svg")
print("figuras escritas:", sorted(p.name for p in aca.glob("*.svg")))
