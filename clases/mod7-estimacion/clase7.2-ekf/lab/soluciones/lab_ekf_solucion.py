#!/usr/bin/env python3
"""Lab 7.2 — EKF sobre pseudodistancias y Doppler (SOLUCION).

El KF de la 7.1 filtraba SOLUCIONES; acá el filtro come OBSERVABLES:
medición no lineal (la raíz de la pseudodistancia), jacobiano = matriz
de geometría (1.4) y el Doppler como observable de velocidad/deriva.
A: arranque frío con toda la constelación -> equivale al LSQ en estático.
B: solo 3 satélites -> el modelo de dinámica sostiene la solución
   (y ahí está el riesgo: el error deriva sin que nada lo delate).
Correr desde la raíz del repo. Requiere data/raw/2026/166 (0.4).
"""
import json
import sys
import warnings
from pathlib import Path

import numpy as np

warnings.filterwarnings("ignore")
RAIZ = Path(__file__).resolve().parents[4].parent
sys.path.insert(0, str(RAIZ / "clases/mod1-posicionamiento/clase1.5-pvt/lab/soluciones"))
import georinex as gr
from lab_pvt_solucion import (C, GAMMA, NAV, OBS, POS_OFICIAL, a_sow,
                              elegir_efemeride, gauss_newton_pvt,
                              kepler_a_ecef, pseudorango_corregido,
                              registros_fnav)

F1 = 1575.42e6
LAM1 = C / F1


def vel_sat(ef, t_tx, dt=0.5):
    """Velocidad ECEF del satélite por derivada centrada del propagador."""
    return (kepler_a_ecef(ef, t_tx + dt) - kepler_a_ecef(ef, t_tx - dt)) / (2 * dt)


def medir_epoca(ep, t_rx, efs, rec_aprox):
    """Por satélite: (xyz_sat, Pc iono-free corregida, rr medida, v_sat)."""
    sats = []
    for s in ep.sv.values:
        s = str(s)
        if s not in efs:
            continue
        try:
            P1 = float(ep.sel(sv=s)["C1X"]); P5 = float(ep.sel(sv=s)["C5X"])
            D1 = float(ep.sel(sv=s)["D1X"])
        except (KeyError, TypeError):
            continue
        if not (np.isfinite(P1) and np.isfinite(P5) and np.isfinite(D1)):
            continue
        P = (GAMMA * P1 - P5) / (GAMMA - 1)
        ef = elegir_efemeride(efs[s], t_rx)
        xyz, Pc, el = pseudorango_corregido(ef, P, t_rx, rec_aprox)
        if el is not None and el < np.radians(10):
            continue
        rr = -LAM1 * D1                      # Doppler>0 = acercándose
        sats.append((s, xyz, Pc, rr, vel_sat(ef, t_rx - P / C)))
    return sats


def ekf_paso(x, P, sats, dt, sa=1e-3, sd=0.03, sig_p=1.0, sig_d=0.05,
             iterar=1, solo_p=False):
    """Un ciclo del EKF de 8 estados (pos, vel, cdt, cdt_dot).

    iterar>1 = IEKF: re-linealiza la corrección en la misma época (la
    corrección del EKF es UN paso de Gauss-Newton; iterada, es GN entero
    — imprescindible arrancando desde el centro de la Tierra).
    solo_p = usar solo pseudodistancias (arranque: el Doppler linealizado
    en cualquier lado mete violencia en los estados de velocidad).
    """
    F = np.eye(8)
    F[:3, 3:6] = np.eye(3) * dt
    F[6, 7] = dt
    q = lambda s2: s2 * np.array([[dt**4/4, dt**3/2], [dt**3/2, dt**2]])
    Q = np.zeros((8, 8))
    for i in range(3):
        b = q(sa**2)
        Q[i, i] = b[0, 0]; Q[i, i+3] = Q[i+3, i] = b[0, 1]; Q[i+3, i+3] = b[1, 1]
    b = q(sd**2)                                # deriva del reloj [m/s]
    Q[6, 6] = b[0, 0]; Q[6, 7] = Q[7, 6] = b[0, 1]; Q[7, 7] = b[1, 1]
    x = F @ x
    P = F @ P @ F.T + Q
    if not sats:
        return x, P, np.array([])
    # salto de reloj del receptor (reset de ±k ms, clásico en geodésicos):
    # si la innovación mediana de los códigos es ~k·c·1ms, va al estado cdt
    if sats:
        prev = np.array([Pc - (np.linalg.norm(xyz - x[:3]) + x[6])
                         for _, xyz, Pc, _, _ in sats])
        salto = np.round(np.median(prev) / (C * 1e-3))
        if abs(salto) >= 1:
            x[6] += salto * C * 1e-3
    y = np.array([])
    for _ in range(max(1, iterar)):
        H, z, h = [], [], []
        for s, xyz, Pc, rr, vs in sats:
            d = xyz - x[:3]
            rho = np.linalg.norm(d)
            u = d / rho
            H.append(np.r_[-u, 0, 0, 0, 1, 0]); z.append(Pc); h.append(rho + x[6])
            if not solo_p:
                H.append(np.r_[0, 0, 0, -u, 0, 1]); z.append(rr)
                h.append(u @ (vs - x[3:6]) + x[7])
        H, z, h = np.array(H), np.array(z), np.array(h)
        rr_sig = [sig_p**2] if solo_p else [sig_p**2, sig_d**2]
        R = np.diag(rr_sig * len(sats))
        y = z - h
        S = H @ P @ H.T + R
        K = P @ H.T @ np.linalg.inv(S)
        x = x + K @ y
    P = (np.eye(8) - K @ H) @ P
    return x, P, y


