#!/usr/bin/env python3
"""Figura 6.2 — la cadena de confianza OSNMA (autocontenida)."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
aca = Path(__file__).resolve().parent
pasos = ["Raíz Merkle\n(embebida)", "Clave pública\n(prueba inclusión)",
         "Firma ECDSA\ndel KROOT", "KROOT\n(raíz TESLA)",
         "Claves TESLA\n(reveladas)", "Tags\n→ datos nav"]
fig, ax = plt.subplots(figsize=(11, 2.6))
x = 0
for i, p in enumerate(pasos):
    ax.add_patch(FancyBboxPatch((x, 0.2), 1.5, 0.9, boxstyle="round,pad=0.05",
                 fc="#f5d9a8" if i in (0,3) else "#dce8f5", ec="#205080"))
    ax.text(x+0.75, 0.65, p, ha="center", va="center", fontsize=8)
    if i < len(pasos)-1:
        ax.add_patch(FancyArrowPatch((x+1.5, 0.65), (x+1.9, 0.65),
                     arrowstyle="-|>", mutation_scale=13, color="#c44"))
    x += 1.9
ax.text(x/2, 1.35, "La confianza fluye de la raíz embebida hasta cada dato de navegación autenticado",
        ha="center", fontsize=9, style="italic", color="#555")
ax.set_xlim(-0.2, x+0.2); ax.set_ylim(0, 1.6); ax.axis("off")
fig.tight_layout(); fig.savefig(aca/"fig1_cadena.svg")
print("figuras escritas: ['fig1_cadena.svg']")
