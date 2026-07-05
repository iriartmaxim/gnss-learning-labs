#!/usr/bin/env python3
"""Solución 3.2 — la combinación iono-free con observables reales.

Abre la caja negra de la 1.5: mide la ionosfera con la divergencia de
doble frecuencia (P5−P1), la compara contra Klobuchar (3.1), y corre el
PVT en tres sabores — E1 crudo, E1+Klobuchar, iono-free — para ver qué
compra cada defensa de la jerarquía. Reusa el motor de la 1.5 por import.

Correr desde la raíz del repo (georinex tarda ~2 min en cargar).
Exporta data/resultados_3_2.json.
"""
import json
import sys
import warnings
from pathlib import Path

import numpy as np

warnings.filterwarnings("ignore")
RAIZ = Path(__file__).resolve().parents[4].parent
sys.path.insert(0, str(RAIZ / "clases/mod1-posicionamiento/clase1.5-pvt/lab/soluciones"))
sys.path.insert(0, str(RAIZ / "clases/mod3-errores/clase3.1-ionosfera/lab/soluciones"))
from lab_pvt_solucion import (C, GAMMA, NAV, OBS, POS_OFICIAL, a_sow,
                              ecef_a_geodetica, elegir_efemeride,
                              gauss_newton_pvt, matriz_enu,
                              pseudorango_corregido, registros_fnav)
from lab_klobuchar_solucion import LAT, LON, klobuchar, leer_iono_header

BASE32 = Path("clases/mod3-errores/clase3.2-ionofree")


def registros_bgd(ds):
    """BGD(E1,E5a) [s] por satélite (registros F/NAV, DataSrc 258)."""
    out = {}
    for sv in ds.sv.values:
        base = str(sv).split("_")[0]
        sel = ds.sel(sv=sv).dropna(dim="time", how="all")
        for t in sel.time.values:
            fila = sel.sel(time=t)
            if int(fila["DataSrc"].values) == 258:
                out[base] = float(fila["BGDe5a"].values)
                break
    return out


def el_az(sat_ecef, rec_ecef):
    """(elevación, azimut) en grados del satélite visto desde rec."""
    lat, lon, _ = ecef_a_geodetica(rec_ecef)
    e, n, u = matriz_enu(lat, lon) @ (sat_ecef - rec_ecef)
    return (np.degrees(np.arctan2(u, np.hypot(e, n))),
            np.degrees(np.arctan2(e, n)) % 360)


def iono_divergencia(p1, p5, bgd):
    """Retardo iono en E1 [m] medido con la divergencia de código.

    P5 − P1 = (γ−1)·I1 + c·(γ−1)·BGD + DCB_rx  ⇒
    I1 = (P5−P1)/(γ−1) − c·BGD  (queda el DCB del receptor, común a todos)
    """
    return (p5 - p1) / (GAMMA - 1.0) - C * bgd


def resolver_flex(ep, t_rx, efs, bgd, ab, modo, cutoff_deg=10.0):
    """PVT de una época en el sabor pedido: 'if', 'e1', 'e1klo'.

    Réplica de las dos pasadas de la 1.5, pero eligiendo el observable y
    su corrección iono. Devuelve (fix, usados, residuos).
    """
    crudos = []
    for sv in ep.sv.values:
        base = str(sv)
        p1, p5 = float(ep.sel(sv=sv)["C1X"]), float(ep.sel(sv=sv)["C5X"])
        if np.isnan(p1) or np.isnan(p5) or base not in efs or base not in bgd:
            continue
        ef = elegir_efemeride(efs[base], t_rx)
        if modo == "if":
            P = (GAMMA * p1 - p5) / (GAMMA - 1.0)
            dbgd = 0.0                       # el reloj F/NAV YA es para IF
        else:
            P = p1
            dbgd = C * bgd[base]             # reloj E1 = reloj IF − BGD
        crudos.append((base, ef, P, dbgd))
    # pasada 1: sin tropo/iono, desde el centro de la Tierra
    d1 = [pseudorango_corregido(ef, P, t_rx) for _, ef, P, _ in crudos]
    fix1, _, _ = gauss_newton_pvt(np.array([d[0] for d in d1]),
                                  np.array([d[1] - c4 for d, (_, _, _, c4)
                                            in zip(d1, crudos)]))
    # pasada 2: tropo + BGD + (iono según el sabor) + cutoff
    datos, usados = [], []
    for base, ef, P, dbgd in crudos:
        xyz, Pc, el = pseudorango_corregido(ef, P, t_rx, fix1[:3])
        eld, azd = el_az(xyz, fix1[:3])
        if eld < cutoff_deg:
            continue
        Pc = Pc - dbgd
        if modo == "e1klo":
            Pc = Pc - float(klobuchar(LAT, LON, eld, azd,
                                      t_rx % 86400.0, *ab))
        datos.append((xyz, Pc))
        usados.append((base, eld, azd))
    fix2, res, _ = gauss_newton_pvt(np.array([d[0] for d in datos]),
                                    np.array([d[1] for d in datos]), fix1[:3])
    return fix2, usados, res


