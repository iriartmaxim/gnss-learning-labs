#!/usr/bin/env python3
"""Solución 6.5 — Jamming: espectrograma, detección por energía y pérdida de C/N0.

Genera IQ sintética estilo GNSS (ruido + señal débil) e inyecta un jammer
(tono CW y chirp) en una ventana temporal. Detecta por energía/AGC y mide
la degradación del C/N0 y la pérdida de tracking. Determinista (seed fija).

Correr:  python3 lab_jamming_solucion.py   → "JAMMING OK".
"""
import json
import sys
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[4].parent
FS = 4_000_000.0            # 4 Msps
DUR = 0.02                  # 20 ms
JAM = (0.008, 0.014)        # jammer entre 8 y 14 ms
CN0_NOM = 45.0             # dB-Hz nominal


def generar_iq(seed=42, jammer="chirp", jsr_db=30.0):
    rng = np.random.default_rng(seed)
    n = int(FS * DUR)
    t = np.arange(n) / FS
    # ruido térmico complejo (potencia 1)
    x = (rng.normal(0, 1, n) + 1j * rng.normal(0, 1, n)) / np.sqrt(2)
    # señal GNSS: muy por debajo del ruido (BPSK a 1.023 Mcps, aprox tono)
    sig = 0.06 * np.exp(2j * np.pi * 1.2e6 * t)
    x += sig
    mask = (t >= JAM[0]) & (t <= JAM[1])
    amp = 10 ** (jsr_db / 20.0)                     # J/S en amplitud
    if jammer == "cw":
        j = amp * np.exp(2j * np.pi * 1.30e6 * t)   # tono fijo cerca de la señal
    else:  # chirp: barre frecuencia (el jammer más común)
        f0, f1 = -1.5e6, 1.5e6
        k = (f1 - f0) / (JAM[1] - JAM[0])
        ph = 2 * np.pi * (f0 * (t - JAM[0]) + 0.5 * k * (t - JAM[0]) ** 2)
        j = amp * np.exp(1j * ph)
    x[mask] += j[mask]
    return t, x, mask


def espectrograma(x, nfft=256):
    hop = nfft
    cols = len(x) // hop
    S = np.zeros((nfft, cols))
    win = np.hanning(nfft)
    for c in range(cols):
        seg = x[c * hop:c * hop + nfft]
        if len(seg) < nfft:
            break
        S[:, c] = np.abs(np.fft.fftshift(np.fft.fft(seg * win))) ** 2
    return 10 * np.log10(S + 1e-12)


def deteccion_energia(x, nfft=256, k=6.0):
    """AGC/energía por bloque: dispara si la potencia supera k·sigma del inicio."""
    hop = nfft
    pot = np.array([np.mean(np.abs(x[i:i + hop]) ** 2)
                    for i in range(0, len(x) - hop, hop)])
    base = pot[:5].mean(); sig = pot[:5].std() + 1e-9
    disparo = pot > base + k * sig
    return pot, disparo


def cn0_estimado(x, mask, nfft=256):
    """C/N0 proxy por bloque: potencia en el BIN FIJO de la señal (1.2 MHz)
    sobre la potencia total de ruido+interferencia. El jammer sube el piso
    → el C/N0 cae (lo contrario de mirar el pico, que se engancha al jammer)."""
    hop = nfft
    bin_sig = int(round(1.2e6 / FS * nfft))          # bin de la señal GNSS
    out = []
    for i in range(0, len(x) - hop, hop):
        seg = x[i:i + hop]
        esp = np.abs(np.fft.fft(seg * np.hanning(nfft))) ** 2
        p_sig = esp[bin_sig]
        p_ruido = (esp.sum() - p_sig) / (nfft - 1)   # piso: todo menos la señal
        snr = p_sig / (p_ruido + 1e-12)
        out.append(CN0_NOM + 10 * np.log10(max(snr, 1e-3) / (esp.mean() and 1)))
    out = np.array(out)
    # normalizar a CN0_NOM fuera del jammer (calibración del proxy)
    return out - (out[:5].mean() - CN0_NOM)


def main() -> int:
    t, x, mask = generar_iq(jammer="chirp", jsr_db=30.0)
    S = espectrograma(x)
    pot, disparo = deteccion_energia(x)
    cn0 = cn0_estimado(x, mask)

    # ventana de bloques afectada por el jammer
    hop = 256
    blk_t = np.arange(len(pot)) * hop / FS
    en_jam = (blk_t >= JAM[0]) & (blk_t <= JAM[1])

    fa = disparo[~en_jam].mean()
    det = disparo[en_jam].mean()
    subida_db = 10 * np.log10(pot[en_jam].mean() / pot[~en_jam].mean())
    cn0_caida = cn0[~en_jam].mean() - cn0[en_jam].mean()

    print(f"[A] subida de potencia con jammer: {subida_db:.1f} dB")
    print(f"[B] detección por energía en la ventana: {100*det:.0f}%  "
          f"(falsa alarma {100*fa:.0f}%)")
    print(f"[C] caída de C/N0 durante el jamming: {cn0_caida:.1f} dB-Hz")
    print(f"[D] tracking: {'PERDIDO' if cn0[en_jam].mean() < 30 else 'degradado'} "
          f"(C/N0 medio {cn0[en_jam].mean():.0f} dB-Hz)")

    dest = RAIZ / "clases/mod6-seguridad/clase6.5-jamming/data"
    dest.mkdir(parents=True, exist_ok=True)
    json.dump({"subida_db": float(subida_db), "deteccion": float(det),
               "falsa_alarma": float(fa), "cn0_caida": float(cn0_caida),
               "espectrograma": S[::4, :].tolist(),
               "pot": pot.tolist(), "cn0": cn0.tolist(),
               "blk_t": blk_t.tolist(), "jam": list(JAM)},
              open(dest / "resultados_6_5.json", "w"))

    assert det > 0.8 and fa < 0.1, "detección/falsa alarma fuera de rango"
    assert subida_db > 10, "el jammer debería elevar claramente la potencia"
    print("\nJAMMING OK: detectado por energía, C/N0 y tracking degradados")
    return 0


if __name__ == "__main__":
    sys.exit(main())
