#!/usr/bin/env python3
"""Solución 6.4 — Detectores de consistencia anti-spoofing.

Sin criptografía: chequeos físicos que delatan un spoofer barato. Sobre
series sintéticas (limpia vs atacada, seed fija) implementamos 4 detectores
clásicos y medimos que disparan en el ataque y NO en datos limpios:

  1. Salto de C/N0 (el spoofer sube la potencia para "ganar" el correlador).
  2. Deriva anómala del reloj del receptor (el spoofer arrastra el tiempo).
  3. Salto de posición/velocidad no físico.
  4. Inconsistencia cruzada entre constelaciones (spoofea GPS, no Galileo).

Correr:  python3 lab_detectores_solucion.py   → "DETECTORES OK".
"""
import json
import sys
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[4].parent
N = 600                      # 10 min a 1 Hz
ATAQUE = slice(300, 600)     # el spoofing arranca a los 5 min


def escenario(spoof: bool, seed: int):
    rng = np.random.default_rng(seed)
    t = np.arange(N)
    # C/N0 nominal ~45 dB-Hz por satélite (8 sats)
    cn0 = 45 + rng.normal(0, 1.0, (N, 8))
    # deriva de reloj del receptor: rampa suave + ruido
    clk = 0.02 * t + rng.normal(0, 0.5, N)
    # posición: quieto + ruido
    pos = rng.normal(0, 2.0, (N, 3))
    # solución GPS y Galileo coinciden (misma verdad) salvo ruido
    dgps_gal = rng.normal(0, 3.0, N)
    if spoof:
        cn0[ATAQUE] += 8.0                       # el spoofer sube la potencia
        clk[ATAQUE] += 0.5 * (t[ATAQUE] - 300)   # arrastra el reloj
        pos[ATAQUE, 0] += 0.3 * (t[ATAQUE] - 300)  # deriva de posición
        dgps_gal[ATAQUE] += 40.0                  # GPS spoofeado, Galileo no
    return dict(cn0=cn0, clk=clk, pos=pos, dgps_gal=dgps_gal)


def det_cn0(cn0, k=5.0):
    """Dispara si el C/N0 medio salta > k dB sobre su línea base inicial."""
    base = cn0[:100].mean()
    m = cn0.mean(axis=1)
    return m > base + k


def det_reloj(clk, k=6.0):
    """Dispara si la 2ª diferencia del reloj (aceleración) supera k·sigma."""
    acc = np.abs(np.diff(clk, 2, prepend=clk[0], append=clk[-1]))
    sig = np.std(acc[:100]) + 1e-9
    return acc > k * sig


def det_salto(pos, k=8.0):
    """Dispara si la velocidad instantánea supera k·sigma del arranque."""
    v = np.linalg.norm(np.diff(pos, axis=0, prepend=pos[:1]), axis=1)
    sig = np.std(v[:100]) + 1e-9
    return v > k * sig


def det_cruzado(dgps_gal, umbral=15.0):
    """Dispara si GPS y Galileo discrepan más que un umbral físico (m)."""
    return np.abs(dgps_gal) > umbral


def evaluar(datos):
    d = (det_cn0(datos["cn0"]) | det_reloj(datos["clk"]) |
         det_salto(datos["pos"]) | det_cruzado(datos["dgps_gal"]))
    return d


def main() -> int:
    limpio = escenario(spoof=False, seed=1)
    atacado = escenario(spoof=True, seed=2)

    d_limpio = evaluar(limpio)
    d_atacado = evaluar(atacado)

    # falsa alarma: fracción de épocas que disparan en datos limpios
    fa = d_limpio.mean()
    # detección: fracción de épocas de ataque que disparan
    det = d_atacado[ATAQUE].mean()
    # latencia: primera época de ataque detectada
    idx = np.where(d_atacado[ATAQUE])[0]
    latencia = int(idx[0]) if len(idx) else -1

    print(f"[A] falsa alarma en datos limpios: {100*fa:.1f}%")
    print(f"[B] detección durante el ataque: {100*det:.1f}%")
    print(f"[C] latencia de detección: {latencia} s tras iniciar el spoofing")
    print("[D] qué detector disparó primero en el ataque:")
    for nombre, f in (("C/N0", det_cn0), ("reloj", det_reloj),
                      ("salto pos", det_salto), ("cruzado GPS/GAL", det_cruzado)):
        arg = (atacado["dgps_gal"] if nombre.startswith("cruz")
               else atacado["clk"] if nombre == "reloj"
               else atacado["pos"] if nombre.startswith("salto")
               else atacado["cn0"])
        disp = f(arg)[ATAQUE]
        prim = int(np.where(disp)[0][0]) if disp.any() else -1
        print(f"     {nombre:16s} primera detección: {prim} s")

    dest = RAIZ / "clases/mod6-seguridad/clase6.4-detectores/data"
    dest.mkdir(parents=True, exist_ok=True)
    json.dump({"falsa_alarma": float(fa), "deteccion": float(det),
               "latencia": latencia,
               "cn0_limpio": limpio["cn0"].mean(axis=1).tolist(),
               "cn0_atacado": atacado["cn0"].mean(axis=1).tolist(),
               "clk_atacado": atacado["clk"].tolist()},
              open(dest / "resultados_6_4.json", "w"))

    assert fa < 0.05, f"demasiada falsa alarma: {fa}"
    assert det > 0.8, f"detección insuficiente: {det}"
    print("\nDETECTORES OK: disparan en el ataque, callan en datos limpios")
    return 0


if __name__ == "__main__":
    sys.exit(main())
