#!/usr/bin/env python3
"""Solución 3.1 — modelos ionosféricos broadcast: Klobuchar y NeQuick-G.

Parsea los coeficientes REALES del header del BRDC (día 166/2026, el mismo
de la clase 1.5), implementa Klobuchar según IS-GPS-200 §20.3.3.5.2.5, y
estima el retardo que la combinación iono-free de la 1.5 eliminó por
construcción, satélite por satélite.

Correr desde la raíz del repo. Exporta data/resultados_3_1.json.
"""
import json
import re
from pathlib import Path

import numpy as np

C = 299_792_458.0
BRDC = Path("data/raw/2026/166/BRDC00IGS_R_20261660000_01D_MN.rnx")
BASE31 = Path("clases/mod3-errores/clase3.1-ionosfera")

# LPGS (La Plata) — la estación de la 1.5
LAT, LON = -34.907, -57.932


def leer_iono_header(ruta=BRDC):
    """Extrae GPSA/GPSB (Klobuchar) y GAL (NeQuick-G) del header RINEX 3."""
    out = {}
    with open(ruta) as f:
        for linea in f:
            if "END OF HEADER" in linea:
                break
            if "IONOSPHERIC CORR" not in linea:
                continue
            clave = linea[:4].strip()
            if clave in ("GPSA", "GPSB", "GAL"):
                vals = [float(v) for v in
                        re.findall(r"[-+]?\d\.\d+E[-+]\d+", linea)]
                out[clave] = vals
    return out


def klobuchar(lat_deg, lon_deg, elev_deg, azim_deg, t_sod, alpha, beta):
    """Retardo ionosférico en L1/E1 (metros), modelo Klobuchar.

    IS-GPS-200 §20.3.3.5.2.5. Ángulos de entrada en grados, t_sod en
    segundos del día (UTC ~ GPS a estos fines). Internamente semicírculos.
    """
    phi_u = lat_deg / 180.0
    lam_u = lon_deg / 180.0
    E = np.asarray(elev_deg) / 180.0
    A = np.radians(azim_deg)

    # 1) ángulo central Tierra->IPP (cascarón a 350 km)
    psi = 0.0137 / (E + 0.11) - 0.022
    # 2) latitud del punto de perforación (clamp +-0.416)
    phi_i = np.clip(phi_u + psi * np.cos(A), -0.416, 0.416)
    # 3) longitud del IPP
    lam_i = lam_u + psi * np.sin(A) / np.cos(phi_i * np.pi)
    # 4) latitud geomagnética del IPP
    phi_m = phi_i + 0.064 * np.cos((lam_i - 1.617) * np.pi)
    # 5) hora local en el IPP
    t = (4.32e4 * lam_i + t_sod) % 86400.0
    # 6) amplitud del coseno (>=0)
    AMP = alpha[0] + phi_m * (alpha[1] + phi_m * (alpha[2] + phi_m * alpha[3]))
    AMP = np.maximum(AMP, 0.0)
    # 7) período (>=72000 s)
    PER = beta[0] + phi_m * (beta[1] + phi_m * (beta[2] + phi_m * beta[3]))
    PER = np.maximum(PER, 72000.0)
    # 8) fase: el pico está clavado a las 14:00 locales (50400 s)
    x = 2.0 * np.pi * (t - 50400.0) / PER
    # 9) factor de oblicuidad (mapea vertical -> oblicuo)
    F = 1.0 + 16.0 * (0.53 - E) ** 3
    # 10) retardo: coseno truncado de día, piso de 5 ns de noche
    noche = 5e-9
    dia = noche + AMP * (1 - x**2 / 2 + x**4 / 24)
    T = np.where(np.abs(x) < 1.57, F * dia, F * noche)
    return T * C


def oblicuidad(elev_deg):
    """Factor F de Klobuchar (adimensional)."""
    E = np.asarray(elev_deg) / 180.0
    return 1.0 + 16.0 * (0.53 - E) ** 3


def nequick_az(ai, modip_deg):
    """Nivel de ionización efectivo Az (sfu) de NeQuick-G.

    Az = ai0 + ai1*mu + ai2*mu^2 con mu = MODIP en grados. El MODIP real
    sale de la grilla de ESA; acá se pasa como argumento (aprox: la
    latitud geomagnética para una idea de orden).
    """
    mu = modip_deg
    return ai[0] + ai[1] * mu + ai[2] * mu * mu


