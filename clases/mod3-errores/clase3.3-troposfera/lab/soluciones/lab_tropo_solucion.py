#!/usr/bin/env python3
"""Solución 3.3 — troposfera: Saastamoinen y el error que no se puede restar.

La tropo no es dispersiva: la doble frecuencia no la toca y hay que
MODELARLA. Implementa Saastamoinen completo (ZHD hidrostático + ZWD
húmedo) con mapeo 1/sin(el), lo compara contra el modelo mínimo de la
1.5, y corre el PVT iono-free con tres troposferas — ninguna, mínima,
Saastamoinen — inyectando el modelo en el motor de la 1.5.

Correr desde la raíz del repo (georinex tarda ~2-3 min).
Exporta data/resultados_3_3.json.
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
sys.path.insert(0, str(RAIZ / "clases/mod3-errores/clase3.2-ionofree/lab/soluciones"))
import lab_pvt_solucion as pvt
from lab_pvt_solucion import NAV, OBS, POS_OFICIAL, a_sow, ecef_a_geodetica
from lab_klobuchar_solucion import leer_iono_header
from lab_ionofree_solucion import enu, registros_bgd, resolver_flex

BASE33 = Path("clases/mod3-errores/clase3.3-troposfera")

# meteo de invierno para La Plata (sin sensores: ISA + climatologia)
T_K, RH = 283.15, 0.70          # 10 C, 70% de humedad relativa


def presion_isa(h_m):
    """Presión ISA [hPa] a la altura h [m]."""
    return 1013.25 * (1 - 2.2557e-5 * h_m) ** 5.2568


def es_agua(T_K):
    """Presión de vapor de saturación [hPa] (fórmula de Magnus)."""
    Tc = T_K - 273.15
    return 6.11 * np.exp(17.27 * Tc / (237.3 + Tc))


def saastamoinen_zhd(P_hPa, lat_deg, h_m):
    """Retardo cenital hidrostático [m]: 0.0022768·P / f(lat, h).

    Sale del equilibrio hidrostático: la columna de aire seco integrada
    ES la presión en superficie / g. Con P medida, exacto a ~1 mm.
    """
    den = 1 - 0.00266 * np.cos(2 * np.radians(lat_deg)) - 0.00028e-3 * h_m
    return 0.0022768 * P_hPa / den


def saastamoinen_zwd(T_K, e_hPa):
    """Retardo cenital húmedo [m]: el vapor NO está en equilibrio
    hidrostático — esta parte es la difícil (~1-4 cm de error)."""
    return 0.002277 * (1255.0 / T_K + 0.05) * e_hPa


def mapeo_simple(el_rad):
    """1/sin(el): plano-paralelo. Bien hasta ~10-15 grados de elevación."""
    return 1.0 / np.sin(el_rad)


def tropo_saastamoinen(el_rad, h):
    """Retardo oblicuo [m] — misma firma que pvt.tropo (para inyectar)."""
    P = presion_isa(h)
    e = RH * es_agua(T_K)
    lat = np.degrees(np.arctan2(POS_OFICIAL[2],
                                np.hypot(POS_OFICIAL[0], POS_OFICIAL[1])))
    return (saastamoinen_zhd(P, lat, h) + saastamoinen_zwd(T_K, e)) \
        * mapeo_simple(el_rad)


def main():
    import georinex as gr
    lat, lon, h = ecef_a_geodetica(POS_OFICIAL)
    lat_d = np.degrees(lat)
    P = presion_isa(h)
    e = RH * es_agua(T_K)
    zhd = saastamoinen_zhd(P, lat_d, h)
    zwd = saastamoinen_zwd(T_K, e)

    print("=== Parte A: Saastamoinen en LPGS (invierno, ISA) ===")
    print(f"  h elipsoidal = {h:.1f} m -> P = {P:.1f} hPa | "
          f"T = {T_K-273.15:.0f} C, RH = {RH:.0%} -> e = {e:.2f} hPa")
    print(f"  ZHD = {zhd:.4f} m ({zhd/(zhd+zwd):.0%}) | ZWD = {zwd:.4f} m "
          f"| cenital total = {zhd+zwd:.4f} m")
    print(f"  sensibilidad: {0.0022768*1000:.2f} mm por hPa de presión")
    assert 2.25 < zhd < 2.35 and 0.04 < zwd < 0.20

    minimo = 2.3 * np.exp(-h / 7160.0)
    print(f"\n=== Parte B: mapeo y comparación con el mínimo de la 1.5 ===")
    print(f"  cenital: Saastamoinen {zhd+zwd:.3f} m vs mínimo {minimo:.3f} m "
          f"(dif {zhd+zwd-minimo:+.3f} m — el ZWD que el mínimo no tiene)")
    tabla = []
    for el in (90, 30, 15, 10, 5):
        m = float(mapeo_simple(np.radians(el)))
        tabla.append({"elev": el, "mapeo": round(m, 2),
                      "saas_m": round((zhd + zwd) * m, 2),
                      "min_m": round(minimo * m, 2)})
        print(f"  elev {el:2d}: 1/sin = {m:5.2f} -> "
              f"Saastamoinen {(zhd+zwd)*m:6.2f} m | mínimo {minimo*m:6.2f} m")
    print("  (la iono a 5 grados amplificaba x3.03; la tropo x11.47 —")
    print("   la capa está pegada al suelo: el rayo rasante la come entera)")
    assert abs(tabla[-1]["mapeo"] - 11.47) < 0.05

    print("\n=== Parte C: PVT iono-free con tres troposferas ===")
    co = leer_iono_header(RAIZ / NAV)
    ab = (co["GPSA"], co["GPSB"])
    print("  cargando nav + obs (georinex, paciencia)...")
    ds = gr.load(str(RAIZ / NAV), use="E")
    efs, bgd = pvt.registros_fnav(ds), registros_bgd(ds)
    obs = gr.load(str(RAIZ / OBS), use="E",
                  tlim=("2026-06-15T12:00", "2026-06-15T13:00"))

    tropo_original = pvt.tropo
    sabores = {
        "sin":  ("sin troposfera", lambda el, hh: 0.0),
        "min":  ("mínimo 1.5 (2.3·exp/sin)", tropo_original),
        "saas": ("Saastamoinen ZHD+ZWD", tropo_saastamoinen),
    }
    rms, res_rms = {}, {}
    for k, (nombre, f) in sabores.items():
        pvt.tropo = f                       # inyectar el modelo en el motor
        errs, rr = [], []
        for i in range(0, len(obs.time), 2):
            epi, ti = obs.isel(time=i), a_sow(obs.time.values[i])
            try:
                fx, us, res = resolver_flex(epi, ti, efs, bgd, ab, "if")
                errs.append(enu(fx[:3]))
                rr.append(float(np.sqrt(np.mean(res**2))))
            except Exception:
                pass
        E = np.array(errs)
        rms[k] = np.sqrt(np.mean(E**2, axis=0)).tolist()
        res_rms[k] = float(np.mean(rr))
        r = rms[k]
        print(f"  {nombre:26s}: RMS E={r[0]:.2f} N={r[1]:.2f} U={r[2]:.2f} m"
              f" | 3D={np.linalg.norm(r):.2f} m | residuos {res_rms[k]:.2f} m")
    pvt.tropo = tropo_original              # restaurar

    uS, uM, uZ = rms["sin"][2], rms["min"][2], rms["saas"][2]
    print(f"\n  vertical: {uS:.2f} -> {uM:.2f} -> {uZ:.2f} m "
          f"(sin -> mínimo -> Saastamoinen)")
    assert uS / uM > 3, "sin tropo la vertical debe explotar"
    assert abs(uZ - uM) < 0.4, "Saastamoinen afina cm sobre el mínimo"
    print("  LECCIÓN: la tropo es GRANDE (sin modelo, la vertical explota)")
    print("  pero MANSA (una línea captura ~95%; Saastamoinen afina cm).")
    print("  La iono era igual de grande pero salvaje: Klobuchar dejaba 50%.")
    print("  Grande+predecible se modela; grande+salvaje se mide (3.2).")

    out = {"h_m": float(h), "P_hPa": float(P), "T_K": T_K, "RH": RH,
           "e_hPa": float(e), "zhd_m": float(zhd), "zwd_m": float(zwd),
           "minimo_15_m": float(minimo), "tabla_mapeo": tabla,
           "rms_enu": rms, "res_rms": res_rms,
           "epoca": "2026-06-15T12:00-13:00"}
    dest = RAIZ / BASE33 / "data" / "resultados_3_3.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=1))
    print(f"\nexportado -> {dest.name}")
    print("OK: Saastamoinen validado e inyectado en el PVT")


if __name__ == "__main__":
    main()
