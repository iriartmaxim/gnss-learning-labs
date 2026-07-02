"""Genera las figuras SVG de la clase 0.2 (figuras como código, reproducibles).

Uso: python make_figures.py   (desde img/)

fig1: recta ajustada con residuos, LS vs LS ponderado (usa data/)
fig2: convergencia de Gauss-Newton (norma del paso, escala log)
fig3: condicionamiento — nube de soluciones con columnas a 90° vs 10°
"""
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

plt.rcParams.update({"font.size": 11, "svg.fonttype": "none"})
AQUI = Path(__file__).resolve().parent


def cargar():
    with open(AQUI.parent / "data" / "datos_ajuste.json") as f:
        return json.load(f)


# ------------------------------------------------------------------- fig 1
def fig1_recta():
    d = cargar()["recta"]
    x, y = np.array(d["x"]), np.array(d["y"])
    sig = np.array(d["sigma"])
    A = np.column_stack([np.ones_like(x), x])
    p_ls = np.linalg.solve(A.T @ A, A.T @ y)
    W = np.diag(1 / sig**2)
    p_w = np.linalg.solve(A.T @ W @ A, A.T @ W @ y)

    fig, ax = plt.subplots(figsize=(7.4, 5.0))
    limpio = sig < 1
    ax.errorbar(x[limpio], y[limpio], yerr=sig[limpio], fmt="o", ms=5,
                color="tab:blue", label="datos σ = 0.5", capsize=2)
    ax.errorbar(x[~limpio], y[~limpio], yerr=sig[~limpio], fmt="s", ms=5,
                color="tab:orange", label="datos σ = 3.0", capsize=2)
    xs = np.array([x.min(), x.max()])
    ax.plot(xs, 2 + 3 * xs, "k--", lw=1.2, label="verdad: y = 2 + 3x")
    ax.plot(xs, p_ls[0] + p_ls[1] * xs, color="tab:red", lw=1.8,
            label=f"LS simple: y = {p_ls[0]:.2f} + {p_ls[1]:.2f}x")
    ax.plot(xs, p_w[0] + p_w[1] * xs, color="tab:green", lw=1.8,
            label=f"LS ponderado: y = {p_w[0]:.2f} + {p_w[1]:.2f}x")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title("Mínimos cuadrados: ponderar por 1/σ² protege de los datos sucios")
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(AQUI / "fig1_recta_ponderada.svg")
    plt.close(fig)


# ------------------------------------------------------------------- fig 2
def fig2_convergencia():
    d = cargar()["exponencial"]
    xe, ye = np.array(d["x"]), np.array(d["y"])

    def f(x, p):
        return p[0] * np.exp(p[1] * x)

    def jac(x, p):
        e = np.exp(p[1] * x)
        return np.column_stack([e, p[0] * x * e])

    p = np.array([1.0, 1.0])
    pasos = []
    for _ in range(12):
        r = ye - f(xe, p)
        J = jac(xe, p)
        delta = np.linalg.solve(J.T @ J, J.T @ r)
        p = p + delta
        pasos.append(np.linalg.norm(delta))
        if pasos[-1] < 1e-14:
            break

    fig, ax = plt.subplots(figsize=(7.0, 4.6))
    ax.semilogy(range(1, len(pasos) + 1), pasos, "o-", color="tab:blue")
    ax.set_xlabel("iteración")
    ax.set_ylabel("‖Δp‖ (norma del paso)")
    ax.set_title("Gauss-Newton sobre y = p₀·exp(p₁·x): convergencia (casi) cuadrática")
    ax.grid(alpha=0.3, which="both")
    ax.annotate("cada iteración ≈ duplica\nlos dígitos correctos",
                xy=(0.62, 0.55), xycoords="axes fraction", fontsize=9)
    fig.tight_layout()
    fig.savefig(AQUI / "fig2_convergencia_gn.svg")
    plt.close(fig)


# ------------------------------------------------------------------- fig 3
def fig3_condicionamiento():
    rng = np.random.default_rng(3)
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 4.8), sharex=True, sharey=True)
    for ax, ang in [(axes[0], 90), (axes[1], 10)]:
        a2 = np.array([np.cos(np.radians(ang)), np.sin(np.radians(ang))])
        M = np.column_stack([[1.0, 0.0], a2])
        b0 = M @ np.array([1.0, 1.0])       # verdad: x = (1, 1)
        sols = np.array([np.linalg.solve(M, b0 + rng.normal(0, 0.05, 2))
                         for _ in range(500)])
        ax.scatter(sols[:, 0], sols[:, 1], s=6, alpha=0.4)
        ax.plot(1, 1, "r*", ms=14)
        ax.set_title(f"columnas a {ang}° — cond = {np.linalg.cond(M):.1f}",
                     fontsize=10)
        ax.set_xlabel("x₁")
        ax.grid(alpha=0.3)
        ax.set_aspect("equal")
    axes[0].set_ylabel("x₂")
    fig.suptitle("Mismo ruido en las mediciones, distinta geometría de columnas",
                 fontsize=11)
    fig.tight_layout()
    fig.savefig(AQUI / "fig3_condicionamiento.svg")
    plt.close(fig)


if __name__ == "__main__":
    fig1_recta()
    fig2_convergencia()
    fig3_condicionamiento()
    print("figuras escritas:", [p.name for p in sorted(AQUI.glob("*.svg"))])
