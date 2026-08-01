#!/usr/bin/env python3
"""Figuras de la clase visión global. Regenerar: python3 make_figures.py"""
import matplotlib
from pathlib import Path
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# fig1 (hero): el arco con el módulo del path debajo de cada eslabón
arco = [("señal", "mod2"), ("observable", "1.5 · 3.4 · 2.2"),
        ("error", "mod3"), ("órbita", "1.3 · 4.1"), ("PVT", "1.5 · mod7")]
fig, ax = plt.subplots(figsize=(10, 2.8))
x = 0.06
for i, (titulo, mod) in enumerate(arco):
    box = FancyBboxPatch((x, 0.45), 0.13, 0.32, boxstyle="round,pad=0.01",
                         fc="#dce8f5", ec="#205080", lw=1.5)
    ax.add_patch(box)
    ax.text(x + 0.065, 0.61, titulo, ha="center", va="center", fontsize=11, weight="bold")
    ax.text(x + 0.065, 0.34, mod, ha="center", va="center", fontsize=8, color="#555")
    if i < len(arco) - 1:
        ax.add_patch(FancyArrowPatch((x + 0.13, 0.61), (x + 0.19, 0.61),
                                     arrowstyle="-|>", mutation_scale=16, color="#205080"))
    x += 0.19
ax.text(0.5, 0.9, "El arco del path: cada eslabón es un módulo del repo",
        ha="center", fontsize=12, weight="bold")
ax.text(0.5, 0.12, "señal → observable → error → órbita → PVT",
        ha="center", fontsize=9, style="italic", color="#666")
ax.set_xlim(0, 1.03); ax.set_ylim(0, 1); ax.axis("off")
aca = Path(__file__).resolve().parent
fig.savefig(aca / "fig1_arco.svg", bbox_inches="tight")

# fig2: los tres segmentos
fig, ax = plt.subplots(figsize=(8, 3.2))
seg = [("Segmento\nespacial", "satélites\nrelojes atómicos\ngeneran la señal", 0.17, "#f5e6cc"),
       ("Segmento de\ncontrol", "estaciones en tierra\ncalculan órbita+reloj\nsuben la efeméride", 0.5, "#d8ecd8"),
       ("Segmento\nusuario", "tu receptor\nadquiere→trackea→PVT", 0.83, "#dce8f5")]
for titulo, det, cx, col in seg:
    ax.add_patch(FancyBboxPatch((cx - 0.14, 0.3), 0.28, 0.5, boxstyle="round,pad=0.015",
                                fc=col, ec="#444", lw=1.2))
    ax.text(cx, 0.68, titulo, ha="center", va="center", fontsize=11, weight="bold")
    ax.text(cx, 0.44, det, ha="center", va="center", fontsize=8)
ax.add_patch(FancyArrowPatch((0.31, 0.7), (0.36, 0.7), arrowstyle="-|>", mutation_scale=14, color="#444"))
ax.text(0.335, 0.75, "sube\nefeméride", ha="center", fontsize=6.5)
ax.add_patch(FancyArrowPatch((0.31, 0.45), (0.36, 0.45), arrowstyle="-|>", mutation_scale=14, color="#444"))
ax.add_patch(FancyArrowPatch((0.64, 0.55), (0.69, 0.55), arrowstyle="-|>", mutation_scale=14, color="#444"))
ax.text(0.665, 0.6, "señal", ha="center", fontsize=6.5)
ax.text(0.5, 0.92, "Los tres segmentos de un GNSS", ha="center", fontsize=12, weight="bold")
ax.set_xlim(0, 1); ax.set_ylim(0.2, 1); ax.axis("off")
fig.savefig(aca / "fig2_segmentos.svg", bbox_inches="tight")

print("figuras escritas: ['fig1_arco.svg', 'fig2_segmentos.svg']")
