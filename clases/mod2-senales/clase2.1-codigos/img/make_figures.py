#!/usr/bin/env python3
"""Figuras de la clase 2.1 (leen data/resultados_2_1.json)."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

aca = Path(__file__).resolve().parent
d = json.load(open(aca.parent / "data" / "resultados_2_1.json"))
auto = np.array(d["auto_prn1"])
cruz = np.array(d["cruz_prn1_prn2"])
lags = np.arange(1023)

# fig1: autocorrelación (panorama + zoom al piso)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.5, 3.9))
a1.plot(lags, auto, lw=0.7)
a1.annotate(f"pico = {d['pico']}", (0, d["pico"]), xytext=(120, 900),
            fontsize=10, arrowprops=dict(arrowstyle="->"))
a1.set_xlabel("desfase (chips)")
a1.set_ylabel("autocorrelación")
a1.set_title("PRN1: el pico que hace posible el GPS")
a1.grid(alpha=0.3)
a2.plot(lags, auto, lw=0.7)
a2.set_ylim(-90, 90)
for v in (-65, -1, 63):
    a2.axhline(v, color="tab:red", ls=":", lw=0.9)
    a2.annotate(f"{v}", (1035, v), fontsize=8, color="tab:red",
                va="center", annotation_clip=False)
a2.set_xlabel("desfase (chips)")
a2.set_title("zoom: el piso toma solo tres valores")
a2.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(aca / "fig1_autocorrelacion.svg")

# fig2: correlación cruzada + histograma de los tres valores
fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.5, 3.9),
                             gridspec_kw={"width_ratios": [2.1, 1]})
a1.plot(lags, cruz, lw=0.7, color="tab:orange")
a1.set_ylim(-90, 90)
a1.set_xlabel("desfase (chips)")
a1.set_ylabel("correlación PRN1 × PRN2")
a1.set_title("otro satélite parece ruido: nunca supera |65|")
a1.grid(alpha=0.3)
hist = d["hist_cruzada"]
vals = sorted(int(k) for k in hist)
a2.bar([str(v) for v in vals], [hist[str(v)] for v in vals],
       color="tab:orange")
for i, v in enumerate(vals):
    a2.annotate(str(hist[str(v)]), (i, hist[str(v)]), ha="center",
                va="bottom", fontsize=9)
a2.set_title("familia Gold: tres valores")
a2.set_xlabel("valor")
a2.set_ylabel("cantidad de desfases")
fig.tight_layout()
fig.savefig(aca / "fig2_cruzada.svg")

# fig3: espectro BPSK(1) del C/A vs BOC(1,1) (la base de Galileo E1)
bits = np.array([int(b) for b in d["bits_prn1"]], dtype=np.int64)
c = 1 - 2 * bits                       # chips ±1
SPC = 4                                # muestras por chip -> fs = 4.092 MHz
bpsk = np.repeat(c, SPC)
sub = np.tile([1, 1, -1, -1], c.size)  # subportadora BOC(1,1)
boc = np.repeat(c, SPC) * sub
fs = SPC * 1.023e6

def psd_db(x, reps=24):
    xs = np.tile(x, reps).reshape(reps, x.size).astype(float)
    xs *= np.hanning(x.size)
    P = np.mean(np.abs(np.fft.fft(xs, axis=1)) ** 2, axis=0)
    P = np.fft.fftshift(P)
    return 10 * np.log10(P / P.max() + 1e-12)

f = np.fft.fftshift(np.fft.fftfreq(bpsk.size, 1 / fs)) / 1e6
fig, ax = plt.subplots(figsize=(8.5, 4.2))
ax.plot(f, psd_db(bpsk), lw=0.9, label="BPSK(1) — GPS C/A")
ax.plot(f, psd_db(boc), lw=0.9, alpha=0.85,
        label="BOC(1,1) — base de Galileo E1")
ax.set_xlim(-2.05, 2.05)
ax.set_ylim(-45, 3)
ax.set_xlabel("frecuencia relativa a la portadora (MHz)")
ax.set_ylabel("PSD normalizada (dB)")
ax.set_title("Mismo código, dos modulaciones: la energía cambia de lugar")
ax.annotate("BOC parte la energía:\nnulo en el centro,\nlóbulos a ±1 MHz",
            (0, -38), ha="center", fontsize=9)
ax.grid(alpha=0.3)
ax.legend(fontsize=9, loc="upper right")
fig.tight_layout()
fig.savefig(aca / "fig3_espectro.svg")
print("figuras escritas:", sorted(p.name for p in aca.glob("*.svg")))
