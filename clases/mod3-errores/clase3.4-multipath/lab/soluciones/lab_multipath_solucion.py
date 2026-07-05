#!/usr/bin/env python3
"""Solución 3.4 — multipath y ruido: la combinación código−fase.

MP1 = P1 − (1+k)·Φ1 + k·Φ5   con k = 2/(γ−1): elimina geometría,
relojes, tropo E iono — queda multipath + ruido + una constante
(ambigüedades) que se resta por arco. Tres validaciones con LPGS:
  A. las magnitudes (dm en E1, menos en E5a: el chip 10× más corto)
  B. la firma en elevación (las reflexiones viven cerca del horizonte)
  C. la repetición sideral GALILEO: la geometría vuelve cada 10 días
     (17 revoluciones), no cada día como GPS — día 166 vs día 176.

Correr desde la raíz del repo (dos RINEX de obs: ~5-7 min).
Exporta data/resultados_3_4.json.
"""
import json
import sys
import warnings
from pathlib import Path

import numpy as np

warnings.filterwarnings("ignore")
RAIZ = Path(__file__).resolve().parents[4].parent
sys.path.insert(0, str(RAIZ / "clases/mod1-posicionamiento/clase1.5-pvt/lab/soluciones"))
sys.path.insert(0, str(RAIZ / "clases/mod3-errores/clase3.2-ionofree/lab/soluciones"))
import lab_pvt_solucion as pvt
from lab_pvt_solucion import (C, GAMMA, NAV, OBS, POS_OFICIAL, a_sow,
                              elegir_efemeride, kepler_a_ecef)
from lab_ionofree_solucion import el_az

BASE34 = Path("clases/mod3-errores/clase3.4-multipath")
OBS176 = "data/raw/2026/176/LPGS00ARG_R_20261760000_01D_30S_MO.rnx"
LAM1, LAM5 = C / 1575.42e6, C / 1176.45e6
K1 = 2.0 / (GAMMA - 1.0)                 # 2.521
K5 = 2.0 * GAMMA / (GAMMA - 1.0)         # 4.521
LAG_TEORICO = -2359.0    # s: 10 días sidéreos − 10 días solares


def combinaciones_mp(o):
    """MP1 y MP5 [m] de un satélite (DataArray por época)."""
    P1, P5 = o["C1X"].values, o["C5X"].values
    F1, F5 = o["L1X"].values * LAM1, o["L5X"].values * LAM5
    mp1 = P1 - (1 + K1) * F1 + K1 * F5
    mp5 = P5 - K5 * F1 + (K5 - 1) * F5
    return mp1, mp5


def sub_arcos(v, salto=1.0, min_ep=10):
    """Tramos válidos [i, j) partidos por NaN y por saltos (> salto m,
    típicamente un salto de ciclo en alguna fase)."""
    arcos, n, i = [], len(v), 0
    while i < n:
        if np.isnan(v[i]):
            i += 1
            continue
        j = i
        while j + 1 < n and not np.isnan(v[j + 1]) \
                and abs(v[j + 1] - v[j]) < salto:
            j += 1
        if j - i + 1 >= min_ep:
            arcos.append((i, j + 1))
        i = j + 1
    return arcos


def detrend(v):
    """Resta la media por sub-arco (absorbe ambigüedades y sesgos)."""
    out = np.full_like(v, np.nan)
    for i, j in sub_arcos(v):
        out[i:j] = v[i:j] - np.nanmean(v[i:j])
    return out


def sigma_ruido(v):
    """σ del ruido por diferencias sucesivas: el multipath (períodos de
    minutos) casi no cambia en 30 s ⇒ σ(ΔMP)/√2 ≈ ruido del código."""
    difs = []
    for i, j in sub_arcos(v):
        difs.append(np.diff(v[i:j]))
    d = np.concatenate(difs) if difs else np.array([np.nan])
    return float(np.std(d) / np.sqrt(2))


def elevaciones(obs, efs):
    """Matriz el[tiempo, sat] en grados."""
    el = np.full((len(obs.time), len(obs.sv)), np.nan)
    for it, t64 in enumerate(obs.time.values):
        t = a_sow(t64)
        for isv, sv in enumerate(obs.sv.values):
            if sv not in efs:
                continue
            ef = elegir_efemeride(efs[sv], t)
            el[it, isv] = el_az(kepler_a_ecef(ef, t), POS_OFICIAL)[0]
    return el


