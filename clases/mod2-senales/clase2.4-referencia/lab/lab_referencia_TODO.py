# %% [markdown]
# # Lab 2.4 — Receptor de referencia: validá tu cadena contra gnss-sdr (TODO)
#
# Construiste un receptor completo a mano: códigos (2.1), adquisición
# (2.2), tracking + bits (2.3). ¿Cómo sabés que está bien? Comparándolo
# con un receptor de referencia, **gnss-sdr**, el software open-source
# estándar de la comunidad GNSS. Este lab cierra el módulo 2: corrés tu
# adquisición sobre las capturas reales y verificás que da lo mismo que
# gnss-sdr, y si lo tenés instalado, lo corrés de verdad.
#
# Correr desde la raíz del repo (con data/raw/iq/ ya bajado por fetch_iq).

# %%
import shutil
from pathlib import Path

import numpy as np

FS = 4_000_000.0
FC = 1.023e6
CODE_LEN = 1023
IQ = Path("data/raw/iq")

# La "verdad" de gnss-sdr para estas capturas (de sus unit tests):
VERDAD = {
    "GPS_L1_CA_ID_1_Fs_4Msps_2ms.dat": {"prn": 1, "delay": 524, "dop": 1680},
    "Galileo_E1_ID_1_Fs_4Msps_8ms.dat": {"prn": 1, "delay": 2920, "dop": -632},
}

TAPS_G2 = {1: (2, 6), 2: (3, 7), 3: (4, 8), 5: (1, 9), 6: (2, 10)}


def ca_chips(prn):
    g1, g2 = [1] * 10, [1] * 10
    s1, s2 = TAPS_G2[prn]
    b = np.empty(CODE_LEN, dtype=np.int64)
    for i in range(CODE_LEN):
        b[i] = g1[9] ^ g2[s1 - 1] ^ g2[s2 - 1]
        g1 = [g1[2] ^ g1[9]] + g1[:9]
        g2 = [g2[1] ^ g2[2] ^ g2[5] ^ g2[7] ^ g2[8] ^ g2[9]] + g2[:9]
    return 1 - 2 * b


# %% [markdown]
# ## Parte A — Tu adquisición (traída de la 2.2)
#
# Reusá tu PCPS: réplica remuestreada a 4 Msps, FFT en fase de código ×
# grilla Doppler. Devolvé (delay, doppler, métrica).

# %%
def replica_gps(prn, fs=FS):
    c = ca_chips(prn).astype(float)
    idx = (np.arange(int(fs * 1e-3)) * FC / fs).astype(int) % CODE_LEN
    return c[idx]


def adquirir(iq, replica, fs=FS, dmax=10_000, dstep=250, no_coh=2):
    n = replica.size
    R = np.conj(np.fft.fft(replica))
    dops = np.arange(-dmax, dmax + 1, dstep)
    grid = np.zeros((dops.size, n))
    t = np.arange(n) / fs
    for k in range(no_coh):
        seg = iq[k * n:(k + 1) * n]
        if seg.size < n:
            break
        # TODO: quitar Doppler, FFT, producto con R, IFFT, |.|**2, acumular
        X = None   # seg * exp(-2j*pi * outer(dops, t))
        grid += None  # abs(ifft(fft(X,axis=1) * R, axis=1))**2
    i, j = np.unravel_index(np.argmax(grid), grid.shape)
    resto = np.delete(grid[i], j)
    return int(j), int(dops[i]), float(grid[i, j] / resto.mean())


# %% [markdown]
# ## Parte B — Comparar con la referencia
#
# Para cada captura, corré tu adquisición y calculá la diferencia contra
# la verdad de gnss-sdr. El desfase de código debería coincidir a ±1-2
# muestras y el Doppler a ±1 celda de la grilla (250 Hz).

# %%
def comparar(nombre):
    iq = np.fromfile(IQ / nombre, dtype=np.complex64)
    v = VERDAD[nombre]
    d, f, m = adquirir(iq, replica_gps(v["prn"]))  # (GPS; para Galileo, réplica E1-B de la 2.2)
    ed = abs(d - v["delay"])
    ef = abs(f - v["dop"])
    print(f"{nombre}")
    print(f"  tu cadena: delay={d}, doppler={f:+d} Hz")
    print(f"  gnss-sdr : delay={v['delay']}, doppler={v['dop']:+d} Hz")
    print(f"  Δ delay={ed}, Δ doppler={ef} Hz")
    return ed, ef


# %% [markdown]
# ## Parte C — (opcional ⭐⭐⭐) Correr gnss-sdr de verdad
#
# Si instalaste gnss-sdr (`sudo apt install gnss-sdr`), podés correrlo
# sobre la misma captura con un archivo `.conf` (ver `conf/gps_l1_acq.conf`)
# y comparar el Doppler/PRN que detecta. Como la captura son sólo 2 ms,
# hay que repetirla ~100× para darle material. La solución de referencia
# lo hace automáticamente.

# %%
def gnss_sdr_esta():
    return shutil.which("gnss-sdr") is not None


# %%
# --- auto-test: sólo GPS (para Galileo necesitás la réplica E1-B de la 2.2) ---
ed, ef = comparar("GPS_L1_CA_ID_1_Fs_4Msps_2ms.dat")
assert ed <= 2, "tu desfase de código no coincide con gnss-sdr"
assert ef <= 250, "tu Doppler no coincide con gnss-sdr"
print(f"\ngnss-sdr instalado: {gnss_sdr_esta()}")
print("OK: tu cadena concuerda con el receptor de referencia")
