#!/usr/bin/env python3
"""Lab 5.1 — RAIM por residuos: el test chi-cuadrado (SOLUCION).

Sobre las épocas reales del motor 1.5: estadístico de residuos, umbral
por probabilidad de falsa alarma, e inyección de fallos de 20-100 m en
una pseudodistancia para medir qué detecta y qué se escapa.
Correr desde la raíz del repo. Requiere data/raw/2026/166.
"""
import json
import sys
import warnings
from pathlib import Path

import numpy as np
from scipy.stats import chi2

warnings.filterwarnings("ignore")
RAIZ = Path(__file__).resolve().parents[4].parent
sys.path.insert(0, str(RAIZ / "clases/mod1-posicionamiento/clase1.5-pvt/lab/soluciones"))
import georinex as gr
from lab_pvt_solucion import (C, GAMMA, NAV, OBS, POS_OFICIAL, a_sow,
                              elegir_efemeride, gauss_newton_pvt,
                              pseudorango_corregido, registros_fnav)

SIGMA = 1.0                      # m, ruido nominal de la pseudodistancia IF
PFA = 1e-3                       # probabilidad de falsa alarma por época


def epoca_sats(ep, t_rx, efs, rec):
    sats = []
    for s in ep.sv.values:
        s = str(s)
        if s not in efs:
            continue
        try:
            P1 = float(ep.sel(sv=s)["C1X"]); P5 = float(ep.sel(sv=s)["C5X"])
        except (KeyError, TypeError):
            continue
        if not (np.isfinite(P1) and np.isfinite(P5)):
            continue
        Pif = (GAMMA * P1 - P5) / (GAMMA - 1)
        ef = elegir_efemeride(efs[s], t_rx)
        xyz, Pc, el = pseudorango_corregido(ef, Pif, t_rx, rec)
        if el is not None and el < np.radians(10):
            continue
        sats.append((s, xyz, Pc))
    return sats


def estadistico(sats, bias_en=None, bias=0.0):
    """LSQ + estadístico de residuos T = SSE/sigma^2 ~ chi2(n-4)."""
    xyz = np.array([s[1] for s in sats])
    pr = np.array([s[2] for s in sats], float)
    if bias_en is not None:
        pr[bias_en] += bias
    fx, _, _ = gauss_newton_pvt(xyz, pr)
    d = np.linalg.norm(xyz - fx[:3], axis=1)
    r = pr - (d + fx[3])
    T = float(r @ r / SIGMA**2)
    err3d = float(np.linalg.norm(fx[:3] - POS_OFICIAL))
    return T, err3d, len(sats), r


def main():
    print("cargando nav y obs (georinex)...")
    efs = registros_fnav(gr.load(str(RAIZ / NAV), use="E"))
    obs = gr.load(str(RAIZ / OBS), use="E",
                  tlim=("2026-06-15T12:00", "2026-06-15T13:00"))
    tiempos = obs.time.values

    # --- A: el estadístico en épocas limpias --------------------------
    Ts, ns = [], []
    for tt in tiempos:
        sats = epoca_sats(obs.sel(time=tt), a_sow(tt), efs, POS_OFICIAL)
        T, _, n, _ = estadistico(sats)
        Ts.append(T); ns.append(n)
    Ts, ns = np.array(Ts), np.array(ns)
    dof = int(np.median(ns)) - 4
    umbral = float(chi2.ppf(1 - PFA, dof))
    fa = int((Ts > umbral).sum())
    print(f"[A] {len(Ts)} épocas limpias | sats típicos: {int(np.median(ns))} (dof={dof})")
    print(f"    T medio {Ts.mean():.1f} | máx {Ts.max():.1f} | umbral chi2(Pfa={PFA}) = {umbral:.1f}")
    print(f"    épocas que disparan: {fa}/{len(Ts)} — y no son 'falsas': son")
    print("    épocas realmente sucias (multipath/satélite bajo). El RAIM")
    print("    también funciona de control de calidad del dataset.")

    # --- B: inyección de fallo en la época 12:00 ----------------------
    sats0 = epoca_sats(obs.isel(time=0), a_sow(tiempos[0]), efs, POS_OFICIAL)
    T0, e0, n0, _ = estadistico(sats0)
    print(f"[B] época 12:00 ({n0} sats): T limpio {T0:.1f} | err 3D {e0:.2f} m")
    filas = []
    for b in (20, 50, 100):
        Tb, eb, _, _ = estadistico(sats0, bias_en=0, bias=b)
        det = "DETECTADO" if Tb > umbral else "se escapa"
        print(f"    bias {b:3d} m en {sats0[0][0]}: T={Tb:8.1f} | err 3D {eb:6.2f} m -> {det}")
        filas.append((b, Tb, eb, Tb > umbral))

    # --- C: el bias mínimo detectable ---------------------------------
    bs = np.arange(2, 41, 2.0)
    Tc = np.array([estadistico(sats0, 0, b)[0] for b in bs])
    b_min = float(bs[np.argmax(Tc > umbral)])
    print(f"[C] barrido 2-40 m: el primer bias que dispara es {b_min:.0f} m")
    print("    (con 8 sats, buena geometría y sigma=1 el RAIM es fino; en")
    print("     operación sigma real y peor geometría agrandan la zona ciega —")
    print("     cuantificar ese 'peor caso' es exactamente el PL de 5.3)")

    assert fa <= 6, f"épocas que disparan: {fa}"
    assert filas[1][3] and filas[2][3], "50/100 m deben detectarse"
    assert estadistico(sats0, 0, 2.0)[0] < umbral, "2 m no debería disparar"
    assert 2 <= b_min <= 12, f"b_min {b_min}"

    base = RAIZ / "clases/mod5-integridad/clase5.1-raim"
    json.dump({"T_serie": Ts.tolist(), "umbral": umbral, "dof": dof,
               "fa": fa, "T0": T0, "filas": [list(f) for f in filas],
               "barrido_b": bs.tolist(), "barrido_T": Tc.tolist(),
               "b_min": b_min},
              open(base / "data" / "resultados_5_1.json", "w"), indent=1)
    print("exportado -> resultados_5_1.json")
    print("OK: RAIM por residuos sobre épocas reales, con fallos inyectados")
    return 0


if __name__ == "__main__":
    sys.exit(main())
