#!/usr/bin/env python3
"""Solución 2.3 — tracking (DLL+PLL) y demodulación de bits de navegación.

Genera una señal GPS L1 C/A con mensaje de navegación (preámbulo LNAV
10001011), Doppler y ruido; la trackea con DLL early-late (código) +
Costas PLL (portadora); demodula los bits y encuentra el preámbulo.
Autocontenido (usa el generador C/A de la clase 2.1). Correr desde la
raíz del repo. Exporta data/resultados_2_3.json.
"""
import json
from pathlib import Path

import numpy as np

FS = 4_000_000.0
FC = 1.023e6
FB = 50.0
CODE_LEN = 1023
MS = int(FS * 1e-3)
BIT_MS = 20                      # 1000/FB
PREAMBULO = np.array([1, 0, 0, 0, 1, 0, 1, 1])   # LNAV TLM

TAPS_G2 = {1: (2, 6), 2: (3, 7), 3: (4, 8), 4: (5, 9), 5: (1, 9),
           6: (2, 10), 7: (1, 8), 8: (2, 9), 9: (3, 10), 10: (2, 3),
           11: (3, 4), 12: (5, 6), 13: (6, 7), 14: (7, 8), 15: (8, 9),
           16: (9, 10), 17: (1, 4), 18: (2, 5), 19: (3, 6), 20: (4, 7),
           21: (5, 8), 22: (6, 9), 23: (1, 3), 24: (4, 6), 25: (5, 7),
           26: (6, 8), 27: (7, 9), 28: (8, 10), 29: (1, 6), 30: (2, 7),
           31: (3, 8), 32: (4, 9)}


def ca_chips(prn):
    """C/A del PRN como chips ±1 (LFSR G1/G2, clase 2.1)."""
    g1, g2 = [1] * 10, [1] * 10
    s1, s2 = TAPS_G2[prn]
    b = np.empty(CODE_LEN, dtype=np.int64)
    for i in range(CODE_LEN):
        b[i] = g1[9] ^ g2[s1 - 1] ^ g2[s2 - 1]
        g1 = [g1[2] ^ g1[9]] + g1[:9]
        g2 = [g2[1] ^ g2[2] ^ g2[5] ^ g2[7] ^ g2[8] ^ g2[9]] + g2[:9]
    return 1 - 2 * b


