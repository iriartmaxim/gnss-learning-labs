#!/usr/bin/env python3
"""Figuras de visión global (esquemáticas, sin dependencia de datos)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrow, FancyBboxPatch

aca = __file__.rsplit("/", 1)[0]

# fig1: el arco con las clases del path
etapas = [("SEÑAL", "2.1–2.4", "#4878cf"), ("OBSERVABLES", "1.2 · 1.5 · 3.4", "#6acc65"),
          ("MENSAJE\nÓRBITAS", "0.4 · 1.3 · 4.1", "#ee854a"),
          ("CORRECCIONES", "3.1–3.4", "#d65f5f"), ("SOLUCIÓN PVT", "1.1–1.5", "#956cb4")]
fig, ax = plt.subplots(figsize=(10, 3.2))
for i, (nombre, clases, color) in enumerate(etapas):
    x = i * 2.0
    ax.add_patch(FancyBboxPatch((x, 0.35), 1.55, 1.05, boxstyle="round,pad=0.08",
                                fc=color, ec="none", alpha=0.85))
    ax.text(x + 0.78, 1.12, nombre, ha="center", va="center", fontsize=9,
            color="white", weight="bold")
    ax.text(x + 0.78, 0.62, clases, ha="center", va="center", fontsize=8, color="white")
    if i < 4:
        ax.add_patch(FancyArrow(x + 1.68, 0.9, 0.22, 0, width=0.06,
                                head_width=0.2, head_length=0.1, fc="#555555", ec="none"))
ax.text(4.9, 2.05, "VERDAD PRECISA (SP3/CLK) — califica todas las etapas",
        ha="center", fontsize=8.5, style="italic", color="#333333")
ax.annotate("", xy=(4.9, 1.55), xytext=(4.9, 1.95),
            arrowprops=dict(arrowstyle="->", color="#333333", ls="--"))
ax.set_xlim(-0.3, 10.1); ax.set_ylim(0, 2.4); ax.axis("off")
ax.set_title("El arco GNSS: cada clase del path trabaja un tramo", fontsize=11)
fig.tight_layout()
fig.savefig(f"{aca}/fig1_arco.svg")

# fig2: los tres segmentos
fig, ax = plt.subplots(figsize=(7.5, 3.6))
segs = [("ESPACIAL", "emite señal + mensaje\n~30 sats por sistema", 0.83, "#4878cf"),
        ("CONTROL", "mide, ajusta, sube efemérides\nel punto único de falla", 0.5, "#d65f5f"),
        ("USUARIO", "escucha, correla, resuelve\n(pasivo: nunca transmite)", 0.17, "#6acc65")]
for nombre, desc, y, color in segs:
    ax.add_patch(FancyBboxPatch((0.06, y - 0.12), 0.36, 0.24, boxstyle="round,pad=0.02",
                                transform=ax.transAxes, fc=color, alpha=0.85, ec="none"))
    ax.text(0.24, y, nombre, transform=ax.transAxes, ha="center", va="center",
            fontsize=10, color="white", weight="bold")
    ax.text(0.72, y, desc, transform=ax.transAxes, ha="center", va="center", fontsize=9)
ax.annotate("", xy=(0.24, 0.62), xytext=(0.24, 0.72), xycoords="axes fraction",
            arrowprops=dict(arrowstyle="<->", color="#555555"))
ax.annotate("", xy=(0.24, 0.29), xytext=(0.24, 0.39), xycoords="axes fraction",
            arrowprops=dict(arrowstyle="->", color="#555555"))
ax.axis("off")
ax.set_title("Los tres segmentos: el de arriba emite, el de abajo escucha,\ny el del medio es el que se rompe", fontsize=10)
fig.tight_layout()
fig.savefig(f"{aca}/fig2_segmentos.svg")
print("figuras escritas: ['fig1_arco.svg', 'fig2_segmentos.svg']")
