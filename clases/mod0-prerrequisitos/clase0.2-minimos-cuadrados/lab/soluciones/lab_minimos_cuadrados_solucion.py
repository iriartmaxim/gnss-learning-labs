"""Clase 0.2 — SOLUCIÓN: mínimos cuadrados, ponderado, Gauss-Newton y rotaciones.

Todo a mano con numpy: nada de scipy.optimize ni np.polyfit (salvo para
cotejar). Este es el motor matemático de TODO el módulo 1.

Uso: python lab_minimos_cuadrados_solucion.py   (desde lab/soluciones/)
"""
import json
from pathlib import Path

import numpy as np


def cargar():
    ruta = Path(__file__).resolve().parents[2] / "data" / "datos_ajuste.json"
    with open(ruta) as f:
        return json.load(f)


# ------------------------------------------------- LS lineal (ec. normales)
def ls_lineal(A, b):
    """x = (A'A)^-1 A'b vía ecuaciones normales (didáctico; en producción
    se usa QR/lstsq por estabilidad)."""
    return np.linalg.solve(A.T @ A, A.T @ b)


def ls_ponderado(A, b, sigmas):
    """Ponderado: W = diag(1/sigma^2). x = (A'WA)^-1 A'Wb."""
    W = np.diag(1.0 / np.asarray(sigmas) ** 2)
    return np.linalg.solve(A.T @ W @ A, A.T @ W @ b)


# ------------------------------------------------------------- Gauss-Newton
def gauss_newton(f, jac, p0, x, y, tol=1e-10, max_iter=50):
    p = np.array(p0, dtype=float)
    hist = [p.copy()]
    for _ in range(max_iter):
        r = y - f(x, p)               # residuos
        J = jac(x, p)                 # jacobiano de f respecto de p
        delta = np.linalg.solve(J.T @ J, J.T @ r)
        p = p + delta
        hist.append(p.copy())
        if np.linalg.norm(delta) < tol:
            break
    return p, np.array(hist)


# --------------------------------------------------------- rotaciones 3D
def Rx(t):
    c, s = np.cos(t), np.sin(t)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def Ry(t):
    c, s = np.cos(t), np.sin(t)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def Rz(t):
    c, s = np.cos(t), np.sin(t)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


