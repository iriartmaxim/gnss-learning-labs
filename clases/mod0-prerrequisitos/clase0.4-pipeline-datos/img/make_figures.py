#!/usr/bin/env python3
"""Figuras de la clase 0.4 — regenerables con: python3 make_figures.py

Los números son los del día de referencia 2026-06-15 (DOY 166),
documentados en el README §6 y verificados por el lab.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# --- fig1: efemérides por constelación en el BRDC mixto (2026-06-15) ---
con = {"GPS": 450, "BeiDou": 901, "Galileo": 11119}
fig, ax = plt.subplots(figsize=(6.4, 3.6))
barras = ax.bar(con.keys(), con.values(), color=["#4878cf", "#d65f5f", "#6acc65"])
ax.set_yscale("log")
ax.set_ylabel("efemérides en el archivo (log)")
ax.set_title("BRDC mixto 2026-06-15: no todas las constelaciones\n"
             "re-emiten igual (GPS c/2 h; Galileo ~10 min × varios canales)")
for b, v in zip(barras, con.values()):
    ax.annotate(f"{v:,}".replace(",", " "), (b.get_x() + b.get_width() / 2, v),
                ha="center", va="bottom", fontsize=9)
ax.grid(axis="y", alpha=0.3, which="both")
fig.tight_layout()
fig.savefig("fig1_censo_brdc.svg")

# --- fig2: productos de órbita — latencia vs precisión ---
# valores nominales IGS (igs.org/products): broadcast ~1 m, rapid ~2.5 cm,
# final ~2.5 cm; MGEX final es el único multi-GNSS de los tres.
prod = [  # (nombre, latencia [h], precisión órbita [m], nota)
    ("broadcast (BRDC)", 0.02, 1.0, "instantáneo, multi-GNSS"),
    ("IGS rapid", 24, 0.025, "~1 día, SOLO GPS"),
    ("MGEX final (CODE)", 24 * 14, 0.025, "~2 semanas, multi-GNSS"),
]
fig, ax = plt.subplots(figsize=(6.4, 3.6))
for nombre, lat, prec, nota in prod:
    ax.scatter(lat, prec, s=90, zorder=3)
    ax.annotate(f"{nombre}\n({nota})", (lat, prec), textcoords="offset points",
                xytext=(8, 8), fontsize=8)
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlabel("latencia [horas] (log)")
ax.set_ylabel("error de órbita [m] (log)")
ax.set_title("El trade-off del pipeline: cuanto mejor la órbita,\nmás hay que esperarla")
ax.grid(alpha=0.3, which="both")
ax.set_xlim(0.01, 1200); ax.set_ylim(0.01, 3)
fig.tight_layout()
fig.savefig("fig2_latencia_precision.svg")

print("figuras escritas: ['fig1_censo_brdc.svg', 'fig2_latencia_precision.svg']")
