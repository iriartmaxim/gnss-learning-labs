#!/usr/bin/env python3
"""Solución 4.1 — propagador kepleriano vs realidad.

La efeméride broadcast NO es una elipse de dos cuerpos: es un kepleriano
con parches. El ICD agrega correcciones que absorben las perturbaciones
reales (achatamiento terrestre, atracción luni-solar, presión de
radiación) sobre el arco de validez (~2-4 h en Galileo). Acá:

  A. Propagamos la MISMA efeméride con y sin cada grupo de correcciones
     y medimos cuánto vale cada una (residuo posicional en el arco).
  B. Comparamos el kepleriano puro contra la SIGUIENTE efeméride del
     mismo satélite: el salto en el empalme es lo que el operador de
     tierra tuvo que re-ajustar — la huella de las perturbaciones.

No hace falta descargar nada nuevo (usa la BRDC del día 166).
Exporta data/resultados_4_1.json.
"""
import json
import sys
import warnings
from pathlib import Path

import numpy as np

warnings.filterwarnings("ignore")
RAIZ = Path(__file__).resolve().parents[4].parent
sys.path.insert(0, str(RAIZ / "clases/mod1-posicionamiento/clase1.5-pvt/lab/soluciones"))
import lab_pvt_solucion as pvt
from lab_pvt_solucion import MU, NAV, OMEGA_E, a_sow, wrap_tk

BASE41 = Path("clases/mod4-orbitas/clase4.1-kepler")


def propagar(ef, t_sow, armonicos=True, idot=True, deltan=True):
    """Posición ECEF [m] del ICD, con flags para apagar correcciones.

    La base kepleriana (anomalía + rotación del nodo) queda SIEMPRE: sin
    la rotación del nodo el resultado no está en un marco Tierra-fija.
    Los flags apagan las tres familias de parches del mensaje:
      - armonicos: Cus/Cuc, Crs/Crc, Cis/Cic (período corto, sobre todo J2)
      - idot: deriva de la inclinación (sobre todo luni-solar)
      - deltan: corrección al movimiento medio (fase a lo largo de la órbita)
    """
    A = ef["sqrtA"] ** 2
    e = ef["Eccentricity"]
    tk = wrap_tk(t_sow - ef["Toe"])
    n = np.sqrt(MU / A**3) + (ef["DeltaN"] if deltan else 0.0)
    M = ef["M0"] + n * tk
    E = M
    for _ in range(40):
        dE = (M - (E - e * np.sin(E))) / (1 - e * np.cos(E))
        E += dE
        if abs(dE) < 1e-13:
            break
    nu = 2 * np.arctan2(np.sqrt(1 + e) * np.sin(E / 2),
                        np.sqrt(1 - e) * np.cos(E / 2))
    phi = nu + ef["omega"]
    s2, c2 = np.sin(2 * phi), np.cos(2 * phi)
    if armonicos:
        u = phi + ef["Cus"] * s2 + ef["Cuc"] * c2
        r = A * (1 - e * np.cos(E)) + ef["Crs"] * s2 + ef["Crc"] * c2
        i = ef["Io"] + ef["Cis"] * s2 + ef["Cic"] * c2
    else:
        u, r, i = phi, A * (1 - e * np.cos(E)), ef["Io"]
    if idot:
        i = i + ef["IDOT"] * tk
    Om = ef["Omega0"] + (ef["OmegaDot"] - OMEGA_E) * tk - OMEGA_E * ef["Toe"]
    xp, yp = r * np.cos(u), r * np.sin(u)
    return np.array([xp * np.cos(Om) - yp * np.cos(i) * np.sin(Om),
                     xp * np.sin(Om) + yp * np.cos(i) * np.cos(Om),
                     yp * np.sin(i)])