if __name__ == "__main__":
    d = cargar()

    print("=== Parte A: recta por ecuaciones normales ===")
    x = np.array(d["recta"]["x"])
    y = np.array(d["recta"]["y"])
    sig = np.array(d["recta"]["sigma"])
    A = np.column_stack([np.ones_like(x), x])
    p_ls = ls_lineal(A, y)
    p_np, *_ = np.linalg.lstsq(A, y, rcond=None)
    print(f"a mano: a={p_ls[0]:.3f} b={p_ls[1]:.3f} | lstsq: "
          f"a={p_np[0]:.3f} b={p_np[1]:.3f} | verdad: (2, 3)")
    assert np.allclose(p_ls, p_np), "ecuaciones normales != lstsq"
    r = y - A @ p_ls
    print(f"ortogonalidad A'r = {np.abs(A.T @ r).max():.2e} (debe ser ~0)")
    assert np.abs(A.T @ r).max() < 1e-9

    print("\n=== Parte B: ponderado (la mitad de los datos es 6x más ruidosa) ===")
    p_w = ls_ponderado(A, y, sig)
    print(f"esta realización -> sin pesos: a={p_ls[0]:.3f} b={p_ls[1]:.3f} | "
          f"con pesos: a={p_w[0]:.3f} b={p_w[1]:.3f} | verdad: (2, 3)")
    print("(en UNA tirada cualquiera puede ganar; la ventaja es ESTADÍSTICA)")
    rngB = np.random.default_rng(123)
    err_ls2, err_w2 = 0.0, 0.0
    N = 1000
    for _ in range(N):
        yy = 2.0 + 3.0 * x + rngB.normal(0, sig)
        err_ls2 += np.sum((ls_lineal(A, yy) - [2, 3]) ** 2)
        err_w2 += np.sum((ls_ponderado(A, yy, sig) - [2, 3]) ** 2)
    rms_ls, rms_w = np.sqrt(err_ls2 / N), np.sqrt(err_w2 / N)
    print(f"Monte Carlo ({N} tiradas) -> RMS del error de parámetros: "
          f"sin pesos {rms_ls:.3f} | con pesos {rms_w:.3f} "
          f"(mejora x{rms_ls / rms_w:.1f})")
    assert rms_w < rms_ls, "en promedio, ponderar con los sigma correctos gana"
    print("-> ponderar por 1/sigma^2 reduce la VARIANZA del estimador. "
          "(En GNSS: pesar por elevación.)")

    print("\n=== Parte C: Gauss-Newton para y = p0*exp(p1*x), a mano ===")
    xe = np.array(d["exponencial"]["x"])
    ye = np.array(d["exponencial"]["y"])

    def f(x, p):
        return p[0] * np.exp(p[1] * x)

    def jac(x, p):
        e = np.exp(p[1] * x)
        return np.column_stack([e, p[0] * x * e])

    p_gn, hist = gauss_newton(f, jac, (1.0, 1.0), xe, ye)
    pasos = np.linalg.norm(np.diff(hist, axis=0), axis=1)
    print(f"convergió en {len(hist)-1} iteraciones a "
          f"p0={p_gn[0]:.4f}, p1={p_gn[1]:.4f} (verdad: 2, 0.5)")
    print("norma del paso por iteración:",
          " ".join(f"{s:.1e}" for s in pasos[:7]))
    assert np.allclose(p_gn, [2.0, 0.5], atol=0.05)

    print("\n=== Parte D: la covarianza del estimador (Monte Carlo) ===")
    rng = np.random.default_rng(7)
    sigma = 1.0
    Q = np.linalg.inv(A.T @ A)              # cov teórica = sigma^2 * Q
    sols = []
    for _ in range(2000):
        yy = 2.0 + 3.0 * x + rng.normal(0, sigma, len(x))
        sols.append(ls_lineal(A, yy))
    cov_emp = np.cov(np.array(sols).T)
    print("cov teórica sigma^2 (A'A)^-1:\n", np.round(sigma**2 * Q, 5))
    print("cov empírica (2000 corridas):\n", np.round(cov_emp, 5))
    ratio = cov_emp[0, 0] / (sigma**2 * Q[0, 0])
    print(f"cociente var(a) empírica/teórica: {ratio:.3f}")
    assert 0.85 < ratio < 1.15
    print("-> sigma^2 (A'A)^-1 PREDICE la dispersión real: la semilla del DOP.")

    print("\n=== Parte E: rotaciones 3D ===")
    for nombre, R in [("Rx(90°)", Rx(np.pi/2)), ("Rz(90°)", Rz(np.pi/2))]:
        assert np.allclose(R @ R.T, np.eye(3)) and np.isclose(np.linalg.det(R), 1)
    print("Rx, Ry, Rz son ortogonales con det=+1: OK")
    v = np.array([0.0, 0.0, 1.0])
    v1 = Rz(np.pi/2) @ Rx(np.pi/2) @ v
    v2 = Rx(np.pi/2) @ Rz(np.pi/2) @ v
    print(f"Rz(90)Rx(90) z = {np.round(v1, 3)} | Rx(90)Rz(90) z = {np.round(v2, 3)}")
    assert not np.allclose(v1, v2)
    print("-> el ORDEN importa: las rotaciones no conmutan "
          "(clave en órbita->ECEF, clase 0.3).")

    print("\n=== Parte F: condicionamiento (por qué existirá el DOP) ===")
    for ang_deg in (90, 30, 5):
        a2 = np.array([np.cos(np.radians(ang_deg)), np.sin(np.radians(ang_deg))])
        M = np.column_stack([[1.0, 0.0], a2])
        print(f"columnas a {ang_deg:>2}°: cond(M) = {np.linalg.cond(M):8.2f} | "
              f"sqrt(tr((M'M)^-1)) = {np.sqrt(np.trace(np.linalg.inv(M.T @ M))):6.2f}")
    print("-> columnas casi paralelas = mediciones casi redundantes = "
          "amplificación del error. En GNSS eso se llama DOP (clase 1.4).")
