#!/usr/bin/env python3
"""Figuras 6.5 (leen data/resultados_6_5.json)."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
aca = Path(__file__).resolve().parent
d = json.load(open(aca.parent/"data"/"resultados_6_5.json"))
S = np.array(d["espectrograma"])
fig, (a1, a2) = plt.subplots(2, 1, figsize=(8, 6))
a1.imshow(S, aspect="auto", origin="lower", cmap="magma",
          extent=[0, 20, -2, 2])
a1.set_ylabel("frecuencia (MHz)"); a1.set_xlabel("tiempo (ms)")
a1.set_title("Espectrograma: el chirp del jammer barre la banda (8-14 ms)")
blk_t = np.array(d["blk_t"])*1000
a2.plot(blk_t, d["cn0"], color="#c44e52", lw=1.2)
a2.axvspan(d["jam"][0]*1000, d["jam"][1]*1000, color="#f2d0d0", alpha=0.5, label="jammer activo")
a2.axhline(30, ls="--", color="#888", label="umbral tracking (30 dB-Hz)")
a2.set_ylabel("C/N0 (dB-Hz)"); a2.set_xlabel("tiempo (ms)")
a2.set_title(f"C/N0 cae {d['cn0_caida']:.0f} dB-Hz → tracking perdido")
a2.legend(fontsize=8)
fig.tight_layout(); fig.savefig(aca/"fig1_jamming.svg")
print("figuras escritas: ['fig1_jamming.svg']")