def main():
    co = leer_iono_header()
    alpha, beta, gal = co["GPSA"], co["GPSB"], co["GAL"]
    print("=== Coeficientes broadcast del dia 166/2026 (BRDC real) ===")
    print(f"  GPSA (alpha): {alpha}")
    print(f"  GPSB (beta) : {beta}")
    print(f"  GAL (ai0-2) : {gal}")
    assert len(alpha) == 4 and len(beta) == 4 and len(gal) == 3

    print("\n=== Parte A: curva diurna en LPGS (cenit) ===")
    horas = np.arange(0, 24.01, 0.25)
    cen = np.array([klobuchar(LAT, LON, 90, 0, h * 3600, alpha, beta)
                    for h in horas])
    h_pico = horas[np.argmax(cen)]
    # hora local del pico = UTC + lon/15
    h_local_pico = (h_pico + LON / 15.0) % 24
    print(f"  piso nocturno : {cen.min():.2f} m (= 5 ns x c)")
    print(f"  pico          : {cen.max():.2f} m a las {h_pico:.2f} UTC "
          f"= {h_local_pico:.2f} hora local")
    assert abs(cen.min() - 5e-9 * C) < 0.01, "el piso debe ser 5 ns"
    assert abs(h_local_pico - 14.0) < 0.35, "el pico de Klobuchar es a las 14 locales"

    print("\n=== Parte B: factor de oblicuidad ===")
    for e in (90, 30, 15, 5):
        print(f"  elev {e:2d} deg -> F = {oblicuidad(e):.2f}")
    assert abs(oblicuidad(90) - 1.0) < 0.01
    assert 2.9 < oblicuidad(5) < 3.2

    print("\n=== Parte C: el retardo que iono-free elimino en la 1.5 ===")
    res15 = json.load(open("clases/mod1-posicionamiento/clase1.5-pvt/"
                           "data/resultados_1_5.json"))
    t15 = 12 * 3600            # epoca 2026-06-15T12:00 UTC
    detalle = []
    print(f"  epoca {res15['epoca']} (~{(12 + LON/15.0) % 24:.1f} h local)")
    for sv, elev in res15["usados"]:
        d = float(klobuchar(LAT, LON, elev, 0, t15, alpha, beta))
        detalle.append({"sv": sv, "elev": round(elev, 1), "iono_m": round(d, 2)})
        print(f"    {sv}  elev {elev:5.1f} deg -> iono ~ {d:5.2f} m")
    vals = [x["iono_m"] for x in detalle]
    print(f"  rango: {min(vals):.2f} a {max(vals):.2f} m — ese es el error que")
    print("  un receptor monofrecuencia SIN modelo comeria entero; Klobuchar")
    print("  corrige ~50% RMS; iono-free (1.5) lo elimina por construccion.")
    # a las 08 locales el modelo esta cerca del piso: sanity
    assert all(1.0 < v < 20.0 for v in vals)

    print("\n=== Parte D: NeQuick-G (Galileo) — el Az efectivo ===")
    modip_aprox = -25.0   # MODIP aprox para La Plata (grilla real: ESA)
    az = nequick_az(gal, modip_aprox)
    print(f"  ai = {gal}  con MODIP ~ {modip_aprox} deg")
    print(f"  Az efectivo = {az:.1f} sfu (nivel de ionizacion equivalente)")
    print("  (NeQuick-G usa este Az para integrar un perfil 3D de densidad")
    print("   electronica por el rayo: corrige ~70% vs ~50% de Klobuchar)")
    assert 60 < az < 200

    out = {
        "coef": co, "curva_horas_utc": horas.tolist(),
        "curva_cenital_m": np.round(cen, 3).tolist(),
        "pico_utc": float(h_pico), "pico_local": float(h_local_pico),
        "oblicuidad": {str(e): float(oblicuidad(e)) for e in (90, 30, 15, 5)},
        "iono_sats_1_5": detalle, "epoca_1_5": res15["epoca"],
        "nequick_az": {"modip_aprox": modip_aprox, "az_sfu": float(az)},
    }
    dest = BASE31 / "data" / "resultados_3_1.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=1))
    print(f"\nexportado -> {dest.name}")
    print("OK: Klobuchar implementado y validado con coeficientes reales")


if __name__ == "__main__":
    main()