def main():
    print("cargando nav (georinex)...")
    efs = registros_fnav(gr.load(str(RAIZ / NAV), use="E"))
    print("cargando obs LPGS 12:00-13:00...")
    obs = gr.load(str(RAIZ / OBS), use="E",
                  tlim=("2026-06-15T12:00", "2026-06-15T13:00"))
    tiempos = obs.time.values
    dt = 30.0

    # --- A: arranque frío -> UNA pasada de GN (1.2/1.5) inicializa el EKF
    t0 = a_sow(tiempos[0])
    sats0 = medir_epoca(obs.sel(time=tiempos[0]), t0, efs, None)
    fx, _, _ = gauss_newton_pvt(np.array([s[1] for s in sats0]),
                                np.array([s[2] for s in sats0]))
    x = np.zeros(8); x[:3], x[6] = fx[:3], fx[3]
    P = np.diag([50.0**2] * 3 + [2.0**2] * 3 + [100.0**2, 500.0**2])
    err_ini = np.linalg.norm(fx[:3] - POS_OFICIAL)
    print(f"    inicialización GN (época 1, desde el centro de la Tierra): 3D {err_ini:.1f} m")
    err3d, vels, drifts = [], [], []
    for tt in tiempos[1:]:
        t_rx = a_sow(tt)
        sats = medir_epoca(obs.sel(time=tt), t_rx, efs, x[:3])
        x, P, _ = ekf_paso(x, P, sats, dt)
        err3d.append(np.linalg.norm(x[:3] - POS_OFICIAL))
        vels.append(np.linalg.norm(x[3:6])); drifts.append(x[7])
    err3d = np.array(err3d)
    conv = err3d[len(err3d)//3:]
    print(f"[A] EKF época 2: {err3d[0]:.1f} m | época 4: {err3d[2]:.1f} m")
    print(f"    3D medio (convergido): {conv.mean():.2f} m | final: {err3d[-1]:.2f} m")
    print(f"    |v| media: {np.mean(vels[40:])*1e3:.1f} mm/s | deriva reloj: {np.mean(drifts[40:]):+.3f} m/s")

    # --- B: solo 3 satélites la última media hora -----------------------
    x2 = x.copy(); P2 = P.copy()
    corte = len(tiempos) // 2
    ref = x2[:3].copy()                 # posición congelada para el cutoff
    err_b, sig_b = [], []
    elegidos = None
    for tt in tiempos[corte:]:
        t_rx = a_sow(tt)
        sats = medir_epoca(obs.sel(time=tt), t_rx, efs, ref)
        if elegidos is None:            # 3 satélites repartidos
            n = len(sats)
            elegidos = [sats[0][0], sats[n // 3][0], sats[2 * n // 3][0]]
        sats3 = [s for s in sats if s[0] in elegidos][:3]
        x2, P2, _ = ekf_paso(x2, P2, sats3, dt)
        err_b.append(np.linalg.norm(x2[:3] - POS_OFICIAL))
        sig_b.append(float(np.sqrt(np.trace(P2[:3, :3]))))
    err_b, sig_b = np.array(err_b), np.array(sig_b)
    print(f"[B] solo 3 SVs ({', '.join(elegidos)}) durante 30 min:")
    print(f"    sigue 'resolviendo': 3D a 5 min {err_b[9]/1e3:.1f} km | a 30 min {err_b[-1]/1e3:.0f} km")
    print(f"    y P MIENTE: sigma_pos dice {sig_b[0]:.0f} -> {sig_b[-1]:.0f} m "
          f"mientras el error real es {err_b[-1]/1e3:.0f} km (x{err_b[-1]/sig_b[-1]:,.0f} overconfident)")
    print("    (LSQ con 3 SVs: subdeterminado, ni solución da; el EKF sí da —")
    print("    una dirección entera quedó inobservable, los supuestos de ruido")
    print("    blanco se rompieron, y P ya no sabe lo que no sabe. Por eso")
    print("    existe la INTEGRIDAD: mod5 pone el perro guardián externo.)")

    assert err3d[2] < 20, "no convergió rápido"
    assert conv.mean() < 3.5, f"3D medio {conv.mean():.2f} m"
    assert np.mean(vels[40:]) * 1e3 < 30, "velocidad no nula"
    assert 1e3 < err_b[-1] < 5e6, "3 SVs fuera del rango esperado"
    assert err_b[-1] > 100 * sig_b[-1], "sin overconfidence no hay lección"
    assert err_b[-1] > conv.mean(), "3 SVs no puede ser mejor que la constelación"

    base = RAIZ / "clases/mod7-estimacion/clase7.2-ekf"
    json.dump({"err3d": err3d.tolist(), "err_3sv": err_b.tolist(),
               "sig_3sv": sig_b.tolist(),
               "v_mms": float(np.mean(vels[40:]) * 1e3),
               "drift_ms": float(np.mean(drifts[40:])),
               "elegidos": elegidos, "corte": int(corte)},
              open(base / "data" / "resultados_7_2.json", "w"), indent=1)
    print("exportado -> resultados_7_2.json")
    print("OK: EKF sobre observables, frío -> fino -> a ciegas con 3")
    return 0


if __name__ == "__main__":
    sys.exit(main())
