"""Genera las figuras SVG de la clase 0.3 (figuras como código, reproducibles).

Uso: python make_figures.py   (desde img/)

fig1: las tres anomalías (M, E, nu) sobre una elipse con e = 0.5
fig2: iteraciones de Newton para Kepler en función de la excentricidad
fig3: ground track de 24 h de un satélite tipo GPS (dos revoluciones)
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

plt.rcParams.update({"font.size": 11, "svg.fonttype": "none"})
AQUI = Path(__file__).resolve().parent

MU = 3.986004418e14
OMEGA_E = 7.2921151467e-5


def kepler(M, e, tol=1e-12):
    E = M if e < 0.8 else np.pi
    for _ in range(50):
        dE = (E - e * np.sin(E) - M) / (1 - e * np.cos(E))
        E -= dE
        if abs(dE) < tol:
            break
    return E


# ------------------------------------------------------------------- fig 1
def fig1_anomalias():
    a, e = 1.0, 0.5
    b = a * np.sqrt(1 - e**2)
    M = 1.0
    E = kepler(M, e)
    nu = 2 * np.arctan2(np.sqrt(1 + e) * np.sin(E / 2),
                        np.sqrt(1 - e) * np.cos(E / 2))
    r = a * (1 - e * np.cos(E))

    fig, ax = plt.subplots(figsize=(7.2, 5.8))
    t = np.linspace(0, 2 * np.pi, 400)
    ax.plot(a * np.cos(t), b * np.sin(t), color="tab:blue", lw=1.6,
            label="órbita (e = 0.5)")
    ax.plot(a * np.cos(t) - 0, a * np.sin(t), color="gray", lw=0.9, ls=":",
            label="círculo auxiliar (radio a)")
    ax.plot(-a * e, 0, "ko", ms=7)
    ax.annotate("foco (Tierra)", (-a * e, 0), textcoords="offset points",
                xytext=(6, -14), fontsize=9)
    ax.plot(0, 0, "k+", ms=9)
    # satélite y su proyección al círculo auxiliar
    xs, ys = a * np.cos(E), b * np.sin(E)
    ax.plot(xs, ys, "o", color="tab:red", ms=9, zorder=5, label="satélite")
    ax.plot([xs, xs], [ys, a * np.sin(E)], color="tab:red", lw=0.9, ls="--")
    ax.plot(a * np.cos(E), a * np.sin(E), "o", mfc="none", mec="tab:red", ms=7)
    # ángulos: nu desde el foco, E desde el centro
    ax.plot([-a * e, xs], [0, ys], color="tab:green", lw=1.4)
    ax.plot([0, a * np.cos(E)], [0, a * np.sin(E)], color="tab:purple", lw=1.2)
    ax.annotate(f"ν = {np.degrees(nu):.0f}° (verdadera, desde el foco)",
                (0.36, 0.30), fontsize=9, color="tab:green")
    ax.annotate(f"E = {np.degrees(E):.0f}° (excéntrica, desde el centro)",
                (0.36, 0.20), fontsize=9, color="tab:purple")
    ax.annotate(f"M = {np.degrees(1.0):.0f}° (media: reloj uniforme,\n"
                "NO es un ángulo geométrico visible)",
                (0.36, 0.05), fontsize=9, color="gray")
    ax.set_aspect("equal")
    ax.set_xlim(-1.6, 1.75)
    ax.set_ylim(-1.35, 1.35)
    ax.legend(loc="lower left", fontsize=8.5)
    ax.set_title("Las tres anomalías: M (tiempo) → E (Kepler) → ν (geometría)")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(AQUI / "fig1_anomalias.svg")
    plt.close(fig)


# ------------------------------------------------------------------- fig 2
def fig2_newton_vs_e():
    es = np.linspace(0.001, 0.95, 60)
    Ms = np.linspace(0.1, 2 * np.pi - 0.1, 25)
    iters = []
    for e in es:
        peor = 0
        for M in Ms:
            E = M if e < 0.8 else np.pi
            for k in range(1, 60):
                dE = (E - e * np.sin(E) - M) / (1 - e * np.cos(E))
                E -= dE
                if abs(dE) < 1e-12:
                    break
            peor = max(peor, k)
        iters.append(peor)

    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    ax.plot(es, iters, "o-", ms=3.5, color="tab:blue")
    ax.axvline(0.02, color="tab:green", ls="--", lw=1.2)
    ax.annotate("zona GNSS\n(e < 0.02)", (0.035, max(iters) * 0.85),
                color="tab:green", fontsize=9)
    ax.set_xlabel("excentricidad e")
    ax.set_ylabel("iteraciones de Newton (peor caso sobre M)")
    ax.set_title("Kepler por Newton: costo vs. excentricidad (tol 1e-12)")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(AQUI / "fig2_newton_vs_e.svg")
    plt.close(fig)


# ------------------------------------------------------------------- fig 3
def fig3_ground_track():
    # órbita tipo GPS: a=26560 km, e=0.01, i=55°
    a, e, inc = 26_560e3, 0.01, np.radians(55.0)
    Om0, w = np.radians(-30.0), np.radians(0.0)
    n = np.sqrt(MU / a**3)
    ts = np.arange(0, 86400, 60.0)
    lats, lons = [], []
    for t in ts:
        M = n * t
        E = kepler(M % (2 * np.pi), e)
        nu = 2 * np.arctan2(np.sqrt(1 + e) * np.sin(E / 2),
                            np.sqrt(1 - e) * np.cos(E / 2))
        r = a * (1 - e * np.cos(E))
        # plano orbital -> ECI (rotaciones 3-1-3) -> ECEF (rotación terrestre)
        u = w + nu
        x_eci = r * (np.cos(Om0) * np.cos(u) - np.sin(Om0) * np.sin(u) * np.cos(inc))
        y_eci = r * (np.sin(Om0) * np.cos(u) + np.cos(Om0) * np.sin(u) * np.cos(inc))
        z_eci = r * np.sin(u) * np.sin(inc)
        th = OMEGA_E * t
        x = np.cos(th) * x_eci + np.sin(th) * y_eci
        y = -np.sin(th) * x_eci + np.cos(th) * y_eci
        lats.append(np.degrees(np.arcsin(z_eci / r)))
        lons.append(np.degrees(np.arctan2(y, x)))
    lats, lons = np.array(lats), np.array(lons)

    fig, ax = plt.subplots(figsize=(9.4, 4.9))
    salto = np.abs(np.diff(lons)) > 180
    lons_plot = lons.copy()
    lons_plot[1:][salto] = np.nan       # cortar el wrap de ±180°
    ax.plot(lons_plot, lats, lw=1.2, color="tab:blue")
    ax.plot(lons[0], lats[0], "o", color="tab:green", ms=8, label="t = 0")
    ax.plot(lons[-1], lats[-1], "s", color="tab:red", ms=7, label="t = 24 h")
    ax.axhline(55, color="gray", ls=":", lw=0.9)
    ax.axhline(-55, color="gray", ls=":", lw=0.9)
    ax.annotate("|lat| ≤ i = 55°: el track nunca pasa de la inclinación",
                (-175, 58), fontsize=8.5, color="gray")
    ax.set_xlim(-180, 180)
    ax.set_ylim(-90, 90)
    ax.set_xlabel("longitud (°)")
    ax.set_ylabel("latitud (°)")
    ax.set_title("Ground track de 24 h de una órbita tipo GPS "
                 "(T ≈ 11h58m: 2 revoluciones, el track se repite)")
    ax.legend(loc="lower left", fontsize=9)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(AQUI / "fig3_ground_track.svg")
    plt.close(fig)


if __name__ == "__main__":
    fig1_anomalias()
    fig2_newton_vs_e()
    fig3_ground_track()
    print("figuras escritas:", [p.name for p in sorted(AQUI.glob("*.svg"))])
