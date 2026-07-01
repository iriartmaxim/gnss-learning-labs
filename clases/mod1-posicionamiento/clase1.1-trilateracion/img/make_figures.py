"""Genera las figuras SVG de la clase 1.1 (figuras como código, reproducibles).

Uso: python make_figures.py   (desde img/)

fig1: intersección de circunferencias en 2D (geometría del ejercicio E1)
fig2: la ambigüedad de 2 mediciones en 2D / 3 en 3D (solución espejo)
fig3: Monte Carlo — misma medición, geometría buena vs. mala (usa data/)
"""
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

plt.rcParams.update({"font.size": 11, "svg.fonttype": "none"})
AQUI = Path(__file__).resolve().parent


# ------------------------------------------------------------------- fig 1
def fig1_interseccion_2d():
    """Geometría del ejercicio E1: balizas (0,0), (6,0), (3,9), rangos 5,5,5."""
    balizas = np.array([[0.0, 0.0], [6.0, 0.0], [3.0, 9.0]])
    r = 5.0
    fig, ax = plt.subplots(figsize=(6.4, 6.4))
    th = np.linspace(0, 2 * np.pi, 400)
    for i, b in enumerate(balizas):
        ax.plot(b[0] + r * np.cos(th), b[1] + r * np.sin(th),
                color="tab:blue", lw=1.6)
        ax.plot(*b, "k^", ms=10)
        ax.annotate(f"$B_{i+1}$", b, textcoords="offset points", xytext=(8, 8))
    ax.plot(3, 4, "*", color="tab:green", ms=17, zorder=5, label="solución (3, 4)")
    ax.plot(3, -4, "x", color="tab:red", ms=12, mew=2.5, zorder=5,
            label="candidata (3, −4): la descarta $B_3$")
    ax.annotate("con $B_1$ y $B_2$ solas hay DOS\npuntos posibles; $B_3$ desambigua",
                xy=(3, -4), xytext=(5.6, -7.6), fontsize=9,
                arrowprops=dict(arrowstyle="->", lw=1.1))
    ax.set_aspect("equal")
    ax.set_xlim(-6, 12)
    ax.set_ylim(-10, 15)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title("Trilateración 2D: intersección de circunferencias (ejercicio E1)")
    ax.legend(loc="upper left", fontsize=9)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(AQUI / "fig1_interseccion_2d.svg")
    plt.close(fig)


# ------------------------------------------------------------------- fig 2
def fig2_ambiguedad():
    """Dos balizas en 2D -> dos soluciones espejo respecto de la recta que
    las une (en 3D: espejo respecto del PLANO de 3 balizas)."""
    b1, b2 = np.array([-4.0, 8.0]), np.array([4.0, 8.0])
    r = np.sqrt(80.0)  # pasa por (0,0) y (0,16)
    fig, ax = plt.subplots(figsize=(6.6, 6.2))
    th = np.linspace(0, 2 * np.pi, 400)
    for b, lbl in [(b1, "$B_1$"), (b2, "$B_2$")]:
        ax.plot(b[0] + r * np.cos(th), b[1] + r * np.sin(th),
                color="tab:blue", lw=1.6)
        ax.plot(*b, "k^", ms=10)
        ax.annotate(lbl, b, textcoords="offset points", xytext=(8, 6))
    ax.axhline(8, color="gray", lw=1.0, ls="--")
    ax.annotate("recta de las balizas\n(en 3D: plano de las 3 balizas)",
                (-9.7, 8.4), fontsize=8.5, color="gray", ha="left")
    ax.plot(0, 0, "*", color="tab:green", ms=17, zorder=5,
            label="receptor verdadero")
    ax.plot(0, 16, "o", mfc="none", mec="tab:red", ms=13, mew=2.2, zorder=5,
            label="solución espejo (¡mismos rangos!)")
    ax.annotate("", xy=(0, 15.2), xytext=(0, 0.8),
                arrowprops=dict(arrowstyle="<->", lw=1.1, color="tab:red"))
    ax.set_aspect("equal")
    ax.set_xlim(-10, 10)
    ax.set_ylim(-3.5, 19)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title("Ambigüedad: mediciones mínimas dejan una solución espejo")
    ax.legend(loc="lower left", fontsize=9)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(AQUI / "fig2_ambiguedad.svg")
    plt.close(fig)


# ------------------------------------------------------------------- fig 3
def fig3_montecarlo():
    """Nube de soluciones con el mismo ruido (sigma=1 m) para las dos
    geometrías del escenario. Proyección horizontal ENU."""
    with open(AQUI.parent / "data" / "escenario_trilat.json") as f:
        esc = json.load(f)
    r_true = np.array(esc["verdad"]["receptor_ecef_m"])
    lat, lon, _ = esc["verdad"]["receptor_geodetico"]
    la, lo = np.radians(lat), np.radians(lon)
    e = np.array([-np.sin(lo), np.cos(lo), 0.0])
    n = np.array([-np.sin(la) * np.cos(lo), -np.sin(la) * np.sin(lo), np.cos(la)])

    def resolver(balizas, r_med, x0):
        x = x0.copy()
        for _ in range(30):
            rho = np.linalg.norm(balizas - x, axis=1)
            u = (balizas - x) / rho[:, None]
            d, *_ = np.linalg.lstsq(-u, r_med - rho, rcond=None)
            x = x + d
            if np.linalg.norm(d) < 1e-4:
                break
        return x

    rng = np.random.default_rng(7)
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 4.8), sharex=True, sharey=True)
    for ax, clave, titulo in [(axes[0], "buenas", "geometría buena (repartida)"),
                              (axes[1], "malas", "geometría mala (cono de ~30°)")]:
        balizas = np.array(esc[f"balizas_{clave}_ecef_m"])
        r_ex = np.array(esc[f"rangos_{clave}_m"])
        pts = []
        for _ in range(400):
            xs = resolver(balizas, r_ex + rng.normal(0, 1.0, 4), r_true + 100.0)
            d = xs - r_true
            pts.append([np.dot(d, e), np.dot(d, n)])
        pts = np.array(pts)
        rms = np.sqrt(np.mean(np.sum(pts**2, axis=1)))
        ax.scatter(pts[:, 0], pts[:, 1], s=6, alpha=0.4)
        ax.plot(0, 0, "r*", ms=13)
        ax.set_title(f"{titulo}\nRMS horizontal = {rms:.1f} m", fontsize=10)
        ax.set_xlabel("Este (m)")
        ax.grid(alpha=0.3)
        ax.set_aspect("equal")
    axes[0].set_ylabel("Norte (m)")
    fig.suptitle("Mismo ruido (σ = 1 m), distinta geometría — antesala del DOP",
                 fontsize=11)
    fig.tight_layout()
    fig.savefig(AQUI / "fig3_montecarlo.svg")
    plt.close(fig)


if __name__ == "__main__":
    fig1_interseccion_2d()
    fig2_ambiguedad()
    fig3_montecarlo()
    print("figuras escritas:", [p.name for p in sorted(AQUI.glob("*.svg"))])