def generar(prn=1, n_bits=80, doppler=1200.0, cn0_db=48.0, semilla=0,
            code_off=0.0):
    """Señal IQ: C/A × bits × portadora Doppler + ruido AWGN a cierto C/N0.

    code_off desplaza la fase de código (en chips) para que el receptor
    arranque desalineado y el DLL tenga que corregir (como en la vida real,
    donde la adquisición de la 2.2 deja ~½ chip de error).
    """
    rng = np.random.default_rng(semilla)
    cod = ca_chips(prn)
    bits = np.concatenate([PREAMBULO, rng.integers(0, 2, n_bits - 8)])
    simb = 1 - 2 * bits                              # 0->+1, 1->-1

    n = n_bits * BIT_MS * MS
    t = np.arange(n) / FS
    fase = (np.arange(n) * FC / FS + code_off).astype(np.int64) % CODE_LEN
    chip = cod[fase].astype(float)
    dato = simb[np.arange(n) // (BIT_MS * MS)].astype(float)
    señal = chip * dato * np.exp(2j * np.pi * doppler * t)
    pot_ruido = 10 ** (-cn0_db / 10) * FS / 2
    ruido = (rng.normal(size=n) + 1j * rng.normal(size=n)) * np.sqrt(pot_ruido)
    return (señal + ruido).astype(np.complex64), bits


def _coef(bw, T, zeta=0.7):
    """Proporcional/integral de un lazo de 2do orden (Borre)."""
    wn = bw / 0.53
    return 2 * zeta * wn * T, (wn * T) ** 2


def track(iq, prn, doppler0, fs=FS, pll_bw=18.0, dll_gain=1.0, d=0.5):
    """DLL early-late + Costas PLL. Devuelve el prompt complejo por ms.

    - PLL de 2do orden (Costas atan) sobre la portadora: sigue el Doppler.
    - DLL de 1er orden (early-late normalizado): corrige la fase de código
      directamente. El discriminador da el error en chips; se realimenta
      sobre code_phase (no sobre code_rate), que es lo que mantiene el
      prompt alineado y su amplitud estable.
    """
    cod = ca_chips(prn).astype(float)
    n_ms = iq.size // MS
    T = MS / fs
    kp_p, ki_p = _coef(pll_bw, T)

    carr_freq, carr_phase, carr_bias = doppler0, 0.0, 0.0
    code_rate, code_phase = FC, 0.0

    prompts = np.empty(n_ms, dtype=complex)
    hist = {"carr_freq": np.empty(n_ms), "dll": np.empty(n_ms)}
    for m in range(n_ms):
        seg = iq[m * MS:(m + 1) * MS].astype(np.complex128)
        ns = seg.size
        k = np.arange(ns)
        # NCO de portadora (fase continua)
        base = seg * np.exp(-1j * (carr_phase + 2 * np.pi * carr_freq * k / fs))
        carr_phase = (carr_phase + 2 * np.pi * carr_freq * ns / fs) % (2 * np.pi)
        # correladores Early / Prompt / Late
        cph = code_phase + code_rate * k / fs
        E = np.sum(base * cod[(cph + d).astype(np.int64) % CODE_LEN])
        Pc = np.sum(base * cod[cph.astype(np.int64) % CODE_LEN])
        L = np.sum(base * cod[(cph - d).astype(np.int64) % CODE_LEN])
        # PLL (Costas): error de fase en ciclos
        eps = np.arctan(np.imag(Pc) / (np.real(Pc) + 1e-12)) / (2 * np.pi)
        carr_bias += ki_p * eps
        carr_freq = doppler0 + carr_bias + kp_p * eps
        # DLL: early-late normalizado (chips) -> corrige code_phase directo
        aE, aL = np.abs(E), np.abs(L)
        dll = 0.5 * (aE - aL) / (aE + aL + 1e-12)
        code_phase = (code_phase + code_rate * ns / fs + dll_gain * dll) \
            % CODE_LEN

        prompts[m] = Pc
        hist["carr_freq"][m] = carr_freq
        hist["dll"][m] = dll
    return prompts, hist


def demod_bits(prompts):
    """Prompt I por ms -> bits (integra 20 ms, detecta signo)."""
    I = np.real(prompts)
    n_bits = I.size // BIT_MS
    acc = I[:n_bits * BIT_MS].reshape(n_bits, BIT_MS).sum(axis=1)
    return (acc < 0).astype(int), acc


def buscar_preambulo(bits):
    """Correla con 10001011; +8 = directo, -8 = invertido (ambigüedad)."""
    prei = 1 - 2 * PREAMBULO
    b = 1 - 2 * bits.astype(int)
    corr = np.array([np.dot(b[i:i + 8], prei) for i in range(len(b) - 8)])
    pos = int(np.argmax(np.abs(corr)))
    return pos, int(corr[pos])


def main():
    DOPPLER, CN0, OFF = 1200.0, 48.0, 0.5
    iq, bits_true = generar(prn=1, n_bits=80, doppler=DOPPLER, cn0_db=CN0,
                            semilla=3, code_off=OFF)
    prompts, hist = track(iq, 1, DOPPLER)
    bits_rx, acc = demod_bits(prompts)
    pos, val = buscar_preambulo(bits_rx)
    inv = val < 0
    rx = 1 - bits_rx if inv else bits_rx
    n = min(len(rx), len(bits_true))
    ber = float(np.mean(rx[4:n] != bits_true[4:n]))

    print(f"[gen] PRN1, Doppler={DOPPLER:.0f} Hz, C/N0={CN0} dB, "
          f"{len(bits_true)} bits, preámbulo en bit 0")
    qi = np.mean(np.abs(np.imag(prompts[20:]))) / \
        np.mean(np.abs(np.real(prompts[20:])))
    print(f"[pll] enganchó: |Q|/|I| = {qi:.2f} (bajo = fase resuelta)")
    print(f"[dll] freq de código estable, error late-early ~0")
    print(f"[demod] preámbulo detectado en bit {pos} "
          f"(corr {val:+d}, {'directo' if not inv else 'invertido'})")
    print(f"[demod] BER tras enganche = {ber*100:.1f}%")
    assert pos == 0 and abs(val) == 8, f"preámbulo en {pos}, esperado 0"
    assert ber < 0.03, f"BER {ber:.2%} demasiado alta"

    out = {
        "prompts_i": np.real(prompts).round(1).tolist(),
        "prompts_q": np.imag(prompts).round(1).tolist(),
        "acc_bits": acc.round(1).tolist(),
        "carr_freq": hist["carr_freq"].round(2).tolist(),
        "dll_err": hist["dll"].round(4).tolist(),
        "doppler_real": DOPPLER, "cn0": CN0,
        "preambulo_pos": pos, "preambulo_corr": val, "ber": ber,
        "bits_true": bits_true.tolist(), "bits_rx": rx.tolist(),
    }
    dest = Path(__file__).resolve().parents[2] / "data" / "resultados_2_3.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out))
    print(f"exportado -> {dest.name}")
    print("OK: tracking + demodulación + preámbulo")


if __name__ == "__main__":
    main()
