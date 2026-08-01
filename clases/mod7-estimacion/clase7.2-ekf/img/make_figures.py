#!/usr/bin/env python3
"""Figuras 7.2 (leen data/resultados_7_2.json)."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

aca = Path(__file__).resolve().parent
d = json.load(open(aca.parent / "data" / "resultados_7_2.json"))
err = np.array(d["err3d"])
t = np.arange(1, len(err) + 1) * 0.5  # min

fig, ax = plt.subplots(figsize=(9, 3.6))
ax.semilogy(t, err, "-", lw=1.2, color="#205080")
ax.axhline(1.95, ls="--", lw=0.9, color="gray")
ax.annotate("LSQ suelto (1.95 m)", (t[-1] * 0.55, 2.1), fontsize=8, color="gray")
ax.set_xlabel("minutos desde 12:00")
ax.set_ylabel("error 3D [m] (log)")
ax.set_title("EKF con toda la constelación: de 8.6 m (GN inicial) a ~1.2 m\n"
             "— velocidad, deriva (−196 m/s) y saltos de ms incluidos")
ax.grid(alpha=0.3, which="both")
fig.tight_layout()
fig.savefig(aca / "fig1_convergencia.svg")

err_b = np.array(d["err_3sv"]); sig_b = np.array(d["sig_3sv"])
tb = np.arange(1, len(err_b) + 1) * 0.5
fig, ax = plt.subplots(figsize=(9, 3.6))
ax.semilogy(tb, err_b, "-", lw=1.4, color="#b03030", label="error 3D real")
ax.semilogy(tb, sig_b, "--", lw=1.2, color="#205080", label="σ que cree el filtro (√tr P)")
ax.fill_between(tb, sig_b, err_b, color="#b03030", alpha=0.12)
ax.set_xlabel("minutos con solo 3 satélites")
ax.set_ylabel("[m] (log)")
ax.legend(fontsize=8)
ax.set_title("La trampa de los 3 SVs: el error corre a cientos de km\n"
             "y la covarianza jura que son 135 m — overconfidence ×~3000")
ax.grid(alpha=0.3, which="both")
fig.tight_layout()
fig.savefig(aca / "fig2_overconfidence.svg")
print("figuras escritas: ['fig1_convergencia.svg', 'fig2_overconfidence.svg']")
