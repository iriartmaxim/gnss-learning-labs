#!/usr/bin/env python3
"""Solución 7.4 — PPP-lite (solo código): órbitas SP3 + relojes CLK + ZWD.

Reemplaza la efeméride broadcast por productos precisos (SP3 orbita, CLK
reloj) sobre observables iono-free E1/E5a, y estima el retardo húmedo
troposférico (ZWD) como quinta incógnita. Compara el error contra la
solución broadcast en las mismas épocas. Reusa el motor de 1.5.

Correr desde la raíz del repo (requiere data/raw/2026/166: obs, SP3, CLK).
"""
import json
import sys
import warnings
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[4].parent
sys.path.insert(0, str(RAIZ / "clases/mod1-posicionamiento/clase1.5-pvt/lab/soluciones"))
import georinex as gr  # noqa: E402
from lab_pvt_solucion import (  # noqa: E402
    C, GAMMA, OBS, POS_OFICIAL, a_sow, ecef_a_geodetica, matriz_enu, el_y_h)

SP3 = "data/raw/2026/166/COD0MGXFIN_20261660000_01D_05M_ORB.SP3"
CLK = "data/raw/2026/166/COD0MGXFIN_20261660000_01D_30S_CLK.CLK"
OMEGA_E = 7.2921151467e-5


def leer_sp3(path):
    """dict sat -> (t_sow[], xyz_km[Nx3]).  Solo Galileo (E)."""
    datos = {}
    t = None
    for l in open(path):
        if l.startswith("*"):
            p = l.split()
            from datetime import datetime
            d = datetime(int(p[1]), int(p[2]), int(p[3]), int(p[4]), int(p[5]), int(float(p[6])))
            t = (d - datetime(2026, 6, 14)).total_seconds()
        elif l.startswith("PE") and t is not None:
            s = l[1:4]
            x, y, z = float(l[4:18]), float(l[18:32]), float(l[32:46])
            datos.setdefault(s, ([], []))
            datos[s][0].append(t); datos[s][1].append([x, y, z])
    return {s: (np.array(v[0]), np.array(v[1])) for s, v in datos.items()}


def leer_clk(path):
    """dict sat -> (t_sow[], clk_s[]).  Líneas 'AS E.. ...'."""
    from datetime import datetime
    datos = {}
    for l in open(path):
        if not l.startswith("AS E"):
            continue
        p = l.split()
        s = p[1]
        d = datetime(int(p[2]), int(p[3]), int(p[4]), int(p[5]), int(p[6]), int(float(p[7])))
        t = (d - datetime(2026, 6, 14)).total_seconds()
        datos.setdefault(s, ([], []))
        datos[s][0].append(t); datos[s][1].append(float(p[9]))
    return {s: (np.array(v[0]), np.array(v[1])) for s, v in datos.items()}


