#!/usr/bin/env python3
"""Figuras de la clase 2.4 (leen data/resultados_2_4.json)."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

aca = Path(__file__).resolve().parent
d = json.load(open(aca.parent / "data" / "resultados_2_4.json"))
comp = d["comparacion"]

# fig1: comparación tu-cadena vs gnss-sdr (delay y doppler, dos paneles)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
etiquetas = [c["sistema"] for c in comp]
x = np.arange(len(comp))
w = 0.35

# panel delay
propio_d = [c["propio"]["delay"] for c in comp]
sdr_d = [c["gnss_sdr_publicado"]["delay"] for c in comp]
a1.bar(x - w/2, propio_d, w, label="tu cadena (2.1->2.3)", color="tab:blue")
a1.bar(x + w/2, sdr_d, w, label="gnss-sdr (referencia)", color="tab:orange")
for i, (p, s) in enumerate(zip(propio_d, sdr_d)):
    a1.text(i - w/2, p, str(p), ha="center", va="bottom", fontsize=8)
    a1.text(i + w/2, s, str(s), ha="center", va="bottom", fontsize=8)
a1.set_xticks(x)
a1.set_xticklabels(etiquetas, fontsize=8)
a1.set_ylabel("desfase de código (muestras)")
a1.set_title("Desfase de código: tu cadena vs gnss-sdr")
a1.legend(fontsize=8)
a1.grid(alpha=0.3, axis="y")

# panel doppler
propio_f = [c["propio"]["doppler"] for c in comp]
sdr_f = [c["gnss_sdr_publicado"]["doppler"] for c in comp]
a2.bar(x - w/2, propio_f, w, label="tu cadena", color="tab:blue")
a2.bar(x + w/2, sdr_f, w, label="gnss-sdr", color="tab:orange")
for i, (p, s) in enumerate(zip(propio_f, sdr_f)):
    va = "bottom" if p >= 0 else "top"
    a2.text(i - w/2, p, f"{p:+d}", ha="center", va=va, fontsize=8)
    a2.text(i + w/2, s, f"{s:+d}", ha="center", va=va, fontsize=8)
a2.axhline(0, color="k", lw=0.5)
a2.set_xticks(x)
a2.set_xticklabels(etiquetas, fontsize=8)
a2.set_ylabel("Doppler (Hz)")
a2.set_title("Doppler: tu cadena vs gnss-sdr")
a2.legend(fontsize=8)
a2.grid(alpha=0.3, axis="y")
fig.suptitle("Modulo 2 cerrado: tu receptor concuerda con la referencia",
             fontsize=12)
fig.tight_layout()
fig.savefig(aca / "fig1_comparacion.svg")

# fig2: el delta (error de tu cadena respecto a la referencia)
fig, ax = plt.subplots(figsize=(8, 4))
dd = [c["delta_delay"] for c in comp]
df = [c["delta_doppler"] for c in comp]
ax.bar(x - w/2, dd, w, label="Delta desfase (muestras)", color="tab:green")
ax.bar(x + w/2, df, w, label="Delta Doppler (Hz)", color="tab:purple")
for i, (a, b) in enumerate(zip(dd, df)):
    ax.text(i - w/2, a, str(a), ha="center", va="bottom", fontsize=9)
    ax.text(i + w/2, b, str(b), ha="center", va="bottom", fontsize=9)
ax.set_xticks(x)
ax.set_xticklabels(etiquetas)
ax.set_ylabel("diferencia absoluta")
ax.set_title("Diferencia tu-cadena vs gnss-sdr (mas chico = mejor)")
ax.legend()
ax.grid(alpha=0.3, axis="y")
real = d.get("gnss_sdr_real", {})
if real.get("doppler") is not None:
    ax.annotate(f"gnss-sdr REAL sobre la captura:\nPRN{real.get('prn','?')}, "
                f"Doppler {real['doppler']:+d} Hz, tracking OK",
                xy=(0.5, 0.85), xycoords="axes fraction", ha="center",
                fontsize=9, bbox=dict(boxstyle="round", fc="lightyellow"))
fig.tight_layout()
fig.savefig(aca / "fig2_delta.svg")
print("figuras escritas:", sorted(p.name for p in aca.glob("*.svg")))
