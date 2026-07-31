#!/usr/bin/env python3
"""Animación de la búsqueda de adquisición (lee data/resultados_2_2.json).

Regenerar:  python3 make_anim.py   ->  anim_busqueda_gps.gif
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import numpy as np

aca = Path(__file__).resolve().parent
d = json.load(open(aca.parent / "data" / "resultados_2_2.json"))
_g = np.array(d["grid_gps"])
grid = np.maximum(_g[:, ::2], _g[:, 1::2])       # 81 x 500, sin perder el pico
meta, gps = d["grid_meta"], d["gps"]
dops = np.arange(-meta["dmax"], meta["dmax"] + 1, meta["dstep"])
chips = np.linspace(0, 1023, grid.shape[1])
i_pico = int(np.argmax(grid.max(axis=1)))
vmax = grid.max() * 1.05

fig, (a1, a2) = plt.subplots(
    1, 2, figsize=(7.2, 3.0), dpi=80, width_ratios=[1.6, 1])
linea, = a1.plot([], [], lw=0.8, color="#205080")
a1.set_xlim(0, 1023); a1.set_ylim(0, vmax)
a1.set_xlabel("desfase de código (chips)", fontsize=8)
a1.set_ylabel("|correlación|²", fontsize=8)
tit = a1.set_title("", fontsize=9)
mejores = np.full(len(dops), np.nan)
linea2, = a2.plot([], [], ".-", ms=3, lw=0.7, color="#777777")
a2.set_xlim(dops[0], dops[-1]); a2.set_ylim(0, vmax)
a2.set_xlabel("Doppler (Hz)", fontsize=8)
a2.set_title("máximo por bin", fontsize=9)
for a in (a1, a2):
    a.tick_params(labelsize=7)
fig.tight_layout()

CONG = 10                                        # frames congelados al final

def frame(k):
    i = min(k, len(dops) - 1)
    linea.set_data(chips, grid[i])
    es_pico = i == i_pico
    linea.set_color("#b03030" if es_pico else "#205080")
    tit.set_text(f"probando f_D = {dops[i]:+d} Hz"
                 + ("  <- ACA" if es_pico else ""))
    mejores[i] = grid[i].max()
    linea2.set_data(dops, mejores)
    if k >= len(dops):                           # cierre: mostrar respuesta
        tit.set_text(f"detectado: {gps['delay']} muestras, "
                     f"{gps['doppler']:+d} Hz")
        linea.set_data(chips, grid[i_pico])
        linea.set_color("#b03030")
    return linea, linea2, tit

anim = FuncAnimation(fig, frame, frames=len(dops) + CONG, blit=False)
anim.save(aca / "anim_busqueda_gps.gif", writer=PillowWriter(fps=12))
print("anim_busqueda_gps.gif")