def main():
    import georinex as gr
    print("=== Parte A: cuánto vale cada corrección del ICD ===")
    print("  cargando BRDC día 166 (Galileo)...")
    ds = gr.load(str(RAIZ / NAV), use="E")
    efs = pvt.registros_fnav(ds)

    # un satélite con varias efemérides en el día
    sv = max(efs, key=lambda s: len(efs[s]))
    lista = sorted(efs[sv], key=lambda e: e["Toe"])
    ef = lista[len(lista) // 2]                 # una del medio del día
    print(f"  satélite {sv}: {len(lista)} efemérides; uso Toe={ef['Toe']:.0f}")
    print(f"  a = {ef['sqrtA']**2/1000:.1f} km, e = {ef['Eccentricity']:.2e}, "
          f"i = {np.degrees(ef['Io']):.1f}°")

    tks = np.arange(-7200, 7201, 300.0)
    full = {tk: propagar(ef, ef["Toe"] + tk) for tk in tks}
    casos = {
        "sin_armonicos": dict(armonicos=False),
        "sin_idot":      dict(idot=False),
        "sin_deltan":    dict(deltan=False),
        "solo_2cuerpos": dict(armonicos=False, idot=False, deltan=False),
    }
    parteA = {}
    etiq = {"sin_armonicos": "armónicos (Cxx, sobre todo J2)",
            "sin_idot": "deriva de inclinación (luni-solar)",
            "sin_deltan": "corrección al movimiento medio (Δn)",
            "solo_2cuerpos": "TODAS juntas (elipse pura)"}
    for k, kw in casos.items():
        d = np.array([np.linalg.norm(propagar(ef, ef["Toe"] + tk, **kw)
                                     - full[tk]) for tk in tks])
        parteA[k] = {"max_m": float(d.max()), "en_toe_m": float(d[len(d)//2]),
                     "borde_m": float(d[-1])}
        print(f"  {etiq[k]:40s}: max {d.max():7.1f} m | "
              f"en Toe {d[len(d)//2]:6.1f} m | a +2h {d[-1]:7.1f} m")
    print("  cada corrección tiene su firma: Δn crece con el arco (fase),")
    print("  los armónicos ya pesan en Toe (J2 es permanente), IDOT es lento.")

    print("\n=== Parte B: el salto en el empalme entre efemérides ===")
    saltos = []
    for a, b in zip(lista, lista[1:]):
        dt = b["Toe"] - a["Toe"]
        if not (1800 <= dt <= 3 * 3600):        # empalmes contiguos
            continue
        tmid = (a["Toe"] + b["Toe"]) / 2
        pa = propagar(a, tmid)                  # extrapolar la vieja
        pb = propagar(b, tmid)                  # interpolar la nueva
        saltos.append(float(np.linalg.norm(pa - pb)))
    saltos = np.array(saltos)
    print(f"  {len(saltos)} empalmes de {sv}: salto medio "
          f"{saltos.mean():.2f} m (máx {saltos.max():.2f} m)")
    print("  ese salto es lo que el segmento de control RE-AJUSTÓ entre")
    print("  cargas: la parte de las perturbaciones que un solo juego de")
    print("  parámetros no alcanza a seguir en todo el arco de validez.")

    # el kepleriano puro extrapolado lejos: cómo diverge
    print("\n=== Parte C: kepleriano puro extrapolado 12 h ===")
    largo = np.arange(0, 12 * 3600 + 1, 600.0)
    dpuro = np.array([np.linalg.norm(
        propagar(ef, ef["Toe"] + s, armonicos=False, idot=False, deltan=False)
        - propagar(ef, ef["Toe"] + s)) for s in largo])
    print(f"  a 2 h: {np.interp(7200, largo, dpuro):6.0f} m | "
          f"6 h: {np.interp(6*3600, largo, dpuro):7.0f} m | "
          f"12 h: {dpuro[-1]:8.0f} m")
    print("  por eso la efeméride broadcast se re-emite cada ~3 h y NO se")
    print("  extrapola: la elipse pura acumula km en medio día.")

    assert parteA["solo_2cuerpos"]["max_m"] > 100
    assert parteA["sin_deltan"]["borde_m"] > parteA["sin_deltan"]["en_toe_m"]
    assert saltos.mean() < 10     # empalmes operativos: métrico, no km
    assert dpuro[-1] > 1000       # 12 h de elipse pura: km

    out = {"sv": sv, "n_efem": len(lista), "toe_usada": ef["Toe"],
           "a_km": ef["sqrtA"]**2 / 1000, "e": ef["Eccentricity"],
           "inc_deg": float(np.degrees(ef["Io"])),
           "parte_a": parteA,
           "tks_min": [t / 60 for t in tks],
           "series": {k: [float(np.linalg.norm(propagar(ef, ef["Toe"]+tk, **kw)
                                               - full[tk])) for tk in tks]
                      for k, kw in casos.items()},
           "empalme_medio_m": float(saltos.mean()),
           "empalme_max_m": float(saltos.max()),
           "n_empalmes": len(saltos),
           "extrap_h": [s / 3600 for s in largo],
           "extrap_puro_m": [float(x) for x in dpuro]}
    dest = RAIZ / BASE41 / "data" / "resultados_4_1.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, separators=(",", ":")))
    print(f"\nexportado -> {dest.name}")
    print("OK: la broadcast es un kepleriano parcheado; medimos cada parche")


if __name__ == "__main__":
    main()
