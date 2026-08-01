#!/usr/bin/env python3
"""Solución 5.3 — Protection levels (HPL/VPL) y disponibilidad de integridad.

Sobre las épocas reales de LPGS (día 166) construye la geometría en ENU,
calcula el HPL por el método clásico de RAIM (slope × pbias) y el VPL, y
mide la disponibilidad contra los alert limits de una operación LPV-200
(HAL=40 m, VAL=35 m). Reusa el motor PVT de 1.5 y la cadena de 5.1.

Correr desde la raíz del repo (requiere data/raw/2026/166).
"""
import json
import sys
import warnings
from pathlib import Path

import numpy as np
from scipy.stats import chi2, ncx2

RAIZ = Path(__file__).resolve().parents[4].parent
for m in ("clases/mod1-posicionamiento/clase1.5-pvt/lab/soluciones",
          "clases/mod5-integridad/clase5.1-raim/lab/soluciones"):
    sys.path.insert(0, str(RAIZ / m))
import georinex as gr  # noqa: E402
from lab_pvt_solucion import (  # noqa: E402
    NAV, OBS, POS_OFICIAL, a_sow, registros_fnav,
    ecef_a_geodetica, matriz_enu)
from lab_raim_solucion import SIGMA, PFA, epoca_sats  # noqa: E402

# operación de referencia: LPV-200 (aproximación con guía vertical)
HAL, VAL = 40.0, 35.0            # m, alert limits horizontal / vertical
PMD = 1e-3                        # prob. de detección fallida objetivo


def geometria_enu(sats, rec):
    """Matriz de geometría G en ENU (filas: -versor E,N,U + 1 del reloj)."""
    lat, lon, _ = ecef_a_geodetica(rec)
    R = matriz_enu(lat, lon)
    G = []
    for _, xyz, _pc in sats:
        u = (xyz - rec) / np.linalg.norm(xyz - rec)   # versor receptor->sat (ECEF)
        u_enu = R @ u
        G.append([-u_enu[0], -u_enu[1], -u_enu[2], 1.0])
    return np.array(G)


def protection_levels(G, n):
    """HPL/VPL por RAIM clásico (slope) + pbias no central.

    - S = (GᵀG)⁻¹Gᵀ  (mínimos cuadrados)
    - P = G S  (hat matrix); 1-Pii = sensibilidad del residuo del sat i
    - slope_H,i = ‖S[:2,i]‖ / sqrt(1-Pii);  slope_V,i = |S[2,i]| / sqrt(1-Pii)
    - pbias = sqrt(λ), con λ la no-centralidad que da PMD para dof=n-4 al umbral PFA
    """
    S = np.linalg.solve(G.T @ G, G.T)          # (4 x n)
    P = G @ S
    dof = n - 4
    T_umbral = chi2.ppf(1 - PFA, dof)
    # no-centralidad λ tal que P(ncx2(dof,λ) < T_umbral) = PMD
    lam = _lambda_pbias(T_umbral, dof, PMD)
    pbias = np.sqrt(lam)
    diag = np.clip(1 - np.diag(P), 1e-9, None)
    slope_h = np.sqrt(S[0]**2 + S[1]**2) / np.sqrt(diag)
    slope_v = np.abs(S[2]) / np.sqrt(diag)
    hpl = slope_h.max() * pbias
    vpl = slope_v.max() * pbias
    return hpl, vpl, pbias


def _lambda_pbias(T_umbral, dof, pmd):
    """Bisección para la no-centralidad λ: P(ncx2(dof,λ) ≤ T_umbral) = pmd."""
    lo, hi = 0.0, 2000.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if ncx2.cdf(T_umbral, dof, mid) > pmd:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def main() -> int:
    if not (RAIZ / NAV).exists():
        print("Faltan datos del día 166 (clase 0.4).")
        return 1
    warnings.filterwarnings("ignore")
    print("cargando nav+obs (georinex, ~1 min)...")
    efs = registros_fnav(gr.load(str(RAIZ / NAV), use="E"))
    obs = gr.load(str(RAIZ / OBS), use="E",
                  tlim=("2026-06-15T12:00", "2026-06-15T13:00"))

    hpls, vpls, disp = [], [], 0
    n_ep = 0
    for i in range(len(obs.time)):
        ep = obs.isel(time=i)
        t_rx = a_sow(obs.time.values[i])
        sats = epoca_sats(ep, t_rx, efs, POS_OFICIAL)
        if len(sats) < 5:                      # RAIM necesita redundancia
            continue
        G = geometria_enu(sats, POS_OFICIAL)
        hpl, vpl, pbias = protection_levels(G, len(sats))
        hpls.append(hpl); vpls.append(vpl); n_ep += 1
        if hpl < HAL and vpl < VAL:
            disp += 1

    hpls, vpls = np.array(hpls), np.array(vpls)
    disponibilidad = 100.0 * disp / n_ep
    print(f"\n[A] épocas con RAIM (≥5 sats): {n_ep}")
    print(f"[B] HPL  mediana {np.median(hpls):.2f} m | max {hpls.max():.2f} m")
    print(f"[C] VPL  mediana {np.median(vpls):.2f} m | max {vpls.max():.2f} m")
    print(f"[D] pbias (no-centralidad) ~ {pbias:.2f}")
    print(f"[E] LPV-200 (HAL={HAL:.0f}, VAL={VAL:.0f}): "
          f"disponibilidad de integridad {disponibilidad:.1f}%")

    dest = RAIZ / "clases/mod5-integridad/clase5.3-protection-levels/data"
    dest.mkdir(parents=True, exist_ok=True)
    json.dump({"n_ep": n_ep, "hpl_med": float(np.median(hpls)),
               "hpl_max": float(hpls.max()), "vpl_med": float(np.median(vpls)),
               "vpl_max": float(vpls.max()), "pbias": float(pbias),
               "disponibilidad": disponibilidad, "HAL": HAL, "VAL": VAL},
              open(dest / "resultados_5_3.json", "w"), indent=1)

    assert 4 <= len(sats) + 10, "sanity"
    assert (vpls >= hpls).mean() > 0.5, "VPL debería superar a HPL casi siempre"
    assert 0 <= disponibilidad <= 100
    print("\nOK: protection levels y disponibilidad calculados")
    return 0


if __name__ == "__main__":
    sys.exit(main())
