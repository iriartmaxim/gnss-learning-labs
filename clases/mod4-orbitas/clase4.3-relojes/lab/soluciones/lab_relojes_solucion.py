#!/usr/bin/env python3
"""Solución 4.3 — Relojes: broadcast (af0/af1/af2) vs CLK preciso y estabilidad.

Compara la corrección de reloj broadcast contra el reloj preciso CLK por
satélite Galileo, y mide la estabilidad (desviación de Allan a 300 s) para
distinguir familias de reloj: el máser pasivo de hidrógeno (PHM) es más
estable que el rubidio (RAFS). Correr desde la raíz del repo (datos día 166).
"""
import json
import sys
import warnings
from datetime import datetime
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[4].parent
sys.path.insert(0, str(RAIZ / "clases/mod1-posicionamiento/clase1.3-efemerides/lab/soluciones"))
import georinex as gr  # noqa: E402
from lab_efemerides_solucion import elegir_efemeride  # noqa: E402

NAV = "data/raw/2026/166/BRDC00IGS_R_20261660000_01D_MN.rnx"
CLK = "data/raw/2026/166/COD0MGXFIN_20261660000_01D_30S_CLK.CLK"
INICIO = datetime(2026, 6, 14)
C = 299792458.0


def registros_clock(ds):
    """dict sv -> lista de dicts con af0/af1/af2 y toc (broadcast)."""
    out = {}
    for s in ds.sv.values:
        d = ds.sel(sv=s)
        recs = []
        for i in range(d.time.size):
            try:
                af0 = float(d["SVclockBias"].values[i])
                af1 = float(d["SVclockDrift"].values[i])
                af2 = float(d["SVclockDriftRate"].values[i])
            except (KeyError, IndexError):
                continue
            if not np.isfinite(af0):
                continue
            toc = (np.datetime64(d.time.values[i]).astype("datetime64[s]").astype(datetime)
                   - INICIO).total_seconds()
            recs.append({"af0": af0, "af1": af1, "af2": af2, "toc": toc, "Toe": toc})
        base = str(s).split("_")[0]
        if recs:
            out.setdefault(base, []).extend(recs)
    return out


def leer_clk(path):
    from collections import defaultdict
    datos = defaultdict(lambda: ([], []))
    for l in open(path):
        if not l.startswith("AS E"):
            continue
        p = l.split()
        s = p[1]
        t = (datetime(int(p[2]), int(p[3]), int(p[4]), int(p[5]), int(p[6]), int(float(p[7])))
             - INICIO).total_seconds()
        datos[s][0].append(t); datos[s][1].append(float(p[9]))
    return {s: (np.array(v[0]), np.array(v[1])) for s, v in datos.items()}


def clock_broadcast(recs, t):
    ef = elegir_efemeride(recs, t)
    dt = t - ef["toc"]
    return ef["af0"] + ef["af1"] * dt + ef["af2"] * dt**2


def allan_dev(y, tau_idx=1):
    """Desviación de Allan (overlapping) de una serie de bias de reloj y[s]
    muestreada uniformemente, para un paso tau_idx."""
    y = np.asarray(y)
    # frecuencia fraccional entre muestras
    d2 = y[2 * tau_idx:] - 2 * y[tau_idx:-tau_idx] + y[:-2 * tau_idx]
    return np.sqrt(np.mean(d2**2) / 2) if len(d2) else np.nan


def main() -> int:
    for f in (NAV, CLK):
        if not (RAIZ / f).exists():
            print(f"Falta {f} (clase 0.4).")
            return 1
    warnings.filterwarnings("ignore")
    print("cargando nav (E) y CLK (georinex, ~1 min)...")
    bc = registros_clock(gr.load(str(RAIZ / NAV), use="E"))
    clk = leer_clk(str(RAIZ / CLK))

    # 1) error broadcast vs preciso por satélite (RMS en metros), ventana 10-14h
    ts = 86400 + np.arange(10 * 3600, 14 * 3600, 300.0)
    rms_bc, allan = {}, {}
    for s in sorted(set(bc) & set(clk)):
        difs, serie = [], []
        tsc, csc = clk[s]
        for t in ts:
            try:
                cb = clock_broadcast(bc[s], t)
            except Exception:
                continue
            cp = float(np.interp(t, tsc, csc))
            difs.append((cb - cp) * C)          # a metros
            serie.append(cp)
        if len(difs) > 10:
            rms_bc[s] = float(np.sqrt(np.mean(np.square(difs))))
            allan[s] = allan_dev(serie, tau_idx=1)   # a 300 s

    rms_vals = np.array(list(rms_bc.values()))
    allan_vals = np.array([a for a in allan.values() if np.isfinite(a)])
    mejor = min(allan, key=allan.get)
    peor = max(allan, key=allan.get)
    print(f"\n[A] satélites con reloj comparado: {len(rms_bc)}")
    print(f"[B] error broadcast−preciso: mediana {np.median(rms_vals):.2f} m "
          f"(RMS en rango)")
    print(f"[C] estabilidad (Allan a 300 s), fracción de frecuencia:")
    print(f"      más estable: {mejor}  σy={allan[mejor]:.2e}  (probable PHM)")
    print(f"      menos estable: {peor}  σy={allan[peor]:.2e}  (probable RAFS)")
    print(f"      razón peor/mejor: ×{allan[peor]/allan[mejor]:.1f}")
    print(f"[D] el reloj broadcast corrige a nivel ~ns; el preciso, a ~0.1 ns")

    dest = RAIZ / "clases/mod4-orbitas/clase4.3-relojes/data"
    dest.mkdir(parents=True, exist_ok=True)
    json.dump({"n": len(rms_bc), "rms_med_m": float(np.median(rms_vals)),
               "allan_mejor": float(allan[mejor]), "sv_mejor": mejor,
               "allan_peor": float(allan[peor]), "sv_peor": peor,
               "rms_bc": rms_bc, "allan": {k: float(v) for k, v in allan.items()}},
              open(dest / "resultados_4_3.json", "w"), indent=1)

    assert len(rms_bc) > 10, "muy pocos satélites"
    assert np.median(rms_vals) < 3, "error de reloj broadcast fuera de rango"
    assert allan[peor] > allan[mejor], "debería haber dispersión de estabilidad"
    print("\nOK: relojes broadcast vs precisos y estabilidad por familia")
    return 0


if __name__ == "__main__":
    sys.exit(main())
