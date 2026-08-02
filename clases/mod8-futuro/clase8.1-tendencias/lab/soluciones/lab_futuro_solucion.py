#!/usr/bin/env python3
"""Solución 8.1 — LEO-PNT vs MEO: por qué la órbita baja cambia el juego.

Lab-lite cuantitativo: compara una constelación MEO (GNSS clásico, ~23 000 km)
con LEO-PNT (~550 km) en período, velocidad angular vista, Doppler y ventaja
de potencia recibida. Todo desde física orbital básica (clase 0.3). Muestra
por qué LEO es prometedor (más señal, geometría que cambia rápido) y difícil
(hand-over veloz, muchos satélites). Correr: python3 lab_futuro_solucion.py.
"""
import json
import sys
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[4].parent
MU = 3.986004418e14        # m3/s2
RE = 6371e3                # m
C = 299792458.0
F_L1 = 1575.42e6


def periodo(alt_km):
    a = RE + alt_km * 1e3
    return 2 * np.pi * np.sqrt(a**3 / MU)


def vel_orbital(alt_km):
    a = RE + alt_km * 1e3
    return np.sqrt(MU / a)


def doppler_max(alt_km):
    """Doppler máximo aproximado (satélite cruzando el cénit): f·v/c."""
    return F_L1 * vel_orbital(alt_km) / C


def ganancia_potencia_db(alt_meo, alt_leo):
    """Ventaja de potencia recibida por distancia usuario→satélite (ley
    cuadrática inversa). Al cénit, esa distancia ES la altitud."""
    return 20 * np.log10((alt_meo * 1e3) / (alt_leo * 1e3))


def main() -> int:
    MEO, LEO = 23222.0, 550.0     # km (Galileo vs LEO-PNT típico)
    out = {}
    for nombre, alt in (("MEO (Galileo)", MEO), ("LEO-PNT", LEO)):
        T = periodo(alt)
        out[nombre] = {"alt_km": alt, "periodo_h": T / 3600,
                       "vel_kms": vel_orbital(alt) / 1000,
                       "doppler_khz": doppler_max(alt) / 1000}
        print(f"[{nombre}]")
        print(f"   período orbital:   {T/3600:.2f} h")
        print(f"   velocidad:         {vel_orbital(alt)/1000:.2f} km/s")
        print(f"   Doppler máx (L1):  ±{doppler_max(alt)/1000:.1f} kHz")

    gan = ganancia_potencia_db(MEO, LEO)      # cénit vs cénit (altitud)
    out["ganancia_potencia_db"] = gan
    print(f"\n[ventaja LEO] potencia recibida (cénit vs cénit): +{gan:.0f} dB "
          f"(por estar {MEO/LEO:.0f}× más cerca del usuario)")
    print(f"   ~coincide con los ~30 dB citados para LEO-PNT; por eso es "
          f"intrínsecamente anti-jamming")
    print(f"[implicancia] más señal → mucho más difícil de jammear, "
          f"pero el Doppler y el hand-over son ~{doppler_max(LEO)/doppler_max(MEO):.0f}× peores")
    print("[trade-off] LEO: más señal y geometría que cambia rápido (bueno para "
          "convergencia PPP y anti-jamming), a costa de MUCHOS satélites y hand-over veloz")

    dest = RAIZ / "clases/mod8-futuro/clase8.1-tendencias/data"
    dest.mkdir(parents=True, exist_ok=True)
    json.dump(out, open(dest / "resultados_8_1.json", "w"), indent=1, ensure_ascii=False)

    # chequeos físicos
    assert 13 < out["MEO (Galileo)"]["periodo_h"] < 15, "período MEO ~14 h"
    assert out["LEO-PNT"]["periodo_h"] < 2, "período LEO < 2 h"
    assert gan > 25, "la ventaja de potencia LEO (cénit) debería rondar los 30 dB"
    print("\nOK: LEO-PNT cuantificado (potencia, Doppler, período)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
