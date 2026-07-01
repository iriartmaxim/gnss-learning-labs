"""Genera las figuras SVG de la clase 1.4 (figuras como código, reproducibles).

Uso: python make_figures.py   (desde img/)

fig1: skyplot del escenario de 10 satélites (usa data/)
fig2: curvas DOP vs. máscara de elevación (usa data/)
fig3: elipses de error horizontal del mejor vs. peor subconjunto de 4 (usa data/)
"""
import json
from itertools import combinations
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

plt.rcParams.update({"font.size": 11, "svg.fonttype": "none"})
AQUI = Path(__file__).resolve().parent


def cargar():
    with open(AQUI.parent / "data" / "escenario_10sats.json") as f:
        return json.load(f)


def matriz_G(x3, sats):
    rho = np.linalg.norm(sats - x3, axis=1)
    u = (sats - x3) / rho[:, None]
    return np.hstack([-u, np.ones((len(sats), 1))])


def rot_enu(lat, lon):
    la, lo = np.radians(lat), np.radians(lon)
    return np.array([
        [-np.sin(lo), np.cos(lo), 0.0],
        [-np.sin(la) * np.cos(lo), -np.sin(la) * np.sin(lo), np.cos(la)],
        [np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)],
    ])


# ------------------------------------------------------------------- fig 1
def fig1_skyplot():
    esc = cargar()
    azel = np.array(esc["sat_azel_deg"])
    fig = plt.figure(figsize=(6.4, 6.4))
    ax = fig.add_subplot(projection="polar")
    ax.set_theta_zero_location("N")   # azimut 0 = Norte
    ax.set_theta_direction(-1)        # horario (convención navegación)
    th = np.radians(azel[:, 0])
    r = 90.0 - azel[:, 1]             # radio = distancia cenital
    ax.scatter(th, r, s=140, c="tab:blue", zorder=5, edgecolors="k")
    for i, (t, rr) in enumerate(zip(th, r)):
        ax.annotate(f"S{i}", (t, rr), textcoords="offset points",
                    xytext=(7, 7), fontsize=9)
    ax.set_rlim(0, 90)
    ax.set_rgrids([0, 30, 60, 90], labels=["90°", "60°", "30°", "0°"],
                  fontsize=8)  # etiquetas en elevación
    ax.set_title("Skyplot — 10 satélites sobre Buenos Aires\n"
                 "(radio = 90° − elevación; centro = cénit)", fontsize=11)
    fig.tight_layout()
    fig.savefig(AQUI / "fig1_skyplot.svg")
    plt.close(fig)


# ------------------------------------------------------------------- fig 2
def fig2_dop_vs_mascara():
    esc = cargar()
    sats = np.array(esc["sat_ecef_m"])
    azel = np.array(esc["sat_azel_deg"])
    r_true = np.array(esc["verdad"]["receptor_ecef_m"])
    lat, lon, _ = esc["verdad"]["receptor_geodetico"]
    R = rot_enu(lat, lon)

    masks, pdops, hdops, vdops, nsats = [], [], [], [], []
    for mask in range(0, 41, 5):
        vis = azel[:, 1] >= mask
        if vis.sum() < 4:
            break
        G = matriz_G(r_true, sats[vis])
        Q = np.linalg.inv(G.T @ G)
        Qe = R @ Q[:3, :3] @ R.T
        masks.append(mask)
        nsats.append(int(vis.sum()))
        pdops.append(np.sqrt(np.trace(Q[:3, :3])))
        hdops.append(np.sqrt(Qe[0, 0] + Qe[1, 1]))
        vdops.append(np.sqrt(Qe[2, 2]))

    fig, ax = plt.subplots(figsize=(7.4, 4.8))
    ax.plot(masks, pdops, "o-", label="PDOP")
    ax.plot(masks, hdops, "s-", label="HDOP")
    ax.plot(masks, vdops, "^-", label="VDOP")
    for m, p, ns in zip(masks, pdops, nsats):
        ax.annotate(f"{ns} sats", (m, p), textcoords="offset points",
                    xytext=(0, 10), fontsize=8, ha="center", color="gray")
    ax.set_xlabel("máscara de elevación (°)")
    ax.set_ylabel("DOP")
    ax.set_title("Subir la máscara descarta satélites bajos… y degrada la geometría")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(AQUI / "fig2_dop_vs_mascara.svg")
    plt.close(fig)


# ------------------------------------------------------------------- fig 3
def fig3_elipses():
    esc = cargar()
    sats = np.array(esc["sat_ecef_m"])
    r_true = np.array(esc["verdad"]["receptor_ecef_m"])
    lat, lon, _ = esc["verdad"]["receptor_geodetico"]
    R = rot_enu(lat, lon)

    resultados = []
    for idx in combinations(range(10), 4):
        G = matriz_G(r_true, sats[list(idx)])
        try:
            Q = np.linalg.inv(G.T @ G)
            resultados.append((np.sqrt(np.trace(Q)), idx))
        except np.linalg.LinAlgError:
            pass
    resultados.sort()
    # el peor absoluto es casi coplanar (GDOP ~1200): su elipse es una aguja
    # de +/-500 m que aplasta la escala. Comparamos contra un subconjunto
    # malo pero acotado, y el extremo se anota como texto.
    acotados = [ri for ri in resultados if ri[0] < 15.0]
    casos = [("mejor 4", resultados[0][1], "tab:green"),
             ("un 4 malo", acotados[-1][1], "tab:red")]

    fig, ax = plt.subplots(figsize=(7.0, 5.6))
    t = np.linspace(0, 2 * np.pi, 200)
    for nombre, idx, color in casos:
        G = matriz_G(r_true, sats[list(idx)])
        Q = np.linalg.inv(G.T @ G)
        Qh = (R @ Q[:3, :3] @ R.T)[:2, :2]     # bloque Este-Norte
        val, vec = np.linalg.eigh(Qh)
        # elipse 1-sigma para sigma_UERE = 1 m
        ell = vec @ np.diag(np.sqrt(val)) @ np.vstack([np.cos(t), np.sin(t)])
        hdop = np.sqrt(np.trace(Qh))
        ax.plot(ell[0], ell[1], color=color, lw=2,
                label=f"{nombre}: HDOP = {hdop:.1f}")
        ax.fill(ell[0], ell[1], color=color, alpha=0.12)
    g_peor = resultados[-1][0]
    ax.annotate(f"(el peor absoluto es casi coplanar:\nGDOP = {g_peor:.0f} — "
                "su elipse no entra en ningún gráfico)",
                xy=(0.97, 0.03), xycoords="axes fraction", ha="right",
                fontsize=8.5, color="gray")
    ax.plot(0, 0, "k+", ms=12, mew=2)
    ax.set_aspect("equal")
    ax.set_xlabel("Este (m)")
    ax.set_ylabel("Norte (m)")
    ax.set_title("Elipse de error horizontal (1σ, σ_UERE = 1 m):\n"
                 "misma constelación, distinto subconjunto de 4")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(AQUI / "fig3_elipses.svg")
    plt.close(fig)


if __name__ == "__main__":
    fig1_skyplot()
    fig2_dop_vs_mascara()
    fig3_elipses()
    print("figuras escritas:", [p.name for p in sorted(AQUI.glob("*.svg"))])
