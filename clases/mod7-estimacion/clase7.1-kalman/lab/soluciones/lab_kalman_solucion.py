#!/usr/bin/env python3
"""Lab 7.1 — Filtro de Kalman desde cero (SOLUCION).

A: KF 1D para una constante (la ganancia se apaga sola, var ~ sigma^2/n).
B: KF 1D pos+vel para una rampa (el modelo de dinámica hace el trabajo).
C: KF 3D velocidad-constante sobre la serie ENU REAL del motor 1.5
   (121 épocas, LPGS estática): reduce el scatter, estima velocidad ~0 y
   sus innovaciones salen blancas — y lo que NO puede arreglar: el sesgo.
Correr desde la raíz del repo. Requiere resultados_1_5.json (clase 1.5).
"""
import json
import sys
from pathlib import Path

import numpy as np

rng = np.random.default_rng(71)


def kf(z, F, H, Q, R, x0, P0):
    """KF lineal genérico. Devuelve estados filtrados e innovaciones."""
    x, P = x0.copy(), P0.copy()
    xs, inns = [], []
    for zk in z:
        x = F @ x                      # predicción
        P = F @ P @ F.T + Q
        y = zk - H @ x                 # innovación (lo que la medición sorprende)
        S = H @ P @ H.T + R
        K = P @ H.T @ np.linalg.inv(S) # ganancia: cuánto le creo a la medición
        x = x + K @ y
        P = (np.eye(len(x)) - K @ H) @ P
        xs.append(x.copy()); inns.append(y.copy())
    return np.array(xs), np.array(inns)


def parte_a():
    verdad = 5.0
    z = verdad + rng.normal(0, 1.0, 50)
    F = np.eye(1); H = np.eye(1); Q = np.zeros((1, 1)); R = np.eye(1)
    xs, _ = kf(z[:, None], F, H, Q, R, np.zeros(1), np.eye(1) * 100)
    err_kf = abs(xs[-1, 0] - verdad)
    err_prom = abs(z.mean() - verdad)
    print(f"[A] constante 5.0 con sigma=1, 50 mediciones:")
    print(f"    KF final: {xs[-1,0]:.4f} | promedio: {z.mean():.4f} "
          f"(coinciden: el KF de una constante ES el promedio recursivo)")
    assert abs(xs[-1, 0] - z.mean()) < 5e-3, "KF != promedio"
    return err_kf, err_prom


def parte_b():
    dt = 1.0
    t = np.arange(80.0)
    verdad_v = 0.7
    pos = 2.0 + verdad_v * t
    z = pos + rng.normal(0, 2.0, len(t))
    F = np.array([[1, dt], [0, 1]]); H = np.array([[1.0, 0]])
    sa = 0.05
    Q = sa**2 * np.array([[dt**4/4, dt**3/2], [dt**3/2, dt**2]])
    R = np.array([[4.0]])
    xs, _ = kf(z[:, None], F, H, Q, R, np.zeros(2), np.eye(2) * 100)
    v_est = xs[-1, 1]
    rms_z = np.sqrt(((z - pos)**2).mean())
    rms_kf = np.sqrt(((xs[:, 0] - pos)**2).mean())
    print(f"[B] rampa v=0.7 con sigma=2: RMS crudo {rms_z:.2f} m -> "
          f"KF {rms_kf:.2f} m | v estimada {v_est:.3f}")
    assert abs(v_est - verdad_v) < 0.05 and rms_kf < 0.5 * rms_z
    return rms_z, rms_kf, v_est