def lagrange_xyz(ts, xyz, t, orden=10):
    """Interpola posición (km) en t con Lagrange de 'orden' nodos centrados."""
    i = np.searchsorted(ts, t)
    lo = max(0, i - orden // 2); hi = min(len(ts), lo + orden)
    lo = max(0, hi - orden)
    tt = ts[lo:hi]; xx = xyz[lo:hi]
    L = np.ones(len(tt))
    for k in range(len(tt)):
        for m in range(len(tt)):
            if m != k:
                L[k] *= (t - tt[m]) / (tt[k] - tt[m])
    return L @ xx


def clk_interp(ts, cs, t):
    return float(np.interp(t, ts, cs))


def observables_if(ep):
    e1 = next((c for c in ("C1X", "C1C") if c in ep), None)
    e5 = next((c for c in ("C5X", "C5Q") if c in ep), None)
    out = {}
    for s in ep.sv.values:
        s = str(s)
        try:
            P1 = float(ep.sel(sv=s)[e1]); P5 = float(ep.sel(sv=s)[e5])
        except (KeyError, TypeError):
            continue
        if np.isfinite(P1) and np.isfinite(P5):
            out[s] = (GAMMA * P1 - P5) / (GAMMA - 1)
    return out


_CACHE = {}


def sat_ecef_preciso(sp3, s, t_tx):
    """Posición ECEF (m) del satélite en t_tx por SP3 (memoizado)."""
    key = (s, round(t_tx, 2))
    p = _CACHE.get(key)
    if p is None:
        ts, xyz = sp3[s]
        p = lagrange_xyz(ts, xyz, t_tx) * 1000.0
        _CACHE[key] = p
    return p


def dt_relativista(sp3, s, t_tx):
    """Corrección relativista periódica [s]: -2(r·v)/c².

    Los relojes precisos (CLK) NO la incluyen — hay que sumarla. r,v en
    ECEF (m, m/s); v por diferencia finita de la interpolación SP3.
    """
    r = sat_ecef_preciso(sp3, s, t_tx)
    dt = 0.5
    v = (sat_ecef_preciso(sp3, s, t_tx + dt) - sat_ecef_preciso(sp3, s, t_tx - dt)) / (2 * dt)
    return -2.0 * (r @ v) / C**2


def resolver_ppp(obs_if, t_rx, sp3, clk, x0, zwd=0.0):
    """PVT con productos precisos: incógnitas (x,y,z,c·dt). Gauss-Newton.

    Órbita SP3, reloj CLK + relatividad, tropo Saastamoinen (ZHD fijo + un
    ZWD que se pasa como argumento; ver estimar_zwd para la versión batch).
    """
    x = np.array([*x0[:3], 0.0])
    for _ in range(8):
        rows, res = [], []
        for s, Pif in obs_if.items():
            if s not in sp3 or s not in clk:
                continue
            tau = Pif / C
            for _k in range(2):
                xyz = sat_ecef_preciso(sp3, s, t_rx - tau)
                a = OMEGA_E * tau
                rot = np.array([[np.cos(a), np.sin(a), 0],
                                [-np.sin(a), np.cos(a), 0], [0, 0, 1]])
                xyz = rot @ xyz
                tau = np.linalg.norm(xyz - x[:3]) / C
            el, hh = el_y_h(xyz, x[:3])
            if el < np.radians(10):
                continue
            dt_sat = (clk_interp(*clk[s], t_rx - tau)
                      + dt_relativista(sp3, s, t_rx - tau))
            zhd = 2.3 * np.exp(-hh / 7160.0) / np.sin(el)
            m_wet = 1.0 / np.sin(el)
            rho = np.linalg.norm(xyz - x[:3])
            pred = rho + x[3] - C * dt_sat + zhd + zwd * m_wet
            u = (x[:3] - xyz) / rho
            rows.append([u[0], u[1], u[2], 1.0])
            res.append(Pif - pred)
        if len(rows) < 4:
            return None
        dx, *_ = np.linalg.lstsq(np.array(rows), np.array(res), rcond=None)
        x = x + dx
        if np.linalg.norm(dx[:3]) < 1e-3:
            break
    return x


def main() -> int:
    for f in (OBS, SP3, CLK):
        if not (RAIZ / f).exists():
            print(f"Falta {f} (clase 0.4: SP3/CLK vía CDDIS).")
            return 1
    warnings.filterwarnings("ignore")
    print("cargando SP3, CLK y obs (georinex, ~1-2 min)...")
    sp3 = leer_sp3(str(RAIZ / SP3))
    clk = leer_clk(str(RAIZ / CLK))
    obs = gr.load(str(RAIZ / OBS), use="E", tlim=("2026-06-15T12:00", "2026-06-15T13:00"))

    def rms_para(zwd):
        errs = []
        for i in range(len(obs.time)):
            t_rx = a_sow(obs.time.values[i])
            x = resolver_ppp(observables_if(obs.isel(time=i)), t_rx, sp3, clk,
                             np.array([*POS_OFICIAL]), zwd=zwd)
            if x is None or not np.all(np.isfinite(x)):
                continue
            enu = matriz_enu(*ecef_a_geodetica(POS_OFICIAL)[:2]) @ (x[:3] - POS_OFICIAL)
            errs.append(np.linalg.norm(enu))
        return np.array(errs)

    errs0 = rms_para(0.0)
    rms0 = float(np.sqrt((errs0**2).mean()))
    # ⭐⭐⭐: estimar UN ZWD para toda la hora (observable en batch, no por época)
    grid = np.linspace(0.0, 0.5, 26)
    rmss = [float(np.sqrt((rms_para(z)**2).mean())) for z in grid]
    z_best = float(grid[int(np.argmin(rmss))])
    rms_best = min(rmss)

    print(f"\n[A] épocas PPP-lite: {len(errs0)}")
    print(f"[B] RMS 3D con ZWD=0: {rms0:.2f} m")
    print(f"[C] ZWD óptimo (batch, toda la hora): {z_best*100:.0f} cm")
    print(f"[D] RMS 3D con ZWD óptimo: {rms_best:.2f} m")
    print(f"[E] referencia broadcast (clase 1.5): 3D ~1.95 m → "
          f"PPP-lite {'MEJORA' if rms_best < 1.95 else 'no mejora'} "
          f"(solo código: techo dm-m; para cm hace falta fase)")

    dest = RAIZ / "clases/mod7-estimacion/clase7.4-ppp/data"
    dest.mkdir(parents=True, exist_ok=True)
    json.dump({"n_ep": len(errs0), "rms_zwd0": rms0, "zwd_cm": z_best*100,
               "rms_best": rms_best, "ref_broadcast": 1.95,
               "grid_zwd": grid.tolist(), "grid_rms": rmss},
              open(dest / "resultados_7_4.json", "w"), indent=1)

    assert len(errs0) > 50, "muy pocas épocas resueltas"
    assert 0 < rms_best < 3, f"RMS fuera de rango razonable: {rms_best}"
    assert rms_best <= rms0 + 1e-9, "el ZWD óptimo no puede empeorar"
    print("\nOK: PPP-lite con productos precisos y ZWD batch")
    return 0


if __name__ == "__main__":
    sys.exit(main())
