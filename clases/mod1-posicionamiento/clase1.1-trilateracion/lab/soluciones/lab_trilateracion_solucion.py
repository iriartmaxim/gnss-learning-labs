"""Clase 1.1 — SOLUCIÓN del laboratorio: trilateración pura (sin reloj).

Resuelve (x, y, z) por Gauss-Newton a partir de rangos exactos, y corre los
experimentos: ambigüedad espejo con 3 balizas y Monte Carlo de geometría
buena vs. mala.

Uso: python lab_trilateracion_solucion.py   (desde lab/soluciones/)
"""
import json
from pathlib import Path

import numpy as np


# ---------------------------------------------------------------- funciones
def cargar_escenario():
    ruta = Path(__file__).resolve().parents[2] / "data" / "escenario_trilat.json"
    with open(ruta) as f:
        return json.load(f)


def rangos(x, balizas):
    """||b_i - x|| para cada baliza."""
    return np.linalg.norm(balizas - x, axis=1)


def matriz_J(x, balizas):
    """Jacobiano: fila i = -u_i^T, con u_i unitario receptor->baliza.
    Es la G de la clase 1.2 SIN la columna de reloj."""
    rho = rangos(x, balizas)
    u = (balizas - x) / rho[:, None]
    return -u


def paso_gauss_newton(x, balizas, r_med):
    dr = r_med - rangos(x, balizas)
    J = matriz_J(x, balizas)
    delta, *_ = np.linalg.lstsq(J, dr, rcond=None)
    return x + delta, np.linalg.norm(delta)


def resolver_trilat(balizas, r_med, x0=None, tol=1e-4, max_iter=30, traza=False):
    x = np.zeros(3) if x0 is None else np.array(x0, dtype=float)
    hist = [x.copy()]
    for _ in range(max_iter):
        x, paso = paso_gauss_newton(x, balizas, r_med)
        hist.append(x.copy())
        if paso < tol:
            break
    return (x, np.array(hist)) if traza else x


def punto_espejo(p, balizas3):
    """Reflexión de p respecto del plano definido por 3 balizas."""
    b0, b1, b2 = balizas3
    n = np.cross(b1 - b0, b2 - b0)
    n = n / np.linalg.norm(n)
    d = np.dot(p - b0, n)
    return p - 2 * d * n


# ------------------------------------------------------------------- script
if __name__ == "__main__":
    esc = cargar_escenario()
    buenas = np.array(esc["balizas_buenas_ecef_m"])
    malas = np.array(esc["balizas_malas_ecef_m"])
    r_true = np.array(esc["verdad"]["receptor_ecef_m"])

    rg_b = np.array(esc["rangos_buenas_m"])
    rg_b_n = np.array(esc["rangos_buenas_ruido1m_m"])
    rg_m_n = np.array(esc["rangos_malas_ruido1m_m"])

    print("=== Parte A: 4 balizas, rangos exactos, desde el centro de la Tierra ===")
    x, hist = resolver_trilat(buenas, rg_b, traza=True)
    err = np.linalg.norm(x - r_true)
    print(f"iteraciones: {len(hist) - 1} | error: {err:.3e} m")
    assert err < 1e-4, "VALIDACIÓN A FALLÓ"
    print("VALIDACIÓN A OK (< 0.1 mm)")

    print("\n=== Parte B: ruido sigma = 1 m ===")
    xb = resolver_trilat(buenas, rg_b_n)
    print(f"error con geometría buena: {np.linalg.norm(xb - r_true):.2f} m")

    print("\n=== Experimento 1: ambigüedad con 3 balizas (solución espejo) ===")
    b3, r3 = buenas[:3], rg_b[:3]
    x_a = resolver_trilat(b3, r3, x0=np.zeros(3))
    espejo_teorico = punto_espejo(r_true, b3)
    x_b = resolver_trilat(b3, r3, x0=espejo_teorico + 1e3)  # arrancar cerca del espejo
    print(f"solución 1 (arrancando del centro): error vs verdad = "
          f"{np.linalg.norm(x_a - r_true):.2e} m")
    print(f"solución 2 (arrancando cerca del espejo): dista de la verdad "
          f"{np.linalg.norm(x_b - r_true) / 1e3:.0f} km")
    res_a = np.abs(r3 - rangos(x_a, b3)).max()
    res_b = np.abs(r3 - rangos(x_b, b3)).max()
    print(f"residuo máximo solución 1: {res_a:.2e} m | solución 2: {res_b:.2e} m")
    assert res_a < 1e-4 and res_b < 1e-4, "ambas deben satisfacer los 3 rangos"
    print("-> AMBAS satisfacen exactamente las 3 distancias: ambigüedad real.")
    print(f"   (separación entre soluciones: "
          f"{np.linalg.norm(x_a - x_b) / 1e3:.0f} km)")

    print("\n=== Experimento 2: Monte Carlo, geometría buena vs. mala ===")
    rng = np.random.default_rng(7)
    N, sigma = 500, 1.0

    def mc(balizas, r_exacto):
        errs = []
        for _ in range(N):
            r_n = r_exacto + rng.normal(0, sigma, len(r_exacto))
            xs = resolver_trilat(balizas, r_n, x0=r_true + 100.0)
            errs.append(np.linalg.norm(xs - r_true))
        return np.sqrt(np.mean(np.square(errs)))  # error RMS 3D

    rg_m = np.array(esc["rangos_malas_m"])
    rms_buena = mc(buenas, rg_b)
    rms_mala = mc(malas, rg_m)

    def factor_geom(balizas):
        J = matriz_J(r_true, balizas)
        return np.sqrt(np.trace(np.linalg.inv(J.T @ J)))

    fb, fm = factor_geom(buenas), factor_geom(malas)
    print(f"RMS 3D con sigma=1 m -> buena: {rms_buena:.2f} m | mala: {rms_mala:.2f} m")
    print(f"factor geométrico sqrt(tr((J'J)^-1)) -> buena: {fb:.2f} | mala: {fm:.2f}")
    print(f"amplificación por geometría: x{rms_mala / rms_buena:.1f} "
          f"(mismo instrumento, mismo ruido)")
    assert rms_mala / rms_buena > 2.0, "la geometría mala debería amplificar >2x"
    print("-> la GEOMETRÍA manda: es la antesala del DOP (clase 1.4).")
