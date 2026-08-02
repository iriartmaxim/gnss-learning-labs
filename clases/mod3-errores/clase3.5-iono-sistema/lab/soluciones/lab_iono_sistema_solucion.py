#!/usr/bin/env python3
"""Solución 3.5 — De medir la iono (3.2) a estimarla como sistema (VTEC).

La semilla de la estimación ionosférica a nivel sistema (grillas TEC tipo
SBAS/IGS): a partir del retardo iono medido por doble frecuencia (3.2), se
obtiene el TEC oblicuo por satélite, se proyecta a TEC vertical (VTEC) con
la función de oblicuidad, y se ubica en el punto ionosférico (IPP). El
conjunto de VTEC/IPP es lo que un centro de análisis interpola en un mapa.

Reusa la cadena de 3.2 (iono medida). Correr desde la raíz del repo
(requiere data/raw/2026/166).
"""
import json
import sys
import warnings
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[4].parent
for m in ("clases/mod1-posicionamiento/clase1.5-pvt/lab/soluciones",
          "clases/mod3-errores/clase3.1-ionosfera/lab/soluciones",
          "clases/mod3-errores/clase3.2-ionofree/lab/soluciones"):
    sys.path.insert(0, str(RAIZ / m))
import georinex as gr  # noqa: E402
from lab_pvt_solucion import (  # noqa: E402
    NAV, OBS, POS_OFICIAL, GAMMA, a_sow, registros_fnav,
    elegir_efemeride, pseudorango_corregido, ecef_a_geodetica, el_y_h)

F1, F5 = 1575.42e6, 1176.45e6
K_TEC = 40.3 / (F1**2)          # m de retardo L1 por TECU·1e16  → factor a TECU
RE = 6371e3
H_ION = 350e3                    # altura de la capa ionosférica (modelo de capa fina)


def oblicuidad(el):
    """Factor de mapeo oblicuo→vertical (capa fina a 350 km)."""
    return np.sqrt(1 - (RE * np.cos(el) / (RE + H_ION))**2)


def ipp_latlon(rec_llh, el, az):
    """Punto ionosférico (IPP): dónde el rayo cruza la capa fina (aprox.)."""
    lat, lon, _ = rec_llh
    psi = np.pi / 2 - el - np.arcsin(RE / (RE + H_ION) * np.cos(el))
    lat_ipp = np.arcsin(np.sin(lat) * np.cos(psi) + np.cos(lat) * np.sin(psi) * np.cos(az))
    lon_ipp = lon + np.arcsin(np.sin(psi) * np.sin(az) / np.cos(lat_ipp))
    return np.degrees(lat_ipp), np.degrees(lon_ipp)


def main() -> int:
    if not (RAIZ / OBS).exists():
        print("Faltan datos del día 166 (clase 0.4).")
        return 1
    warnings.filterwarnings("ignore")
    print("cargando nav+obs (georinex, ~1 min)...")
    efs = registros_fnav(gr.load(str(RAIZ / NAV), use="E"))
    obs = gr.load(str(RAIZ / OBS), use="E",
                  tlim=("2026-06-15T12:00", "2026-06-15T12:30"))
    lat, lon, h = ecef_a_geodetica(POS_OFICIAL)

    vtecs = []
    for i in range(len(obs.time)):
        ep = obs.isel(time=i)
        t_rx = a_sow(obs.time.values[i])
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
            # retardo iono en L1 desde doble frecuencia (3.2): I1 = (P5-P1)/(gamma-1)
            I1 = (P5 - P1) / (GAMMA - 1)
            ef = elegir_efemeride(efs[s], t_rx)
            xyz, _pc, el = pseudorango_corregido(ef, (GAMMA*P1-P5)/(GAMMA-1), t_rx, POS_OFICIAL)
            if el is None or el < np.radians(20):        # solo altos: menos ruido/multipath
                continue
            stec = I1 / (40.3 / F1**2) / 1e16            # TEC oblicuo [TECU]
            vtec = stec * oblicuidad(el)                  # a vertical
            if 0 < vtec < 100:                            # sanity
                vtecs.append(vtec)

    vtecs = np.array(vtecs)
    print(f"\n[A] muestras VTEC (satélites altos, 30 min): {len(vtecs)}")
    print(f"[B] VTEC sobre LPGS: mediana {np.median(vtecs):.1f} TECU "
          f"(rango {np.percentile(vtecs,10):.0f}–{np.percentile(vtecs,90):.0f})")
    print(f"[C] 1 TECU ≈ 0.162 m en L1 → {np.median(vtecs)*0.162:.1f} m de retardo vertical")
    print(f"[D] esto es la SEMILLA del mapa TEC: cada satélite da un VTEC en su "
          f"punto ionosférico; el sistema los interpola en una grilla")

    dest = RAIZ / "clases/mod3-errores/clase3.5-iono-sistema/data"
    dest.mkdir(parents=True, exist_ok=True)
    json.dump({"n": len(vtecs), "vtec_med": float(np.median(vtecs)),
               "vtec_p10": float(np.percentile(vtecs, 10)),
               "vtec_p90": float(np.percentile(vtecs, 90)),
               "vtecs": vtecs.tolist()}, open(dest / "resultados_3_5.json", "w"))

    assert len(vtecs) > 30, "muy pocas muestras"
    assert 5 < np.median(vtecs) < 60, f"VTEC fuera de rango físico: {np.median(vtecs)}"
    print("\nOK: VTEC estimado desde doble frecuencia — la semilla del mapa TEC")
    return 0


if __name__ == "__main__":
    sys.exit(main())
