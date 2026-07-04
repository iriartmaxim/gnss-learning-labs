#!/usr/bin/env python3
"""Figuras de la clase 2.3 (leen data/resultados_2_3.json)."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

aca = Path(__file__).resolve().parent
d = json.load(open(aca.parent / "data" / "resultados_2_3.json"))
I = np.array(d["prompts_i"])
Q = np.array(d["prompts_q"])
ms = np.arange(I.size)

# fig1: prompt I(t) — se ven los bits como bloques de signo constante
fig, (a1, a2) = plt.subplots(2, 1, figsize=(10, 5), sharex=True)
a1.plot(ms, I, lw=0.6, color="tab:blue", label="I (prompt)")
a1.plot(ms, Q, lw=0.6, color="tab:orange", alpha=0.7, label="Q (prompt)")
a1.axhline(0, color="k", lw=0.5)
a1.set_ylabel("correlador prompt")
a1.set_title("Tracking: la energía cae toda en I (PLL enganchado); "
             "cada 20 ms un bit")
a1.legend(fontsize=8, loc="upper right")
a1.grid(alpha=0.3)
# marcar límites de bit
for b in range(0, I.size, 20):
    a1.axvline(b, color="gray", ls=":", lw=0.4)
# barras de bits acumulados
acc = np.array(d["acc_bits"])
bit_ms = np.arange(acc.size) * 20 + 10
a2.bar(bit_ms, acc, width=16,
       color=["tab:green" if x > 0 else "tab:red" for x in acc])
a2.axhline(0, color="k", lw=0.5)
a2.set_xlabel("tiempo (ms)")
a2.set_ylabel("Σ I por bit")
a2.set_title("Integración de 20 ms → signo → bit (verde=0, rojo=1)")
a2.grid(alpha=0.3, axis="y")
fig.tight_layout()
fig.savefig(aca / "fig1_prompt_bits.svg")

# fig2: convergencia de los lazos (PLL freq y DLL error)
cf = np.array(d["carr_freq"])
dll = np.array(d["dll_err"])
fig, (b1, b2) = plt.subplots(2, 1, figsize=(10, 5), sharex=True)
b1.plot(ms, cf, lw=0.8, color="tab:purple")
b1.axhline(d["doppler_real"], color="tab:green", ls="--", lw=1,
           label=f"Doppler real = {d['doppler_real']:.0f} Hz")
b1.set_ylabel("freq portadora NCO (Hz)")
b1.set_title("PLL: el NCO converge al Doppler real en ~decenas de ms")
b1.legend(fontsize=8)
b1.grid(alpha=0.3)
b2.plot(ms, dll, lw=0.7, color="tab:brown")
b2.axhline(0, color="k", lw=0.5)
b2.set_xlabel("tiempo (ms)")
b2.set_ylabel("discriminador DLL (chips)")
b2.set_title("DLL: parte de ~0.5 chip (error de adquisición) y converge a 0")
b2.set_ylim(-0.6, 0.6)
b2.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(aca / "fig2_lazos.svg")

# fig3: constelación I/Q — antes vs después del enganche
fig, (c1, c2) = plt.subplots(1, 2, figsize=(9, 4.3))
n0 = 15   # primeros ms (transitorio)
c1.scatter(I[:n0], Q[:n0], s=18, alpha=0.7, color="tab:red")
c1.set_title(f"primeros {n0} ms (enganchando)")
c1.set_xlabel("I")
c1.set_ylabel("Q")
c1.axhline(0, color="k", lw=0.4)
c1.axvline(0, color="k", lw=0.4)
c1.grid(alpha=0.3)
c1.set_aspect("equal")
c2.scatter(I[25:], Q[25:], s=18, alpha=0.6, color="tab:green")
c2.set_title("tras enganche: dos nubes sobre el eje I (±)")
c2.set_xlabel("I")
c2.set_ylabel("Q")
c2.axhline(0, color="k", lw=0.4)
c2.axvline(0, color="k", lw=0.4)
c2.grid(alpha=0.3)
c2.set_aspect("equal")
lim = np.max(np.abs(I)) * 1.1
for ax in (c1, c2):
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
fig.suptitle("Constelación del prompt: BPSK a lo largo del eje I",
             fontsize=11)
fig.tight_layout()
fig.savefig(aca / "fig3_constelacion.svg")
print("figuras escritas:", sorted(p.name for p in aca.glob("*.svg")))
