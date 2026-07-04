# %% [markdown]
# # Lab 2.3 — Tracking: seguir el satélite y leer sus bits (TODO)
#
# La 2.2 te dio el pico: dónde (código) y a qué Doppler está el satélite,
# pero con ±½ chip de error y sólo por un instante. Ahora hay que
# *engancharlo* y seguirlo en el tiempo con dos lazos realimentados —
# DLL para el código, PLL/Costas para la portadora — y con el prompt ya
# limpio, integrar 20 ms por bit y **demodular el mensaje de navegación**.
# La validación: encontrar el preámbulo LNAV `10001011`.
#
# Autocontenido: generamos una señal con navegación conocida (no hay
# captura pública con un subframe entero), la trackeamos y recuperamos
# sus bits. Correr desde la raíz del repo.

# %%
import numpy as np

FS = 4_000_000.0
FC = 1.023e6
CODE_LEN = 1023
MS = int(FS * 1e-3)          # muestras por ms (= por código)
BIT_MS = 20                  # ms por bit (50 bps)
PREAMBULO = np.array([1, 0, 0, 0, 1, 0, 1, 1])   # LNAV TLM

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
# ## Parte A — El corazón del tracking: Early / Prompt / Late
#
# En cada ms, correlamos el segmento (ya sin portadora) con tres réplicas
# del código: Early (adelantada ½ chip), Prompt (centrada) y Late
# (atrasada ½ chip). Si el Prompt está alineado, |E| ≈ |L|; si el código
# se corrió, una de las dos crece y la otra baja → eso mide el error.

# %%
def correladores(base, cod, code_phase, code_rate, d=0.5, fs=FS):
    """Devuelve (E, P, L) complejos para un ms de señal sin portadora."""
    k = np.arange(base.size)
    cph = code_phase + code_rate * k / fs
    E = None  # TODO: sum(base * cod[(cph + d) mod CODE_LEN])
    P = None  # TODO: sum(base * cod[ cph      mod CODE_LEN])
    L = None  # TODO: sum(base * cod[(cph - d) mod CODE_LEN])
    return E, P, L


# %% [markdown]
# ## Parte B — Los discriminadores
#
# Cada lazo necesita convertir los correladores en un "error":
# - **PLL Costas**: `atan(Q/I)/2π` sobre el Prompt. Insensible al signo
#   del bit (por eso Costas y no un PLL común): da la fase residual.
# - **DLL early-late normalizado**: `½·(|E|−|L|)/(|E|+|L|)`. Da el error
#   de código en chips, robusto a la amplitud.

# %%
def disc_pll(P):
    """Error de fase de portadora en ciclos (Costas)."""
    return None  # TODO: arctan(imag(P)/real(P)) / (2*pi)


def disc_dll(E, L):
    """Error de código en chips (early-late normalizado)."""
    aE, aL = abs(E), abs(L)
    return None  # TODO: 0.5*(aE - aL)/(aE + aL)


# %% [markdown]
# ## Parte C — El lazo cerrado
#
# Con los errores, un filtro de lazo actualiza los NCO: el de portadora
# (freq) y el de código (fase). El PLL es de 2º orden (sigue rampas de
# Doppler); el DLL de 1º orden alcanza. Realimentar sobre `code_phase`
# (no sobre `code_rate`) mantiene el prompt alineado y con amplitud
# estable.

# %%
def _coef(bw, T, zeta=0.7):
    wn = bw / 0.53
    return 2 * zeta * wn * T, (wn * T) ** 2


def track(iq, prn, doppler0, fs=FS, pll_bw=18.0, dll_gain=1.0, d=0.5):
    cod = ca_chips(prn).astype(float)
    n_ms = iq.size // MS
    kp_p, ki_p = _coef(pll_bw, MS / fs)
    carr_freq, carr_phase, carr_bias = doppler0, 0.0, 0.0
    code_rate, code_phase = FC, 0.0
    prompts = np.empty(n_ms, dtype=complex)
    for m in range(n_ms):
        seg = iq[m * MS:(m + 1) * MS].astype(np.complex128)
        k = np.arange(seg.size)
        base = seg * np.exp(-1j * (carr_phase + 2 * np.pi * carr_freq * k / fs))
        carr_phase = (carr_phase + 2 * np.pi * carr_freq * seg.size / fs) \
            % (2 * np.pi)
        E, P, L = correladores(base, cod, code_phase, code_rate, d, fs)
        eps = disc_pll(P)
        carr_bias += ki_p * eps
        carr_freq = doppler0 + carr_bias + kp_p * eps
        dll = disc_dll(E, L)
        code_phase = (code_phase + code_rate * seg.size / fs
                      + dll_gain * dll) % CODE_LEN
        prompts[m] = P
    return prompts


# %% [markdown]
# ## Parte D — De prompts a bits, y el preámbulo
#
# Con el PLL enganchado toda la energía cae en I. Integrás 20 ms (un bit),
# mirás el signo, y tenés el bit. Como Costas tiene ambigüedad de fase
# (no distingue 0 de 180°), buscás el preámbulo `10001011` correlacionando:
# +8 = directo, −8 = invertido (y ahí sabés que hay que dar vuelta todo).

# %%
def demod_bits(prompts):
    I = np.real(prompts)
    n_bits = I.size // BIT_MS
    acc = I[:n_bits * BIT_MS].reshape(n_bits, BIT_MS).sum(axis=1)
    return (acc < 0).astype(int), acc


def buscar_preambulo(bits):
    prei = 1 - 2 * PREAMBULO
    b = 1 - 2 * bits.astype(int)
    corr = np.array([np.dot(b[i:i + 8], prei) for i in range(len(b) - 8)])
    pos = int(np.argmax(np.abs(corr)))
    return pos, int(corr[pos])


# %% [markdown]
# ## Generador (dado) y auto-test
#
# La señal trae el preámbulo en el bit 0, con Doppler y ruido, y arranca
# con ½ chip de error de código (como la deja la adquisición de la 2.2).

# %%
def generar(prn=1, n_bits=80, doppler=1200.0, cn0_db=48.0, semilla=3,
            code_off=0.5):
    rng = np.random.default_rng(semilla)
    cod = ca_chips(prn)
    bits = np.concatenate([PREAMBULO, rng.integers(0, 2, n_bits - 8)])
    simb = 1 - 2 * bits
    n = n_bits * BIT_MS * MS
    t = np.arange(n) / FS
    fase = (np.arange(n) * FC / FS + code_off).astype(np.int64) % CODE_LEN
    chip = cod[fase].astype(float)
    dato = simb[np.arange(n) // (BIT_MS * MS)].astype(float)
    s = chip * dato * np.exp(2j * np.pi * doppler * t)
    pot = 10 ** (-cn0_db / 10) * FS / 2
    r = (rng.normal(size=n) + 1j * rng.normal(size=n)) * np.sqrt(pot)
    return (s + r).astype(np.complex64), bits


# %%
iq, bits_true = generar(doppler=1200.0, cn0_db=48.0)
prompts = track(iq, 1, 1200.0)
bits_rx, acc = demod_bits(prompts)
pos, val = buscar_preambulo(bits_rx)
inv = val < 0
rx = 1 - bits_rx if inv else bits_rx
n = min(len(rx), len(bits_true))
ber = np.mean(rx[4:n] != bits_true[4:n])
print(f"preámbulo en bit {pos} (corr {val:+d}), BER {ber*100:.1f}%")
assert pos == 0 and abs(val) == 8, "revisá los discriminadores / el lazo"
assert ber < 0.03, "el tracking no está limpio"
print("OK: enganchaste el satélite y leíste su preámbulo LNAV")
