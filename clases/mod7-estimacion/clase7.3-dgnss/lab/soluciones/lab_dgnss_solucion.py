#!/usr/bin/env python3
"""Solución 7.3 — DGNSS: LPGS (base conocida) corrige a CORD (rover).

Baseline La Plata–Córdoba ~715 km (largo a propósito): mide qué se cancela
(reloj/órbita, común) y qué decorrelaciona con la distancia (iono/tropo).
Reusa el motor PVT de 1.5. Correr desde la raíz del repo (datos día 166).
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
    C, GAMMA, NAV, POS_OFICIAL, a_sow, registros_fnav,
    elegir_efemeride, pseudorango_corregido, gauss_newton_pvt)

OBS_BASE = "data/raw/2026/166/LPGS00ARG_R_20261660000_01D_30S_MO.rnx"
OBS_ROVER = "data/raw/2026/166/CORD00ARG_R_20261660000_01D_30S_MO.rnx"
POS_BASE = POS_OFICIAL                                   # LPGS
POS_ROVER = np.array([2345503.9452, -4910842.9601, -3316365.5474])  # CORD (header)


def observables(ep):
    """dict sv -> pseudodistancia E1 monofrecuencia, para los Galileo.

    DGNSS de código se hace por banda: usamos E1 cruda (sin iono-free), que
    es donde la corrección diferencial rinde (la iono, común entre estaciones
    cercanas, se cancela). Robusto al código de tracking: LPGS C1X, CORD C1C.
    """
    e1 = next((c for c in ("C1X", "C1C", "C1B") if c in ep), None)
    if e1 is None:
        return {}
    out = {}
    for s in ep.sv.values:
        s = str(s)
        try:
            P1 = float(ep.sel(sv=s)[e1])
        except (KeyError, TypeError):
            continue
        if np.isfinite(P1):
            out[s] = P1
    return out


def prc_base(obs_sv, t_rx, efs, pos_base):
    """Corrección de pseudodistancia por satélite (PRC) desde la base conocida.

    PRC = rango_geométrico(base->sat) - pseudodistancia_corregida_base.
    Absorbe reloj de satélite, error de órbita y atmósfera vistos en la base.
    """
    prc = {}
    for s, Pif in obs_sv.items():
        if s not in efs:
            continue
        ef = elegir_efemeride(efs[s], t_rx)
        xyz, Pc, el = pseudorango_corregido(ef, Pif, t_rx, pos_base)
        if el is not None and el < np.radians(10):
            continue
        rango_geom = np.linalg.norm(xyz - pos_base)
        prc[s] = rango_geom - Pc
    return prc


def resolver_rover(obs_sv, t_rx, efs, pos_aprox, prc=None):
    xyz_l, pr_l = [], []
    for s, Pif in obs_sv.items():
        if s not in efs:
            continue
        ef = elegir_efemeride(efs[s], t_rx)
        xyz, Pc, el = pseudorango_corregido(ef, Pif, t_rx, pos_aprox)
        if el is not None and el < np.radians(10):
            continue
        if prc is not None:
            if s not in prc:
                continue
            Pc += prc[s]                     # aplico la corrección de la base
        xyz_l.append(xyz); pr_l.append(Pc)
    if len(xyz_l) < 4:
        return None
    fx, _, _ = gauss_newton_pvt(np.array(xyz_l), np.array(pr_l), pos_aprox)
    return fx[:3]


def main() -> int:
    if not (RAIZ / OBS_BASE).exists() or not (RAIZ / OBS_ROVER).exists():
        print("Faltan obs de LPGS y/o CORD del día 166 (clase 0.4).")
        return 1
    warnings.filterwarnings("ignore")
    print(f"baseline LPGS-CORD: {np.linalg.norm(POS_ROVER-POS_BASE)/1000:.1f} km")
    print("cargando nav+obs (georinex, ~1-2 min)...")
    efs = registros_fnav(gr.load(str(RAIZ / NAV), use="E"))
    tlim = ("2026-06-15T12:00", "2026-06-15T13:00")
    ob = gr.load(str(RAIZ / OBS_BASE), use="E", tlim=tlim)
    orv = gr.load(str(RAIZ / OBS_ROVER), use="E", tlim=tlim)

    # épocas comunes
    tb = {str(t)[:19]: i for i, t in enumerate(ob.time.values)}
    err_solo, err_dgnss = [], []
    for j, t in enumerate(orv.time.values):
        k = str(t)[:19]
        if k not in tb:
            continue
        t_rx = a_sow(t)
        obs_b = observables(ob.isel(time=tb[k]))
        obs_r = observables(orv.isel(time=j))
        prc = prc_base(obs_b, t_rx, efs, POS_BASE)
        fx_solo = resolver_rover(obs_r, t_rx, efs, POS_ROVER)
        fx_dg = resolver_rover(obs_r, t_rx, efs, POS_ROVER, prc)
        if fx_solo is not None and np.all(np.isfinite(fx_solo)):
            err_solo.append(np.linalg.norm(fx_solo - POS_ROVER))
        if fx_dg is not None and np.all(np.isfinite(fx_dg)):
            err_dgnss.append(np.linalg.norm(fx_dg - POS_ROVER))

    err_solo, err_dgnss = np.array(err_solo), np.array(err_dgnss)
    rms_solo = float(np.sqrt((err_solo**2).mean()))
    rms_dg = float(np.sqrt((err_dgnss**2).mean()))
    print(f"\n[A] epocas comunes procesadas: {len(err_dgnss)}")
    print(f"[B] RMS 3D rover SOLO (standalone): {rms_solo:.2f} m")
    print(f"[C] RMS 3D rover DGNSS (con PRC de LPGS): {rms_dg:.2f} m")
    print(f"[D] mejora: {100*(1-rms_dg/rms_solo):.0f}% (x{rms_solo/rms_dg:.2f})")
    print("[E] baseline 715 km: el reloj de satelite se cancela; "
          "iono/tropo decorrelacionan -> mejora parcial, no cm.")

    dest = RAIZ / "clases/mod7-estimacion/clase7.3-dgnss/data"
    dest.mkdir(parents=True, exist_ok=True)
    json.dump({"baseline_km": float(np.linalg.norm(POS_ROVER-POS_BASE)/1000),
               "n_ep": len(err_dgnss), "rms_solo": rms_solo, "rms_dgnss": rms_dg,
               "mejora_pct": 100*(1-rms_dg/rms_solo)},
              open(dest / "resultados_7_3.json", "w"), indent=1)

    assert rms_dg < rms_solo, "DGNSS deberia mejorar al standalone"
    print("\nOK: DGNSS con baseline largo - mejora parcial cuantificada")
    return 0


if __name__ == "__main__":
    sys.exit(main())
