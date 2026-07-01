"""Clase 1.2 — SOLUCIÓN del laboratorio: PVT con pseudodistancias y sesgo de reloj.

Resuelve (x, y, z, c·dt) por Gauss-Newton desde el centro de la Tierra y corre
los cuatro experimentos guiados. Ver el enunciado en ../lab_pseudodistancias_TODO.py

Uso: python lab_pseudodistancias_solucion.py   (desde lab/soluciones/)
"""
import json
from pathlib import Path

import numpy as np

C = 299_792_458.0  # m/s


# ---------------------------------------------------------------- funciones
def cargar_escenario():
    ruta = Path(__file__).resolve().parents[2] / "data" / "escenario_5sats.json"
    with open(ruta) as f:
        esc = json.load(f)
    sats = np.array(esc["sat_ecef_m"])
    pr = np.array(esc["pseudodistancias_m"])
    pr_ruido = np.array(esc["pseudodistancias_ruido1m_m"])
    verdad = esc["verdad"]
    return sats, pr, pr_ruido, verdad


def rangos_geometricos(x, sats):
    """||r_sat - r_rx|| para cada satélite. x = [x, y, z, c*dt]."""
    return np.linalg.norm(sats - x[:3], axis=1)


def matriz_G(x, sats):
    """Fila i: [-u_i^T, 1], con u_i unitario receptor->satélite."""
    rho = rangos_geometricos(x, sats)
    u = (sats - x[:3]) / rho[:, None]
    return np.hstack([-u, np.ones((len(sats), 1))])


def paso_gauss_newton(x, sats, pr):
    """Un paso: resuelve G·delta = dP en mínimos cuadrados y actualiza."""
    rho = rangos_geometricos(x, sats)
    pred = rho + x[3]                 # pseudodistancia modelada
    dP = pr - pred                    # residuos prefit
    G = matriz_G(x, sats)
    delta, *_ = np.linalg.lstsq(G, dP, rcond=None)
    return x + delta, np.linalg.norm(delta)


def resolver_pvt(sats, pr, x0=None, tol=1e-4, max_iter=20, traza=False):
    x = np.zeros(4) if x0 is None else np.array(x0, dtype=float)
    historial = [x.copy()]
    for _ in range(max_iter):
        x, paso = paso_gauss_newton(x, sats, pr)
        historial.append(x.copy())
        if paso < tol:
            break
    return (x, np.array(historial)) if traza else x


def dop(x, sats):
    G = matriz_G(x, sats)
    Q = np.linalg.inv(G.T @ G)
    gdop = np.sqrt(np.trace(Q))
    pdop = np.sqrt(np.trace(Q[:3, :3]))
    tdop = np.sqrt(Q[3, 3])
    return gdop, pdop, tdop


# ------------------------------------------------------------------- script
if __name__ == "__main__":
    sats, pr, pr_ruido, verdad = cargar_escenario()
    r_true = np.array(verdad["receptor_ecef_m"])
    cdt_true = verdad["c_dt_receptor_m"]

    print("=== Parte A: solución sin ruido, arrancando del centro de la Tierra ===")
    x, hist = resolver_pvt(sats, pr, traza=True)
    err_pos = np.linalg.norm(x[:3] - r_true)
    err_cdt = abs(x[3] - cdt_true)
    print(f"iteraciones: {len(hist) - 1}")
    print(f"error posición: {err_pos:.3e} m   error c·dt: {err_cdt:.3e} m")
    print(f"c·dt estimado: {x[3]:.3f} m  ({x[3] / C * 1e3:.6f} ms)")
    assert err_pos < 1e-4 and err_cdt < 1e-4, "VALIDACIÓN A FALLÓ"
    print("VALIDACIÓN A OK (< 0.1 mm)")

    print("\n=== convergencia por iteración (norma del error de posición, m) ===")
    for i, xi in enumerate(hist):
        print(f"  it {i}: {np.linalg.norm(xi[:3] - r_true):.6e}")

    print("\n=== DOP del escenario ===")
    g, p, t = dop(x, sats)
    print(f"GDOP={g:.2f}  PDOP={p:.2f}  TDOP={t:.2f}")

    print("\n=== Parte B: con ruido sigma = 1 m ===")
    xn = resolver_pvt(sats, pr_ruido)
    print(f"error posición: {np.linalg.norm(xn[:3] - r_true):.2f} m   "
          f"error c·dt: {abs(xn[3] - cdt_true):.2f} m")

    print("\n=== Experimento 1: solo 3 incógnitas (ignorar el reloj) ===")
    # resolver solo (x,y,z) usando pseudodistancias sesgadas como si fueran rangos
    x3 = np.zeros(3)
    for _ in range(20):
        rho = np.linalg.norm(sats - x3, axis=1)
        u = (sats - x3) / rho[:, None]
        d, *_ = np.linalg.lstsq(-u, pr - rho, rcond=None)
        x3 = x3 + d
        if np.linalg.norm(d) < 1e-4:
            break
    print(f"error de posición ignorando el reloj: {np.linalg.norm(x3 - r_true) / 1e3:.1f} km "
          f"(c·dt real = {cdt_true / 1e3:.1f} km)")

    print("\n=== Experimento 2: solo 3 satélites, 4 incógnitas ===")
    x, hist = resolver_pvt(sats[:3], pr[:3], traza=True)
    print(f"solución con 3 sats (mínima norma de lstsq): error posición "
          f"{np.linalg.norm(x[:3] - r_true) / 1e3:.1f} km -> subdeterminado, NO confiable")

    print("\n=== Experimento 3: fallo de reloj en un satélite (puente a RAIM) ===")
    pr_falla = pr.copy()
    pr_falla[2] += 13.7e-6 * C  # caso 2016: 13.7 microsegundos
    xf = resolver_pvt(sats, pr_falla)
    resid = pr_falla - (rangos_geometricos(xf, sats) + xf[3])
    print(f"error de posición con fallo de 13.7 us en 1 sat: "
          f"{np.linalg.norm(xf[:3] - r_true):.1f} m")
    print(f"residuos postfit (m): {np.round(resid, 1)}  <- el fallo se 'reparte'")
