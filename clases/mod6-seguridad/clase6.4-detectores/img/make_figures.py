#!/usr/bin/env python3
"""Figuras 6.4 (leen data/resultados_6_4.json)."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
aca = Path(__file__).resolve().parent
d = json.load(open(aca.parent/"data"/"resultados_6_4.json"))
t = np.arange(len(d["cn0_atacado"]))
fig, (a1, a2) = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
a1.plot(t, d["cn0_limpio"], color="#55a868", lw=1, label="limpio")
a1.plot(t, d["cn0_atacado"], color="#c44e52", lw=1, label="atacado")
a1.axvspan(300, 600, color="#f2d0d0", alpha=0.4)
a1.axhline(np.mean(d["cn0_limpio"][:100])+5, ls="--", color="#888", label="umbral +5 dB")
a1.set_ylabel("C/N0 medio (dB-Hz)"); a1.legend(fontsize=8); a1.set_title("Detector de salto de C/N0: el spoofer sube la potencia")
a2.plot(t, d["clk_atacado"], color="#c44e52", lw=1)
a2.axvspan(300, 600, color="#f2d0d0", alpha=0.4, label="ventana de ataque")
a2.set_ylabel("reloj receptor (m)"); a2.set_xlabel("tiempo (s)")
a2.legend(fontsize=8); a2.set_title("El spoofer arrastra el reloj del receptor")
fig.tight_layout(); fig.savefig(aca/"fig1_detectores.svg")
print("figuras escritas: ['fig1_detectores.svg']")
