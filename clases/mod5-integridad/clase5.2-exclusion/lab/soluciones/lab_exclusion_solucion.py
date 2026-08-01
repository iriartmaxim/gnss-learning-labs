#!/usr/bin/env python3
"""Lab 5.2 — Identificación y exclusión por subconjuntos (SOLUCION).

RAIM (5.1) grita; esta clase señala: resolver n subconjuntos dejando un
satélite afuera por vez — el subconjunto cuyo estadístico se DESPLOMA es
el que dejó afuera al culpable. Después: excluir, re-resolver, verificar.
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
for m in ("clases/mod1-posicionamiento/clase1.5-pvt/lab/soluciones",
          "clases/mod5-integridad/clase5.1-raim/lab/soluciones"):
    sys.path.insert(0, str(RAIZ / m))
import georinex as gr
from lab_pvt_solucion import NAV, OBS, POS_OFICIAL, a_sow, registros_fnav
from lab_raim_solucion import SIGMA, epoca_sats, estadistico


def t_subconjuntos(sats, bias_en, bias):
    """T del conjunto completo y de cada leave-one-out (con el bias puesto)."""
    T_full, err_full, n, _ = estadistico(sats, bias_en, bias)
    Ts = []
    for k in range(len(sats)):
        sub = [s for i, s in enumerate(sats) if i != k]
        b_en = None
        if bias_en is not None and bias_en != k:
            b_en = bias_en - (1 if k < bias_en else 0)
        Tk, ek, _, _ = estadistico(sub, b_en, bias if b_en is not None else 0.0)
        Ts.append((sats[k][0], Tk, ek))
    return T_full, err_full, Ts


def main():
    print("cargando datos (georinex)...")
    efs = registros_fnav(gr.load(str(RAIZ / NAV), use="E"))
    obs = gr.load(str(RAIZ / OBS), use="E",
                  tlim=("2026-06-15T12:00", "2026-06-15T13:00"))
    sats = epoca_sats(obs.isel(time=0), a_sow(obs.time.values[0]), efs, POS_OFICIAL)
    nombres = [s[0] for s in sats]
    culpable = 0                       # E07, bias de 50 m
    BIAS = 50.0

    T_full, err_full, Ts = t_subconjuntos(sats, culpable, BIAS)
    print(f"[A] {len(sats)} sats, bias {BIAS:.0f} m en {nombres[culpable]}:")
    print(f"    conjunto completo: T = {T_full:.0f} | err 3D = {err_full:.2f} m")
    print("    sub-conjunto sin…   T        err")
    for nom, Tk, ek in Ts:
        marca = "  <- SE DESPLOMA: el culpable es este" if Tk == min(t[1] for t in Ts) else ""
        print(f"      {nom}: {Tk:10.1f} {ek:8.2f} m{marca}")
    orden = sorted(range(len(Ts)), key=lambda i: Ts[i][1])
    ident = Ts[orden[0]][0]
    separacion = Ts[orden[1]][1] / max(Ts[orden[0]][1], 1e-9)

    # exclusión y verificación
    sub = [s for i, s in enumerate(sats) if nombres[i] != ident]
    T_post, err_post, n_post, _ = estadistico(sub)
    umbral_post = float(chi2.ppf(1 - 1e-3, n_post - 4))
    print(f"[B] excluyo {ident} y re-resuelvo: T = {T_post:.1f} (umbral {umbral_post:.1f}) "
          f"| err 3D = {err_post:.2f} m -> nominal recuperado")

    # a qué bias se puede IDENTIFICAR con confianza
    b_ident = None
    for b in np.arange(2, 41, 2.0):
        _, _, Ts_b = t_subconjuntos(sats, culpable, float(b))
        o = sorted(range(len(Ts_b)), key=lambda i: Ts_b[i][1])
        if Ts_b[o[0]][0] == nombres[culpable] and Ts_b[o[1]][1] > 3 * Ts_b[o[0]][1]:
            b_ident = float(b)
            break
    print(f"[C] identificación confiable (T del 2º mínimo > 3x el mínimo) desde ~{b_ident:.0f} m")
    print("    detectar era posible desde 4 m (5.1): señalar cuesta más que gritar.")

    assert ident == nombres[culpable], f"identificó {ident}"
    assert T_post < umbral_post and err_post < 3.0
    assert separacion > 10
    assert b_ident is not None and 4 <= b_ident <= 30

    base = RAIZ / "clases/mod5-integridad/clase5.2-exclusion"
    json.dump({"nombres": nombres, "culpable": nombres[culpable], "bias": BIAS,
               "T_full": T_full, "err_full": err_full,
               "subconjuntos": [[n, T, e] for n, T, e in Ts],
               "T_post": T_post, "err_post": err_post,
               "separacion": separacion, "b_ident": b_ident},
              open(base / "data" / "resultados_5_2.json", "w"), indent=1)
    print("exportado -> resultados_5_2.json")
    print("OK: identificado, excluido y verificado")
    return 0


if __name__ == "__main__":
    sys.exit(main())
