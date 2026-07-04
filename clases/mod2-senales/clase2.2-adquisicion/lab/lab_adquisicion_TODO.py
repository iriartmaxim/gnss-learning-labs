# %% [markdown]
# # Lab 2.2 — Adquisición: encontrar un satélite dentro del ruido (TODO)
#
# En la 2.1 fabricaste los códigos. Ahora los vas a *buscar* dentro de IQ
# real capturado del aire: barrer todos los desfases de código (con una
# FFT) contra una grilla de Doppler, y ver aparecer el pico. Es el
# arranque en frío de todo receptor GNSS.
#
# Datos: `python3 tools/fetch_iq.py` (3 capturas de gnss-sdr).
# Correr desde la raíz del repo.

# %%
import numpy as np
from pathlib import Path

FS = 4_000_000.0
IQ = Path("data/raw/iq")

# Réplica C/A de la clase 2.1 (traé tu generador; acá el mínimo)
TAPS_G2 = {1: (2, 6), 2: (3, 7), 3: (4, 8), 4: (5, 9), 5: (1, 9),
           10: (2, 3), 15: (8, 9), 20: (4, 7), 27: (7, 9)}  # los que uses


def ca_chips(prn: int) -> np.ndarray:
    g1, g2 = [1] * 10, [1] * 10
    s1, s2 = TAPS_G2[prn]
    bits = np.empty(1023, dtype=np.int64)
    for i in range(1023):
        bits[i] = g1[9] ^ g2[s1 - 1] ^ g2[s2 - 1]
        g1 = [g1[2] ^ g1[9]] + g1[:9]
        g2 = [g2[1] ^ g2[2] ^ g2[5] ^ g2[7] ^ g2[8] ^ g2[9]] + g2[:9]
    return 1 - 2 * bits


# %% [markdown]
# ## Parte A — La réplica muestreada
#
# El código son 1023 chips a 1.023 Mcps (1 ms). La captura está a 4 Msps,
# así que un período son 4000 muestras: hay que *remuestrear* el código a
# fs mapeando cada muestra al chip que le toca.

# %%
def replica_gps(prn: int, fs: float = FS) -> np.ndarray:
    """Un período de C/A (1 ms) a fs muestras/s."""
    c = ca_chips(prn).astype(float)
    idx = None  # TODO: (arange(muestras_por_ms) * 1.023e6 / fs).astype(int) % 1023
    return c[idx]


# %% [markdown]
# ## Parte B — PCPS (Parallel Code Phase Search)
#
# Para un Doppler fijo, la correlación en *todos* los desfases a la vez es
# una correlación circular → una FFT (¡el truco de la 2.1!). Repetimos por
# cada Doppler de la grilla y nos quedamos con el máximo del plano.

# %%
def adquirir(iq, replica, fs=FS, dmax=10_000, dstep=250):
    """Devuelve (delay_muestras, doppler_hz, metrica)."""
    n = replica.size
    R = np.conj(np.fft.fft(replica))          # réplica en frecuencia
    dops = np.arange(-dmax, dmax + 1, dstep)
    t = np.arange(n) / fs
    seg = iq[:n]
    grid = np.empty((dops.size, n))
    for i, fd in enumerate(dops):
        x = None  # TODO: sacar el Doppler -> seg * exp(-2j*pi*fd*t)
        corr = None  # TODO: ifft( fft(x) * R )  -> |.|**2
        grid[i] = np.abs(corr) ** 2
    i, j = np.unravel_index(np.argmax(grid), grid.shape)
    resto = np.delete(grid[i], j)
    return int(j), int(dops[i]), float(grid[i, j] / resto.mean())


def cargar_iq(nombre: str) -> np.ndarray:
    """gr_complex = float32 I/Q intercalado."""
    return np.fromfile(IQ / nombre, dtype=np.complex64)


# %% [markdown]
# ## Parte C — Buscar de verdad
#
# Si tu réplica y tu PCPS están bien, el pico de GPS PRN1 tiene que caer en
# delay=524, doppler≈+1680 Hz (las verdades vienen de los tests de
# gnss-sdr). El "métrica" (pico/media) separa señal de ruido.

# %%
# --- auto-test ---
iq = cargar_iq("GPS_L1_CA_ID_1_Fs_4Msps_2ms.dat")
d, f, m = adquirir(iq, replica_gps(1))
print(f"GPS PRN1: delay={d}, doppler={f:+d} Hz, métrica={m:.1f}")
print("esperado: delay=524, doppler=+1680 Hz")
assert abs(d - 524) <= 2, "revisá el remuestreo de la réplica"
assert abs(f - 1680) <= dstep, "revisá el barrido Doppler"
print("OK: adquiriste un satélite dentro del ruido")