def enu(fix_xyz):
    lat, lon, _ = ecef_a_geodetica(POS_OFICIAL)
    return matriz_enu(lat, lon) @ (fix_xyz - POS_OFICIAL)


def main():
    import georinex as gr
    co = leer_iono_header(RAIZ / NAV)
    ab = (co["GPSA"], co["GPSB"])
    print("cargando nav (georinex, ~1-2 min)...")
    ds = gr.load(str(RAIZ / NAV), use="E")
    efs, bgd = registros_fnav(ds), registros_bgd(ds)
    print(f"SVs con F/NAV: {len(efs)} | con BGD: {len(bgd)}")
    print("cargando obs LPGS 12:00-13:00...")
    obs = gr.load(str(RAIZ / OBS), use="E",
                  tlim=("2026-06-15T12:00", "2026-06-15T13:00"))
    print(f"epocas: {len(obs.time)}")

    # --- Parte A: medir la iono en la epoca 12:00 y comparar vs Klobuchar
    ep, t_rx = obs.isel(time=0), a_sow(obs.time.values[0])
    fix_if, usados, _ = resolver_flex(ep, t_rx, efs, bgd, ab, "if")
    print(f"\n[A] 12:00 UTC — iono MEDIDA (divergencia P5−P1 − c·BGD) vs "
          f"Klobuchar:")
    tabla, difs = [], []
    for base, eld, azd in sorted(usados, key=lambda u: u[1]):
        p1 = float(ep.sel(sv=base)["C1X"]); p5 = float(ep.sel(sv=base)["C5X"])
        med = iono_divergencia(p1, p5, bgd[base])
        klo = float(klobuchar(LAT, LON, eld, azd, t_rx % 86400.0, *ab))
        difs.append(med - klo)
        tabla.append({"sv": base, "elev": round(eld, 1), "az": round(azd, 0),
                      "iono_med_m": round(med, 2), "iono_klo_m": round(klo, 2)})
        print(f"    {base} elev {eld:5.1f} az {azd:5.1f} -> "
              f"medida {med:6.2f} m | Klobuchar {klo:5.2f} m")
    dcb_rx = float(np.median(difs))
    resid = np.array(difs) - dcb_rx
    print(f"    offset comun (DCB receptor + sesgos): {dcb_rx:+.2f} m")
    print(f"    residual vs Klobuchar (sin offset): RMS "
          f"{np.sqrt(np.mean(resid**2)):.2f} m — el ~50% que el modelo no ve")
    assert np.sqrt(np.mean(resid**2)) < 3.0

    # --- Parte B: la serie I1(t) por satelite (la iono evoluciona suave)
    print("\n[B] serie I1(t) 12:00-13:00 (cada 30 s)...")
    svs_serie = [u[0] for u in usados]
    serie_iono = {sv: [] for sv in svs_serie}
    tt = []
    for i in range(len(obs.time)):
        epi = obs.isel(time=i)
        tt.append(a_sow(obs.time.values[i]) % 86400.0)
        for sv in svs_serie:
            try:
                p1 = float(epi.sel(sv=sv)["C1X"])
                p5 = float(epi.sel(sv=sv)["C5X"])
                serie_iono[sv].append(iono_divergencia(p1, p5, bgd[sv])
                                      if not (np.isnan(p1) or np.isnan(p5))
                                      else np.nan)
            except Exception:
                serie_iono[sv].append(np.nan)
    v = np.array(serie_iono[usados[-1][0]])   # el mas alto
    print(f"    {usados[-1][0]}: media {np.nanmean(v):.2f} m, "
          f"sigma 30s {np.nanstd(np.diff(v))/np.sqrt(2):.2f} m "
          f"(ruido de la divergencia ~ sigma_P x 2.6/1.6)")

    # --- Parte C: PVT en tres sabores sobre la serie (cada 60 s)
    print("\n[C] PVT tres sabores (cada 60 s):")
    sabores = {"e1": "E1 crudo (sin iono)", "e1klo": "E1 + Klobuchar",
               "if": "iono-free E1/E5a"}
    rms, series_enu, res_rms = {}, {}, {}
    for modo in sabores:
        errs, rr = [], []
        for i in range(0, len(obs.time), 2):
            epi, ti = obs.isel(time=i), a_sow(obs.time.values[i])
            try:
                fx, us, res = resolver_flex(epi, ti, efs, bgd, ab, modo)
                errs.append(enu(fx[:3]))
                rr.append(float(np.sqrt(np.mean(res**2))))
            except Exception:
                pass
        E = np.array(errs)
        rms[modo] = np.sqrt(np.mean(E**2, axis=0)).tolist()
        series_enu[modo] = E.tolist()
        res_rms[modo] = float(np.mean(rr))
        r = rms[modo]
        print(f"    {sabores[modo]:24s}: RMS E={r[0]:.2f} N={r[1]:.2f} "
              f"U={r[2]:.2f} m | 3D={np.linalg.norm(r):.2f} m | "
              f"residuos {res_rms[modo]:.2f} m")

    uA, uB, uC = rms["e1"][2], rms["e1klo"][2], rms["if"][2]
    print(f"\n    vertical: {uA:.2f} -> {uB:.2f} -> {uC:.2f} m "
          f"(crudo -> Klobuchar -> iono-free)")
    # validacion del path: quitar la iono mejora CLARAMENTE la vertical
    assert uA / uC > 1.5, "iono-free debe mejorar claramente la vertical"
    assert uA / uB > 1.5, "Klobuchar tambien debe mejorar la vertical"
    # el precio: los residuos iono-free son mas ruidosos que E1
    k_teo = np.sqrt((GAMMA / (GAMMA - 1))**2 + (1 / (GAMMA - 1))**2)
    k_emp = res_rms["if"] / res_rms["e1"]
    print(f"    precio del iono-free: sigma x {k_teo:.2f} teorico | "
          f"x {k_emp:.2f} empirico en los residuos")
    assert 1.3 < k_emp < 2.9, "el ruido amplificado debe ser visible"
    print("    NOTA: a las ~8-9 h locales de invierno la iono es mansa y el")
    print("    modelo rinde; iono-free paga el ruido x2.6 SIEMPRE. Sesgo vs")
    print("    ruido: en tormenta o cinturon ecuatorial la cuenta se invierte.")

    out = {"tabla_12": tabla, "dcb_rx_m": dcb_rx,
           "serie_t_sod": tt, "serie_iono": {k: v for k, v in serie_iono.items()},
           "rms_enu": rms, "series_enu": series_enu, "res_rms": res_rms,
           "k_teorico": float(k_teo), "epoca": "2026-06-15T12:00-13:00"}
    dest = RAIZ / BASE32 / "data" / "resultados_3_2.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=1))
    print(f"\nexportado -> {dest.name}")
    print("OK: iono medida, comparada con Klobuchar, y PVT en tres sabores")


if __name__ == "__main__":
    main()
