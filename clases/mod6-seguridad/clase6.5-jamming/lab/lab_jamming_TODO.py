# %% [markdown]
# # Lab 6.5 — Jamming: espectrograma y detección por energía (ESQUELETO)
#
# IQ sintética con un jammer (chirp). Completá los TODO: detección por
# energía y estimación de C/N0. Determinista.
#
#     python3 clases/mod6-seguridad/clase6.5-jamming/lab/lab_jamming_TODO.py

# %%
import sys
from pathlib import Path
import numpy as np
RAIZ = Path(__file__).resolve().parents[4].parent
sys.path.insert(0, str(RAIZ / "clases/mod6-seguridad/clase6.5-jamming/lab/soluciones"))
from lab_jamming_solucion import generar_iq, FS, JAM

# %% [markdown]
# ## TODO 1 — detección por energía (proxy de AGC)
# Potencia media por bloque; dispara si supera base + k·sigma del inicio.

# %%
def deteccion_energia(x, nfft=256, k=6.0):
    hop = nfft
    pot = np.array([np.mean(np.abs(x[i:i+hop])**2) for i in range(0, len(x)-hop, hop)])
    base = pot[:5].mean(); sig = pot[:5].std() + 1e-9
    # TODO 1: disparo = pot > base + k*sig
    ...
    return pot, disparo

# %%
t, x, mask = generar_iq(jammer="chirp", jsr_db=30.0)
pot, disparo = deteccion_energia(x)
hop = 256; blk_t = np.arange(len(pot))*hop/FS
en_jam = (blk_t >= JAM[0]) & (blk_t <= JAM[1])
det = disparo[en_jam].mean(); fa = disparo[~en_jam].mean()
subida = 10*np.log10(pot[en_jam].mean()/pot[~en_jam].mean())
print(f"subida {subida:.1f} dB | detección {100*det:.0f}% | falsa alarma {100*fa:.0f}%")
assert det > 0.8 and fa < 0.1 and subida > 10
print("LISTO: jamming 6.5")
