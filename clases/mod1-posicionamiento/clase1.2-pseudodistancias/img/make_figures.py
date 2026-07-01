"""Genera las figuras SVG de la clase 1.2 (figuras como código, reproducibles).

Uso: python make_figures.py   (desde img/; escribe los .svg en este dir)

fig1: por qué el sesgo de reloj rompe la trilateración (2D, misma geometría
      que el ejercicio E1)
fig2: convergencia de Gauss-Newton desde el centro de la Tierra (escenario
      real de data/escenario_5sats.json)
fig3: anatomía de la pseudodistancia (esquema, no a escala)
"""
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

plt.rcParams.update({"font.size": 11, "svg.fonttype": "none"})
AQUI = Path(__file__).resolve().parent


# ------------------------------------------------------------------- fig 1
def fig1_sesgo_2d():
    sats = np.array([[3.0, 4.0], [-4.0, 3.0], [0.0, -5.0]])
    r_true, b = 5.0, 1.0  # rangos verdaderos y sesgo c*dt (unidades arbitrarias)

    fig, ax = plt.subplots(figsize=(6.4, 6.4))
    th = np.linspace(0, 2 * np.pi, 400)
    for i, s in enumerate(sats):
        ax.plot(s[0] + r_true * np.cos(th), s[1] + r_true * np.sin(th),
                color="tab:blue", lw=1.6,
                label="rango verdadero $\\rho_i$" if i == 0 else None)
        ax.plot(s[0] + (r_true + b) * np.cos(th), s[1] + (r_true + b) * np.sin(th),
                "--", color="tab:red", lw=1.4,
                label="pseudodistancia $P_i = \\rho_i + c\\,\\delta t_r$" if i == 0 else None)
        ax.plot(*s, "k^", ms=10)
        ax.annotate(f"$S_{i+1}$", s, textcoords="offset points", xytext=(8, 8))

    ax.plot(0, 0, "*", color="tab:green", ms=16, zorder=5,
            label="receptor (posición verdadera)")
    ax.annotate("las circunferencias medidas NO se\ncortan en un punto: todas están\n"
                "infladas por el mismo $c\\,\\delta t_r$\n(la 4ª incógnita)",
                xy=(-0.35, 0.75), xytext=(-10.6, 6.9), fontsize=9,
                arrowprops=dict(arrowstyle="->", lw=1.2))
    ax.set_aspect("equal")
    ax.set_xlim(-11, 11)
    ax.set_ylim(-11.5, 11)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title("El sesgo de reloj del receptor rompe la trilateración pura")
    ax.legend(loc="lower left", fontsize=9)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(AQUI / "fig1_sesgo_2d.svg")
    plt.close(fig)


# ------------------------------------------------------------------- fig 2
def fig2_convergencia():
    with open(AQUI.parent / "data" / "escenario_5sats.json") as f:
        esc = json.load(f)
    sats = np.array(esc["sat_ecef_m"])
    pr = np.array(esc["pseudodistancias_m"])
    r_true = np.array(esc["verdad"]["receptor_ecef_m"])
    cdt_true = esc["verdad"]["c_dt_receptor_m"]

    x = np.zeros(4)  # centro de la Tierra, reloj perfecto
    err_pos, err_cdt = [np.linalg.norm(x[:3] - r_true)], [abs(x[3] - cdt_true)]
    for _ in range(8):
        rho = np.linalg.norm(sats - x[:3], axis=1)
        u = (sats - x[:3]) / rho[:, None]
        G = np.hstack([-u, np.ones((len(sats), 1))])
        delta, *_ = np.linalg.lstsq(G, pr - (rho + x[3]), rcond=None)
        x = x + delta
        err_pos.append(np.linalg.norm(x[:3] - r_true))
        err_cdt.append(abs(x[3] - cdt_true))
        if np.linalg.norm(delta) < 1e-6:
            break

    it = np.arange(len(err_pos))
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    ax.semilogy(it, np.maximum(err_pos, 1e-10), "o-", label="error de posición")
    ax.semilogy(it, np.maximum(err_cdt, 1e-10), "s--", label="error de $c\\,\\delta t_r$")
    ax.axhline(1.0, color="gray", lw=0.8, ls=":")
    ax.annotate("1 m", (it[-1], 1.3), color="gray", fontsize=9, ha="right")
    ax.set_xlabel("iteración de Gauss-Newton")
    ax.set_ylabel("error (m, escala log)")
    ax.set_title("Convergencia de Gauss-Newton desde el centro de la Tierra\n"
                 "(6371 km de error inicial → sub-mm en 5 iteraciones)", fontsize=11)
    ax.legend()
    ax.grid(alpha=0.3, which="both")
    fig.tight_layout()
    fig.savefig(AQUI / "fig2_convergencia.svg")
    plt.close(fig)


# ------------------------------------------------------------------- fig 3
def fig3_anatomia():
    fig, ax = plt.subplots(figsize=(9.0, 4.0))
    # segmentos (anchos no a escala, elegidos para legibilidad)
    partes = [
        ("$\\rho$  distancia geométrica\n20 000–26 000 km", 6.0, "tab:blue"),
        ("$+\\,c\\,\\delta t_r$  reloj receptor\nhasta ~10² km", 2.0, "tab:red"),
        ("$-\\,c\\,\\delta t^s$  reloj satélite\n(corregido: ~dm–m)", 1.5, "tab:orange"),
        ("$+I$  iono\n~1–30 m", 1.3, "tab:purple"),
        ("$+T$  tropo\n~2–25 m", 1.3, "tab:green"),
        ("$+\\varepsilon$  multipath+ruido\n~dm–m", 1.1, "gray"),
    ]
    x0 = 0.0
    for k, (etiqueta, ancho, color) in enumerate(partes):
        ax.barh(0, ancho, left=x0, height=0.5, color=color, alpha=0.75,
                edgecolor="black", lw=0.6)
        xc = x0 + ancho / 2
        y_lbl = 0.55 if k % 2 == 0 else 1.15  # alternar alturas
        ax.plot([xc, xc], [0.27, y_lbl - 0.05], color="0.4", lw=0.7)
        ax.text(xc, y_lbl, etiqueta, ha="center", va="bottom", fontsize=8.5)
        x0 += ancho
    ax.annotate("", xy=(x0, -0.55), xytext=(0, -0.55),
                arrowprops=dict(arrowstyle="<->", lw=1.2))
    ax.text(x0 / 2, -0.85,
            "$P = \\rho + c(\\delta t_r - \\delta t^s) + I + T + \\varepsilon$"
            "   —   lo que el receptor mide realmente",
            ha="center", fontsize=11)
    ax.text(x0 + 0.15, 0.0, "(esquema\nNO a escala)", fontsize=8,
            style="italic", va="center")
    ax.set_xlim(-0.2, x0 + 1.8)
    ax.set_ylim(-1.2, 2.05)
    ax.axis("off")
    ax.set_title("Anatomía de la pseudodistancia")
    fig.tight_layout()
    fig.savefig(AQUI / "fig3_anatomia.svg")
    plt.close(fig)


if __name__ == "__main__":
    fig1_sesgo_2d()
    fig2_convergencia()
    fig3_anatomia()
    print("figuras escritas:", [p.name for p in sorted(AQUI.glob("*.svg"))])
