#!/usr/bin/env python3
"""Solución 2.1 — códigos C/A: LFSR G1/G2, propiedades Gold y espectro.

Genera los 32 códigos C/A de GPS, valida contra los octales del IS-GPS-200,
verifica las propiedades de la familia Gold (pico 1023, tres valores) y
exporta data/resultados_2_1.json para las figuras. Correr desde la raíz.
"""
import json
from pathlib import Path

import numpy as np

# Selectores de fase de G2 por PRN (tabla 3-Ia del IS-GPS-200)
TAPS_G2 = {1: (2, 6), 2: (3, 7), 3: (4, 8), 4: (5, 9), 5: (1, 9),
           6: (2, 10), 7: (1, 8), 8: (2, 9), 9: (3, 10), 10: (2, 3),
           11: (3, 4), 12: (5, 6), 13: (6, 7), 14: (7, 8), 15: (8, 9),
           16: (9, 10), 17: (1, 4), 18: (2, 5), 19: (3, 6), 20: (4, 7),
           21: (5, 8), 22: (6, 9), 23: (1, 3), 24: (4, 6), 25: (5, 7),
           26: (6, 8), 27: (7, 9), 28: (8, 10), 29: (1, 6), 30: (2, 7),
           31: (3, 8), 32: (4, 9)}

# Primeros 10 chips en octal, para validar (tabla 3-Ia del IS-GPS-200)
OCTAL_ESPERADO = {1: 0o1440, 2: 0o1620, 3: 0o1710, 4: 0o1744, 5: 0o1133}


def ca_bits(prn: int) -> np.ndarray:
    """Código C/A del PRN dado, como 1023 bits 0/1.

    G1: 1 + x^3 + x^10 (realimenta 3 y 10)
    G2: 1 + x^2 + x^3 + x^6 + x^8 + x^9 + x^10
    Salida: G1[10] XOR (G2[s1] XOR G2[s2]) con los selectores del PRN.
    """
    g1 = [1] * 10
    g2 = [1] * 10
    s1, s2 = TAPS_G2[prn]
    bits = np.empty(1023, dtype=np.int8)
    for i in range(1023):
        bits[i] = g1[9] ^ g2[s1 - 1] ^ g2[s2 - 1]
        f1 = g1[2] ^ g1[9]
        f2 = g2[1] ^ g2[2] ^ g2[5] ^ g2[7] ^ g2[8] ^ g2[9]
        g1 = [f1] + g1[:9]
        g2 = [f2] + g2[:9]
    return bits


def chips(prn: int) -> np.ndarray:
    """Bits 0/1 -> chips ±1 (0 -> +1, 1 -> -1)."""
    return 1 - 2 * ca_bits(prn).astype(np.int64)


def corr_circular(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Correlación circular vía FFT: IFFT(FFT(a)·conj(FFT(b)))."""
    return np.real(np.fft.ifft(np.fft.fft(a) * np.conj(np.fft.fft(b))))


# --- [A] Validación contra el IS-GPS-200 ---------------------------------
print("[A] primeros 10 chips (octal) vs IS-GPS-200")
for prn, esperado in OCTAL_ESPERADO.items():
    b10 = ca_bits(prn)[:10]
    valor = int("".join(map(str, b10)), 2)
    print(f"  PRN{prn:02d}: {valor:04o} (esperado {esperado:04o})")
    assert valor == esperado, f"PRN{prn}: {valor:04o} != {esperado:04o}"

# balance de la familia (códigos Gold balanceados: 512 unos, 511 ceros)
unos = {int(ca_bits(p).sum()) for p in TAPS_G2}
print(f"  balance: unos por código = {sorted(unos)}")
assert unos == {512}, "todos los C/A elegidos son Gold balanceados"

# --- [B] Autocorrelación --------------------------------------------------
c1 = chips(1)
auto = np.round(corr_circular(c1, c1)).astype(int)
pico = int(auto[0])
lados = sorted(set(auto[1:].tolist()))
print(f"\n[B] autocorrelación PRN1: pico={pico}, laterales={lados}")
assert pico == 1023
GOLD = {-65, -1, 63}
assert set(lados) <= GOLD, "los lóbulos deben ser tres-valuados (Gold)"

# --- [C] Correlación cruzada ---------------------------------------------
c2 = chips(2)
cruz = np.round(corr_circular(c1, c2)).astype(int)
vals, cuentas = np.unique(cruz, return_counts=True)
print(f"[C] cruzada PRN1×PRN2: valores={vals.tolist()} "
      f"cuentas={cuentas.tolist()}")
assert set(vals.tolist()) <= GOLD

# todas las parejas (496): ningún valor fuera del set Gold
peor = 0
for i in range(1, 33):
    ci = chips(i)
    for j in range(i + 1, 33):
        cc = np.round(corr_circular(ci, chips(j))).astype(int)
        assert set(np.unique(cc).tolist()) <= GOLD
        peor = max(peor, int(np.abs(cc).max()))
print(f"    496 parejas verificadas: |cruzada| máxima = {peor}")
assert peor == 65

# --- [D] Números para ejercicios -----------------------------------------
aisl = 20 * np.log10(65 / 1023)
gp = 10 * np.log10(1023)
print(f"\n[D] ganancia de procesamiento = {gp:.1f} dB | "
      f"aislación peor caso = {aisl:.1f} dB")
print(f"    chip = {299792458/1.023e6:.1f} m | período = 1 ms = "
      f"{299792458*1e-3/1000:.1f} km")

# --- [E] Export para figuras ---------------------------------------------
salida = {
    "auto_prn1": auto.tolist(),
    "cruz_prn1_prn2": cruz.tolist(),
    "hist_cruzada": {str(int(v)): int(c) for v, c in zip(vals, cuentas)},
    "pico": pico,
    "peor_cruzada": peor,
    "bits_prn1": "".join(map(str, ca_bits(1).tolist())),
    "octales": {str(p): f"{int(''.join(map(str, ca_bits(p)[:10])), 2):04o}"
                for p in TAPS_G2},
}
dest = Path(__file__).resolve().parents[2] / "data" / "resultados_2_1.json"
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps(salida))
print(f"\nexportado -> {dest.relative_to(dest.parents[3])}")
print("OK: todos los asserts pasaron")