def grilla_dia(times64, valores):
    """Serie en grilla de 30 s del día (2880 huecos) para correlacionar."""
    g = np.full(2880, np.nan)
    t0 = times64.astype("datetime64[D]")
    idx = np.round((times64 - t0) / np.timedelta64(1, "s") / 30).astype(int)
    g[idx] = valores
    return g


def corr_lag(gA, gB, L):
    """Correlación de gA[i] con gB[i+L] (L en muestras de 30 s)."""
    n = len(gA)
    i0, i1 = max(0, -L), min(n, n - L)
    a, b = gA[i0:i1], gB[i0 + L:i1 + L]
    ok = ~np.isnan(a) & ~np.isnan(b)
    if ok.sum() < 50:
        return np.nan
    return float(np.corrcoef(a[ok], b[ok])[0, 1])


def main():
    import georinex as gr
    print("=== Parte A: la combinación código−fase ===")
    print(f"  γ = {GAMMA:.4f} | MP1 = P1 − {1+K1:.3f}·Φ1 + {K1:.3f}·Φ5")
    print(f"  MP5 = P5 − {K5:.3f}·Φ1 + {K5-1:.3f}·Φ5")
    print("  (elimina geometría, relojes, tropo e iono: queda MP + ruido + cte)")

    print("\n  cargando nav + obs día 166 (paciencia)...")
    ds = gr.load(str(RAIZ / NAV), use="E")
    efs = pvt.registros_fnav(ds)
    obs = gr.load(str(RAIZ / OBS), use="E",
                  tlim=("2026-06-15T12:00", "2026-06-15T13:30"))
    el = elevaciones(obs, efs)

    svs = list(obs.sv.values)
    MP1 = np.full((len(obs.time), len(svs)), np.nan)
    MP5 = np.full_like(MP1, np.nan)
    for isv, sv in enumerate(svs):
        mp1, mp5 = combinaciones_mp(obs.sel(sv=sv))
        MP1[:, isv], MP5[:, isv] = detrend(mp1), detrend(mp5)

    rms1 = float(np.sqrt(np.nanmean(MP1**2)))
    rms5 = float(np.sqrt(np.nanmean(MP5**2)))
    sig1 = float(np.nanmedian([sigma_ruido(MP1[:, i])
                               for i in range(len(svs))]))
    sig5 = float(np.nanmedian([sigma_ruido(MP5[:, i])
                               for i in range(len(svs))]))
    print(f"\n  RMS MP1 = {rms1*100:.1f} cm | RMS MP5 = {rms5*100:.1f} cm "
          f"(chip E1 293 m vs E5a 29 m)")
    print(f"  ruido (dif. sucesivas): σ1 ≈ {sig1*100:.1f} cm | "
          f"σ5 ≈ {sig5*100:.1f} cm")
    print("  σ(dif)/√2 ≈ RMS total: a 30 s las muestras ya casi no se")
    print("  correlacionan — LPGS tiene antena choke ring: el multipath")
    print("  está mitigado por hardware y lo que sobrevive es ruido +")
    print("  reflejos de baja elevación (Parte B) y lentos (Parte C)")

    print("\n=== Parte B: la firma en elevación ===")
    bordes = [(10, 20), (20, 30), (30, 45), (45, 60), (60, 90)]
    bins = []
    for lo, hi in bordes:
        m = (el >= lo) & (el < hi)
        r1 = float(np.sqrt(np.nanmean(MP1[m]**2))) if m.any() else np.nan
        r5 = float(np.sqrt(np.nanmean(MP5[m]**2))) if m.any() else np.nan
        n = int(np.isfinite(MP1[m]).sum())
        bins.append({"lo": lo, "hi": hi, "rms1_cm": round(r1*100, 1),
                     "rms5_cm": round(r5*100, 1), "n": n})
        print(f"  {lo:2d}-{hi:2d}°: MP1 {r1*100:5.1f} cm | MP5 {r5*100:5.1f} cm"
              f"  (n={n})")
    print("  E5a gana ~20-25% en elevaciones medias/altas (chip 10× más")
    print("  corto recorta reflejos lejanos); debajo de 20° se empareja:")
    print("  los reflejos cercanos y el tracking al límite golpean a ambos")

    print("\n=== Parte C: la repetición sideral Galileo (10 días) ===")
    el_med = np.nanmean(el, axis=0)
    stds = [float(np.nanstd(MP1[:, i])) for i in range(len(svs))]
    neps = [int(np.isfinite(MP1[:, i]).sum()) for i in range(len(svs))]
    cand = [i for i in range(len(svs)) if neps[i] >= 120]
    isel = max(cand, key=lambda i: stds[i])
    sv_sid = svs[isel]
    print(f"  satélite elegido: {sv_sid} (std {stds[isel]*100:.1f} cm, "
          f"elev media {el_med[isel]:.0f}°)")
    print("  cargando obs día 176 (11:15-13:00)...")
    obs2 = gr.load(str(RAIZ / OBS176), use="E",
                   tlim=("2026-06-25T11:15", "2026-06-25T13:00"))
    mp1b, _ = combinaciones_mp(obs2.sel(sv=sv_sid))
    mp1b = detrend(mp1b)
    g166 = grilla_dia(obs.time.values, MP1[:, isel])
    g176 = grilla_dia(obs2.time.values, mp1b)
    lags = list(range(-95, -59)) + [0]
    corrs = {L: corr_lag(g166, g176, L) for L in lags}
    L_opt = max((L for L in lags if L != 0 and np.isfinite(corrs[L])),
                key=lambda L: corrs[L])
    print(f"  lag óptimo: {L_opt*30} s (teórico {LAG_TEORICO:.0f} s) | "
          f"correlación {corrs[L_opt]:.2f}")
    print(f"  correlación a lag 0 (mismo reloj, sin shift): "
          f"{corrs[0] if np.isfinite(corrs[0]) else float('nan'):.2f}")
    print("  la geometría (y SUS reflejos) volvió 39 min antes, 10 días después:")
    print("  el multipath no es ruido — es determinista si el entorno no cambió")

    # asserts de la clase
    assert 0.10 < rms1 < 0.60 and rms5 < rms1
    assert bins[0]["rms1_cm"] > bins[-1]["rms1_cm"]
    assert abs(L_opt * 30 - LAG_TEORICO) <= 90
    assert corrs[L_opt] > 0.5 and corrs[L_opt] - abs(corrs.get(0) or 0) > 0.2

    ihi = max(range(len(svs)), key=lambda i: el_med[i] if neps[i] > 100 else -1)
    ilo = min(range(len(svs)), key=lambda i: el_med[i] if neps[i] > 100 else 99)
    tmin = ((obs.time.values - obs.time.values[0])
            / np.timedelta64(1, "m")).astype(float)
    tmin2 = ((obs2.time.values - obs2.time.values[0])
             / np.timedelta64(1, "m")).astype(float)

    def serie(i):
        return {"sv": svs[i], "el_med": round(float(el_med[i]), 1),
                "t_min": [round(float(x), 1) for x in tmin],
                "mp1_cm": [None if not np.isfinite(v) else round(v*100, 1)
                           for v in MP1[:, i]],
                "el": [None if not np.isfinite(v) else round(v, 1)
                       for v in el[:, i]]}

    out = {"rms1_cm": round(rms1*100, 1), "rms5_cm": round(rms5*100, 1),
           "sig1_cm": round(sig1*100, 1), "sig5_cm": round(sig5*100, 1),
           "bins": bins, "sat_alto": serie(ihi), "sat_bajo": serie(ilo),
           "sideral": {"sv": sv_sid, "lag_opt_s": L_opt*30,
                       "lag_teorico_s": LAG_TEORICO,
                       "corr_opt": round(corrs[L_opt], 3),
                       "corr_lag0": None if not np.isfinite(corrs[0])
                       else round(corrs[0], 3),
                       "lags_s": [L*30 for L in lags if L != 0],
                       "corrs": [None if not np.isfinite(corrs[L])
                                 else round(corrs[L], 3)
                                 for L in lags if L != 0],
                       "t166_min": [round(float(x), 1) for x in tmin],
                       "mp166_cm": [None if not np.isfinite(v)
                                    else round(v*100, 1)
                                    for v in MP1[:, isel]],
                       "t176_min": [round(float(x), 1) for x in tmin2],
                       "mp176_cm": [None if not np.isfinite(v)
                                    else round(v*100, 1) for v in mp1b]}}
    dest = RAIZ / BASE34 / "data" / "resultados_3_4.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, separators=(",", ":")))
    print(f"\nexportado -> {dest.name}")
    print("OK: multipath medido, con firma de elevación y memoria sideral")


if __name__ == "__main__":
    main()