def parte_c():
    d = json.load(open("clases/mod1-posicionamiento/clase1.5-pvt/data/resultados_1_5.json"))
    S = np.array(d["serie"])           # columnas: t_sow, E, N, U, nsats
    t, enu = S[:, 0], S[:, 1:4]
    dt = float(np.median(np.diff(t)))  # 30 s
    # estado: (E, N, U, vE, vN, vU); medición: ENU
    F = np.eye(6); F[:3, 3:] = np.eye(3) * dt
    H = np.hstack([np.eye(3), np.zeros((3, 3))])
    sa = 1e-4                          # m/s^2: la estación NO acelera
    q = sa**2 * np.array([[dt**4/4, dt**3/2], [dt**3/2, dt**2]])
    Q = np.zeros((6, 6))
    for i in range(3):
        Q[i, i] = q[0, 0]; Q[i, i+3] = Q[i+3, i] = q[0, 1]; Q[i+3, i+3] = q[1, 1]
    R = np.diag(enu.std(axis=0)**2)
    x0 = np.zeros(6); x0[:3] = enu[0]
    xs, inns = kf(enu, F, H, Q, R, x0, np.eye(6))
    filt = xs[:, :3]
    n_est = len(enu) // 3              # estadísticas tras converger (últimos 2/3)
    std_raw = enu[n_est:].std(axis=0)
    std_kf = filt[n_est:].std(axis=0)
    rms_raw = np.sqrt((enu**2).mean(axis=0))
    rms_kf = np.sqrt((filt[n_est:]**2).mean(axis=0))
    v_final = xs[-1, 3:] * 1e3         # mm/s
    rho1 = np.array([np.corrcoef(inns[1:, i], inns[:-1, i])[0, 1] for i in range(3)])
    print(f"[C] serie REAL 1.5 (121 épocas, LPGS estática, dt={dt:.0f} s):")
    print(f"    scatter E/N/U crudo : {std_raw[0]:.2f} / {std_raw[1]:.2f} / {std_raw[2]:.2f} m")
    print(f"    scatter E/N/U KF    : {std_kf[0]:.2f} / {std_kf[1]:.2f} / {std_kf[2]:.2f} m "
          f"(x{(std_raw/std_kf).mean():.0f} menos)")
    print(f"    RMS vs oficial crudo: {rms_raw[0]:.2f} / {rms_raw[1]:.2f} / {rms_raw[2]:.2f} m")
    print(f"    RMS vs oficial KF   : {rms_kf[0]:.2f} / {rms_kf[1]:.2f} / {rms_kf[2]:.2f} m"
          "   <- el piso que queda es SESGO, no ruido")
    print(f"    velocidad estimada  : ({v_final[0]:+.1f}, {v_final[1]:+.1f}, {v_final[2]:+.1f}) mm/s ~ 0")
    print(f"    innovaciones rho(1) : {rho1[0]:+.2f} / {rho1[1]:+.2f} / {rho1[2]:+.2f}  (blancas si ~0)")
    print("    nota: el scatter baja ~x2 y no mas — el resto NO es ruido")
    print("    blanco sino error correlacionado (iono/multipath): si forzas")
    print("    mas suavizado (Q menor), rho(1) se vuelve positivo y el test")
    print("    de blancura te delata el modelo. El sesgo, ni te lo toca.")
    assert np.allclose(rms_raw, [0.72, 0.752, 1.448], atol=5e-3), "serie 1.5 cambió"
    assert (std_kf < 0.75 * std_raw).all(), "el KF no redujo el scatter"
    assert (np.abs(v_final) < 10).all(), "velocidad no nula en estación estática"
    assert (np.abs(rho1) < 0.35).all(), "innovaciones no blancas: modelo de ruido mal"
    return dict(std_raw=std_raw.tolist(), std_kf=std_kf.tolist(),
                rms_raw=rms_raw.tolist(), rms_kf=rms_kf.tolist(),
                v_mms=v_final.tolist(), rho1=rho1.tolist(),
                serie_raw=enu.tolist(), serie_kf=filt.tolist(), t=t.tolist())


def main():
    a = parte_a(); b = parte_b(); c = parte_c()
    base = Path("clases/mod7-estimacion/clase7.1-kalman")
    json.dump({"A": a, "B": b, "C": {k: v for k, v in c.items()
               if k not in ("serie_raw", "serie_kf", "t")},
               "series": {k: c[k] for k in ("serie_raw", "serie_kf", "t")}},
              open(base / "data" / "resultados_7_1.json", "w"), indent=1)
    print("exportado -> resultados_7_1.json")
    print("OK: KF didactico + KF sobre la serie real, innovaciones blancas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
