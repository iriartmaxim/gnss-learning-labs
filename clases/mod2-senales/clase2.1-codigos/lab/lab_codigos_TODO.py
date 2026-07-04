# %% [markdown]
# # Lab 2.1 — Generación de códigos C/A (versión TODO)
#
# Vas a construir los códigos que hacen posible que 32 satélites
# compartan la misma frecuencia: los C/A de GPS (familia Gold). Todo se
# genera acá — no hay datos que bajar. La validación es contra la tabla
# oficial del IS-GPS-200 y las propiedades matemáticas de la familia.
# Correr desde la raíz del repo.

# %%
import numpy as np

# Selectores de fase de G2 por PRN (tabla 3-Ia del IS-GPS-200)
TAPS_G2 = {1: (2, 6), 2: (3, 7), 3: (4, 8), 4: (5, 9), 5: (1, 9),
           6: (2, 10), 7: (1, 8), 8: (2, 9), 9: (3, 10), 10: (2, 3),
           11: (3, 4), 12: (5, 6), 13: (6, 7), 14: (7, 8), 15: (8, 9),
           16: (9, 10), 17: (1, 4), 18: (2, 5), 19: (3, 6), 20: (4, 7),
           21: (5, 8), 22: (6, 9), 23: (1, 3), 24: (4, 6), 25: (5, 7),
           26: (6, 8), 27: (7, 9), 28: (8, 10), 29: (1, 6), 30: (2, 7),
           31: (3, 8), 32: (4, 9)}

# %% [markdown]
# ## Parte A — Los dos LFSR
#
# `G1: 1 + x³ + x¹⁰` y `G2: 1 + x² + x³ + x⁶ + x⁸ + x⁹ + x¹⁰`, ambos de
# 10 etapas inicializadas en todos-unos. La salida C/A es
# `G1[10] XOR (G2[s1] XOR G2[s2])` con los selectores de tu PRN.
# Ojo con el índice: la etapa "1" del estándar es `g[0]` en Python.

# %%
def ca_bits(prn: int) -> np.ndarray:
    """Código C/A del PRN dado, como 1023 bits 0/1."""
    g1 = [1] * 10
    g2 = [1] * 10
    s1, s2 = TAPS_G2[prn]
    bits = np.empty(1023, dtype=np.int8)
    for i in range(1023):
        bits[i] = None  # TODO: g1[9] XOR g2[s1-1] XOR g2[s2-1]
        f1 = None  # TODO: realimentación de G1 (etapas 3 y 10)
        f2 = None  # TODO: realimentación de G2 (etapas 2,3,6,8,9,10)
        g1 = [f1] + g1[:9]
        g2 = [f2] + g2[:9]
    return bits


def chips(prn: int) -> np.ndarray:
    """Bits 0/1 -> chips ±1 (0 -> +1, 1 -> -1)."""
    return None  # TODO: una resta lo resuelve


# %% [markdown]
# ## Parte B — Correlación circular vía FFT
#
# El truco que reaparece en la adquisición (2.2): correlacionar en todos
# los desfases a la vez cuesta una FFT, no 1023 productos punto.

# %%
def corr_circular(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """IFFT( FFT(a) · conj(FFT(b)) ), parte real."""
    return None  # TODO


# %% [markdown]
# ## Parte C — Propiedades de la familia Gold
#
# Si tu LFSR está bien: pico de autocorrelación = 1023, y TODO lo demás
# (autocorrelación fuera de fase y cruzadas entre PRNs) vive en el set
# `{-65, -1, 63}`. Ni un valor afuera. Esa rigidez es la firma Gold.

# %%
# --- auto-test ---
b1 = ca_bits(1)
octal = int("".join(map(str, b1[:10].tolist())), 2)
print(f"PRN1, primeros 10 chips: {octal:04o} (IS-GPS-200: 1440)")
assert octal == 0o1440, "revisá índices de taps y estado inicial"

c1, c2 = chips(1), chips(2)
auto = np.round(corr_circular(c1, c1)).astype(int)
cruz = np.round(corr_circular(c1, c2)).astype(int)
print(f"pico = {auto[0]} | laterales = {sorted(set(auto[1:].tolist()))}")
print(f"cruzada PRN1×PRN2: {sorted(set(cruz.tolist()))}")
assert auto[0] == 1023
GOLD = {-65, -1, 63}
assert set(auto[1:].tolist()) <= GOLD and set(cruz.tolist()) <= GOLD
print("OK: sos oficialmente capaz de fabricar señal GPS (la parte pública)")
