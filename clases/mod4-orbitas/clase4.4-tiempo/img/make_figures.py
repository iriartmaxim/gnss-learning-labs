#!/usr/bin/env python3
"""Figuras 4.4 — la escalera de escalas de tiempo (autocontenida)."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
aca = Path(__file__).resolve().parent
# offsets respecto de TAI (2026, ΔAT=37)
escalas = {"TAI": 0, "GPST": -19, "GST": -19, "UTC": -37}
fig, ax = plt.subplots(figsize=(8, 4))
y = list(range(len(escalas)))
for i, (n, off) in enumerate(escalas.items()):
    ax.barh(i, off, color="#4878cf" if n != "UTC" else "#c44e52")
    ax.text(off - 1 if off < 0 else 0.3, i, f"{n}: TAI{off:+d} s", va="center",
            ha="right" if off < 0 else "left", fontsize=9)
ax.axvline(0, color="#333", lw=1)
ax.set_yticks(y); ax.set_yticklabels(list(escalas.keys()))
ax.set_xlabel("offset respecto de TAI (s)")
ax.set_title("Las escalas de tiempo GNSS (2026, ΔAT=37):\nGPST=TAI−19 fija · UTC=TAI−37 salta con leaps · GPST−UTC=18 s")
ax.set_xlim(-42, 8); ax.invert_xaxis(); fig.tight_layout()
fig.savefig(aca/"fig1_escalas.svg")

# fig2: leaps en el tiempo
import matplotlib.dates as mdates
from datetime import datetime
fechas = [datetime(1999,1,1),datetime(2006,1,1),datetime(2009,1,1),
          datetime(2012,7,1),datetime(2015,7,1),datetime(2017,1,1),datetime(2026,6,15)]
dat = [32,33,34,35,36,37,37]
fig, ax = plt.subplots(figsize=(8, 3.5))
ax.step(fechas, dat, where="post", color="#55a868", lw=1.5)
ax.set_ylabel("ΔAT = TAI − UTC (s)"); ax.set_title("Segundos intercalares: sin leaps nuevos desde 2017")
ax.grid(alpha=0.3); fig.tight_layout(); fig.savefig(aca/"fig2_leaps.svg")
print("figuras escritas: ['fig1_escalas.svg', 'fig2_leaps.svg']")
