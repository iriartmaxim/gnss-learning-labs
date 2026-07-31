#!/usr/bin/env python3
"""Figuras de la clase 2.2 (leen data/resultados_2_2.json)."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

aca = Path(__file__).resolve().parent
d = json.load(open(aca.parent / "data" / "resultados_2_2.json"))

# fig1: la función de ambigüedad (CAF) del GPS como mapa de calor
grid = np.array(d["grid_gps"])
meta = d["grid_meta"]
dmax, dstep, dec = meta["dmax"], meta["dstep"], meta["dec"]
dops = np.arange(-dmax, dmax + 1, dstep)
n_code = grid.shape[1] * dec
fig, ax = plt.subplots(figsize=(9, 4.3))
ext = [0, n_code * 1e3 / 4000, dops[0], dops[-1]]
im = ax.imshow(grid, aspect="auto", origin="lower", extent=ext,
               cmap="viridis")
gps = d["gps"]
ax.plot(gps["delay"] * 1e3 / 4000, gps["doppler"], "rx", ms=12, mew=2)
ax.annotate(f"PRN1\n{gps['delay']} muestras\n{gps['doppler']:+d} Hz",
            (gps["delay"] * 1e3 / 4000, gps["doppler"]),
            xytext=(0.55, 0.75), textcoords="axes fraction", color="white",
            fontsize=9, arrowprops=dict(arrowstyle="->", color="white"))
ax.set_xlabel("desfase de código (chips)")
ax.set_ylabel("Doppler (Hz)")
ax.set_title("Función de ambigüedad: el pico dice DÓNDE y a qué VELOCIDAD")
fig.colorbar(im, ax=ax, label="|correlación|²")
fig.tight_layout()
fig.savefig(aca / "fig1_caf_gps.svg")

# fig2: corte en el Doppler del pico — el triángulo de correlación
fila = grid[np.argmin(np.abs(dops - gps["doppler"]))]
chips = np.arange(fila.size) * dec
fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.5, 3.9))
a1.plot(chips, fila, lw=0.8)
a1.axvline(gps["delay"], color="tab:red", ls=":", lw=1)
a1.set_xlabel("desfase de código (chips)")
a1.set_ylabel("|correlación|²")
a1.set_title(f"corte en {gps['doppler']:+d} Hz: un pico, el resto ruido")
a1.grid(alpha=0.3)
# zoom alrededor del pico
lo = max(0, gps["delay"] - 40)
hi = min(fila.size * dec, gps["delay"] + 40)
sel = (chips >= lo) & (chips <= hi)
a2.plot(chips[sel], fila[sel], "o-", ms=3, lw=0.8)
a2.axvline(gps["delay"], color="tab:red", ls=":", lw=1)
a2.set_xlabel("desfase de código (chips)")
a2.set_title("zoom: base de ±1 chip (por eso ~300 m sin afinar)")
a2.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(aca / "fig2_corte_gps.svg")

# fig3: sky-search CTTC — quién está en el cielo
sky = d["sky_cttc"]
prns = sorted(sky, key=int)
met = [sky[p]["metrica"] for p in prns]
piso = np.median(met)
umbral = 2.5 * piso
fig, ax = plt.subplots(figsize=(10, 4))
colores = ["tab:green" if m >= umbral else "0.7" for m in met]
ax.bar([int(p) for p in prns], met, color=colores)
ax.axhline(umbral, color="tab:red", ls="--", lw=1,
           label=f"umbral (2.5× piso ≈ {umbral:.0f})")
vis = [int(p) for p in prns if sky[p]["metrica"] >= umbral]
ax.set_xlabel("PRN")
ax.set_ylabel("métrica de adquisición (pico / media)")
ax.set_title(f"Sky-search: satélites presentes = {sorted(vis)}")
ax.set_xticks(range(1, 33))
ax.tick_params(axis="x", labelsize=7)
ax.legend()
ax.grid(alpha=0.3, axis="y")
fig.tight_layout()
fig.savefig(aca / "fig3_skysearch.svg")
print("figuras escritas:", sorted(p.name for p in aca.glob("*.svg")))

# fig4 (hero): la aguja aparece solo en el bin correcto — todo desde el JSON
i_pico, j_pico = np.unravel_index(grid.argmax(), grid.shape)
chips = np.linspace(0, 1023, grid.shape[1])
fig = plt.figure(figsize=(10, 4.4))
gs = fig.add_gridspec(2, 2, width_ratios=[1.35, 1], hspace=0.45, wspace=0.28)
a1 = fig.add_subplot(gs[0, 0])
a1.plot(chips, grid[0], lw=0.6, color="#888888")
a1.set_title(f"f_D equivocado ({dops[0]:+d} Hz): solo ruido", fontsize=9)
a1.set_xticks([])
a2 = fig.add_subplot(gs[1, 0])
a2.plot(chips, grid[i_pico], lw=0.6, color="#205080")
a2.annotate("la aguja", (chips[j_pico], grid[i_pico, j_pico]),
            xytext=(chips[j_pico] + 180, grid[i_pico, j_pico] * 0.82),
            fontsize=9, color="#b03030",
            arrowprops=dict(arrowstyle="->", color="#b03030"))
a2.set_title(f"f_D correcto ({dops[i_pico]:+d} Hz): pico en "
             f"{gps['delay']} muestras (~134 chips)", fontsize=9)
a2.set_xlabel("desfase de código (chips)")
a3 = fig.add_subplot(gs[:, 1])
a3.imshow(grid, aspect="auto", origin="lower", extent=ext, cmap="viridis",
          vmax=np.percentile(grid, 99.5))
a3.plot(gps["delay"] * 1e3 / 4000, gps["doppler"], "rx", ms=10, mew=2)
a3.set_title("el plano completo τ × f_D", fontsize=9)
a3.set_xlabel("chips"); a3.set_ylabel("Doppler (Hz)")
fig.suptitle("Adquisición = encontrar la aguja en el pajar (captura real, PRN1)",
             fontsize=11)
fig.savefig(aca / "fig4_hero_adquisicion.svg", bbox_inches="tight")
print("fig4_hero_adquisicion.svg")
