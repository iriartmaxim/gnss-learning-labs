#!/usr/bin/env python3
"""Solución 7.5 — Fusión GNSS+INS loosely-coupled (2D, IMU sintética).

El INS (acelerómetros) integra y deriva; el GNSS ancla pero tiene cortes.
Un filtro de Kalman los fusiona: el INS puentea los cortes de GNSS y el
GNSS frena la deriva del INS. Todo sintético y determinista (seed fija).

Correr desde cualquier lado (no usa datos externos):
    python3 clases/mod7-estimacion/clase7.5-fusion/lab/soluciones/lab_fusion_solucion.py
"""
import json
import sys
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[4].parent
DT = 0.1                       # IMU a 10 Hz
T = 120.0                      # 2 minutos
GNSS_CADA = 10                 # GNSS a 1 Hz (cada 10 pasos de IMU)
CORTE = (50.0, 80.0)          # apagón de GNSS entre 50 s y 80 s
SIG_GNSS = 3.0                 # m, ruido de la posición GNSS
SIG_ACC = 0.05                 # m/s^2, ruido del acelerómetro
BIAS_ACC = np.array([0.02, -0.03])   # m/s^2, sesgo constante del IMU


def trayectoria():
    """Verdad: arranca yendo al este, dobla suavemente. Devuelve pos y acel."""
    n = int(T / DT)
    t = np.arange(n) * DT
    # aceleración verdadera: un giro suave (senoidal) en y
    a = np.column_stack([0.1 * np.cos(0.05 * t), 0.15 * np.sin(0.05 * t)])
    v = np.cumsum(a, axis=0) * DT + np.array([8.0, 0.0])   # v inicial 8 m/s este
    p = np.cumsum(v, axis=0) * DT
    return t, p, v, a


def ins_solo(a_med):
    """Dead-reckoning: integra la aceleración medida (con sesgo+ruido)."""
    v = np.array([8.0, 0.0]); p = np.array([0.0, 0.0])
    out = []
    for am in a_med:
        v = v + am * DT
        p = p + v * DT
        out.append(p.copy())
    return np.array(out)


def fusion_kf(a_med, gnss):
    """KF loosely-coupled: estado [x,y,vx,vy]; predice con IMU, corrige con GNSS."""
    F = np.array([[1, 0, DT, 0], [0, 1, 0, DT], [0, 0, 1, 0], [0, 0, 0, 1]], float)
    B = np.array([[0.5 * DT**2, 0], [0, 0.5 * DT**2], [DT, 0], [0, DT]])
    H = np.array([[1, 0, 0, 0], [0, 1, 0, 0]], float)
    Q = np.diag([0.01, 0.01, 0.02, 0.02])          # ruido de proceso (IMU imperfecto)
    R = np.eye(2) * SIG_GNSS**2
    x = np.array([0.0, 0.0, 8.0, 0.0]); P = np.eye(4) * 10
    out = []
    for k, am in enumerate(a_med):
        x = F @ x + B @ am                          # predicción con IMU
        P = F @ P @ F.T + Q
        if gnss[k] is not None:                     # corrección con GNSS
            z = gnss[k]
            S = H @ P @ H.T + R
            K = P @ H.T @ np.linalg.inv(S)
            x = x + K @ (z - H @ x)
            P = (np.eye(4) - K @ H) @ P
        out.append(x[:2].copy())
    return np.array(out)


def main() -> int:
    rng = np.random.default_rng(42)
    t, p, v, a = trayectoria()
    n = len(t)
    a_med = a + BIAS_ACC + rng.normal(0, SIG_ACC, a.shape)   # IMU real

    # GNSS: fix a 1 Hz con ruido, salvo durante el corte
    gnss = [None] * n
    err_gnss = []
    for k in range(n):
        if k % GNSS_CADA == 0 and not (CORTE[0] <= t[k] <= CORTE[1]):
            z = p[k] + rng.normal(0, SIG_GNSS, 2)
            gnss[k] = z
            err_gnss.append(np.linalg.norm(z - p[k]))

    p_ins = ins_solo(a_med)
    p_kf = fusion_kf(a_med, gnss)

    err_ins = np.linalg.norm(p_ins - p, axis=1)
    err_kf = np.linalg.norm(p_kf - p, axis=1)
    corte = (t >= CORTE[0]) & (t <= CORTE[1])

    rms_gnss = float(np.sqrt(np.mean(np.square(err_gnss))))
    rms_ins = float(np.sqrt(np.mean(err_ins**2)))
    rms_kf = float(np.sqrt(np.mean(err_kf**2)))
    print(f"[A] RMS GNSS solo (época con fix): {rms_gnss:.2f} m")
    print(f"[B] RMS INS solo (deriva libre):   {rms_ins:.2f} m")
    print(f"[C] RMS fusión KF:                 {rms_kf:.2f} m")
    print(f"[D] error máx durante el corte ({CORTE[0]:.0f}-{CORTE[1]:.0f}s):")
    print(f"      INS solo:  {err_ins[corte].max():.2f} m")
    print(f"      fusión KF: {err_kf[corte].max():.2f} m  <- el INS puentea, el KF acota")
    print(f"[E] fuera del corte el GNSS frena la deriva del INS; "
          f"dentro, el INS mantiene la solución")

    dest = RAIZ / "clases/mod7-estimacion/clase7.5-fusion/data"
    dest.mkdir(parents=True, exist_ok=True)
    json.dump({"rms_gnss": rms_gnss, "rms_ins": rms_ins, "rms_kf": rms_kf,
               "corte": list(CORTE), "max_ins_corte": float(err_ins[corte].max()),
               "max_kf_corte": float(err_kf[corte].max()),
               "t": t.tolist(), "err_ins": err_ins.tolist(),
               "err_kf": err_kf.tolist(),
               "px": p[:, 0].tolist(), "py": p[:, 1].tolist(),
               "kfx": p_kf[:, 0].tolist(), "kfy": p_kf[:, 1].tolist(),
               "insx": p_ins[:, 0].tolist(), "insy": p_ins[:, 1].tolist()},
              open(dest / "resultados_7_5.json", "w"))

    assert rms_kf < rms_gnss, "la fusión debería mejorar al GNSS solo"
    assert rms_kf < rms_ins, "la fusión debería mejorar al INS solo"
    assert err_kf[corte].max() < err_ins[corte].max(), "el KF debe acotar el corte"
    print("\nOK: fusión GNSS+INS — el KF supera a cada sensor por separado")
    return 0


if __name__ == "__main__":
    sys.exit(main())
