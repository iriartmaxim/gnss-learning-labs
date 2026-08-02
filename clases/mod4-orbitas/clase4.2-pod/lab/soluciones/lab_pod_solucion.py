#!/usr/bin/env python3
"""Solución 4.2 — Broadcast vs órbitas precisas (SP3) con descomposición RTN.

Propaga la efeméride broadcast y la compara contra el SP3 preciso,
descomponiendo la diferencia en Radial / Along-track / Cross-track (RTN)
por constelación (Galileo y GPS). La radial es la que pesa en el rango.
Reusa el propagador de 1.3. Correr desde la raíz del repo (datos día 166).
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
from lab_efemerides_solucion import (  # noqa: E402
    kepler_a_ecef, elegir_efemeride)

# campos keplerianos de propagación comunes a GPS y Galileo (sin los
# específicos de Galileo como DataSrc/IODnav, que GPS no trae)
CAMPOS = ["sqrtA", "Eccentricity", "M0", "DeltaN", "Omega0", "OmegaDot",
          "Io", "IDOT", "omega", "Cuc", "Cus", "Crc", "Crs", "Cic", "Cis", "Toe"]

NAV = "data/raw/2026/166/BRDC00IGS_R_20261660000_01D_MN.rnx"
SP3 = "data/raw/2026/166/COD0MGXFIN_20261660000_01D_05M_ORB.SP3"
INICIO = datetime(2026, 6, 14)


def registros(ds, sistema):
    """dict sv -> lista de efemérides (una fuente por sistema)."""
    out = {}
    svs = [s for s in ds.sv.values if str(s).startswith(sistema)]
    for s in svs:
        d = ds.sel(sv=s)
        recs = []
        for i in range(d.time.size):
            r = {}
            ok = True
            for c in CAMPOS:
                if c not in d:
                    ok = False; break
                v = float(d[c].values[i]) if d[c].values.ndim else float(d[c].values)
                r[c] = v
            if not ok or not np.isfinite(r.get("sqrtA", np.nan)):
                continue
            r["toc"] = (np.datetime64(d.time.values[i]).astype("datetime64[s]").astype(datetime)
                        - INICIO).total_seconds()
            r["Toe"] = r.get("Toe", r["toc"])
            recs.append(r)
        base = str(s).split("_")[0]
        if recs:
            out.setdefault(base, []).extend(recs)
    return out


def leer_sp3_multi(path):
    """dict sat -> (t_sow[], xyz_km[Nx3]) para todos los sistemas."""
    datos, t = {}, None
    for l in open(path):
        if l.startswith("*"):
            p = l.split()
            d = datetime(int(p[1]), int(p[2]), int(p[3]), int(p[4]), int(p[5]), int(float(p[6])))
            t = (d - INICIO).total_seconds()
        elif l.startswith("P") and t is not None and l[1] in "GERC":
            s = l[1:4]
            try:
                x, y, z = float(l[4:18]), float(l[18:32]), float(l[32:46])
            except ValueError:
                continue
            datos.setdefault(s, ([], []))
            datos[s][0].append(t); datos[s][1].append([x, y, z])
    return {s: (np.array(v[0]), np.array(v[1])) for s, v in datos.items()}


def lagrange(ts, xyz, t, orden=10):
    i = np.searchsorted(ts, t)
    lo = max(0, min(i - orden // 2, len(ts) - orden)); hi = lo + orden
    tt, xx = ts[lo:hi], xyz[lo:hi]
    L = np.ones(len(tt))
    for k in range(len(tt)):
        for m in range(len(tt)):
            if m != k:
                L[k] *= (t - tt[m]) / (tt[k] - tt[m])
    return L @ xx


def rtn(dpos, r_sat, v_sat):
    """Proyecta la diferencia dpos (m) en Radial/Along/Cross."""
    R = r_sat / np.linalg.norm(r_sat)
    Cr = np.cross(r_sat, v_sat); Cr /= np.linalg.norm(Cr)   # cross-track (normal)
    A = np.cross(Cr, R)                                       # along-track
    return np.array([dpos @ R, dpos @ A, dpos @ Cr])


def evaluar(sistema, efs, sp3):
    """RMS RTN broadcast-SP3 para un sistema, muestreando cada 5 min 10:00-14:00."""
    difs = []
    # día 166 = lunes = 1 día tras el inicio de semana → sumar 86400 a la hora del día
    ts_eval = 86400 + np.arange(10 * 3600, 14 * 3600 + 1, 300.0)  # sow (seg. de semana)
    for s, recs in efs.items():
        if s not in sp3:
            continue
        for t in ts_eval:
            ef = elegir_efemeride(recs, t)
            if abs(t - ef["Toe"]) > 3600:          # solo dentro del arco de validez
                continue
            xb = kepler_a_ecef(ef, t)
            dt = 1.0
            vb = (kepler_a_ecef(ef, t + dt) - kepler_a_ecef(ef, t - dt)) / (2 * dt)
            ts_sp3, xyz_sp3 = sp3[s]
            xp = lagrange(ts_sp3, xyz_sp3, t) * 1000.0
            difs.append(rtn(xb - xp, xb, vb))
    difs = np.array(difs)
    if difs.ndim != 2 or len(difs) == 0:
        return np.array([np.nan]*3), np.nan, 0
    rms = np.sqrt((difs**2).mean(axis=0))          # [R, A, C]
    sisre3d = np.sqrt((np.sum(difs**2, axis=1)).mean())
    return rms, sisre3d, len(difs)


def main() -> int:
    for f in (NAV, SP3):
        if not (RAIZ / f).exists():
            print(f"Falta {f} (clase 0.4).")
            return 1
    warnings.filterwarnings("ignore")
    print("cargando nav (G y E) y SP3 (georinex, ~1-2 min)...")
    sp3 = leer_sp3_multi(str(RAIZ / SP3))
    out = {}
    for sis, nombre in (("E", "Galileo"), ("G", "GPS")):
        ds = gr.load(str(RAIZ / NAV), use=sis)
        efs = registros(ds, sis)
        rms, sisre, n = evaluar(sis, efs, sp3)
        out[nombre] = {"R": rms[0], "A": rms[1], "C": rms[2], "3D": sisre, "n": n}
        print(f"\n[{nombre}] muestras {n}")
        print(f"  RMS radial   {rms[0]:.2f} m")
        print(f"  RMS along    {rms[1]:.2f} m")
        print(f"  RMS cross    {rms[2]:.2f} m")
        print(f"  dif 3D total {sisre:.2f} m")

    print("\n[resumen] la radial es la que más pesa en el rango al usuario; "
          "Galileo suele quedar entre las mejores.")
    dest = RAIZ / "clases/mod4-orbitas/clase4.2-pod/data"
    dest.mkdir(parents=True, exist_ok=True)
    json.dump(out, open(dest / "resultados_4_2.json", "w"), indent=1)

    assert out["Galileo"]["n"] > 100 and out["GPS"]["n"] > 100
    assert out["Galileo"]["3D"] < 5 and out["GPS"]["3D"] < 5, "dif órbita fuera de rango"
    print("\nOK: broadcast vs SP3 con RTN por constelación")
    return 0


if __name__ == "__main__":
    sys.exit(main())
