# %% [markdown]
# # Lab 6.3 — Anatomía de un spoofing en la adquisición (ESQUELETO)
#
# La firma de un ataque: un SEGUNDO pico en la CAF, más fuerte, que arrastra
# al correlador. Núcleo sintético sobre el código C/A de 2.1. Completá TODO.
#
#     python3 clases/mod6-seguridad/clase6.3-spoofing/lab/lab_spoofing_TODO.py

# %%
import sys
from pathlib import Path
import numpy as np
RAIZ = Path(__file__).resolve().parents[4].parent
sys.path.insert(0, str(RAIZ / "clases/mod2-senales/clase2.1-codigos/lab/soluciones"))
sys.path.insert(0, str(RAIZ / "clases/mod6-seguridad/clase6.3-spoofing/lab/soluciones"))
from lab_codigos_solucion import chips
from lab_spoofing_solucion import picos, CODE_LEN

# %% [markdown]
# ## TODO 1 — construir la señal spoofeada
# Señal = auténtico (delay_auth) + copia falsa MÁS FUERTE (delay_spoof) + ruido.
# Después correlacionar circularmente con la réplica local para la CAF.

# %%
def escenario(prn=1, delay_auth=100, delay_spoof=140, amp_auth=1.0, amp_spoof=1.6, ruido=0.7, seed=42):
    rng = np.random.default_rng(seed); c = chips(prn).astype(float)
    # TODO 1: señal = amp_auth*roll(c,delay_auth) + amp_spoof*roll(c,delay_spoof) + ruido
    ...
    R = np.fft.ifft(np.fft.fft(señal) * np.conj(np.fft.fft(c))).real
    return R / CODE_LEN

# %%
limpio = escenario(amp_spoof=0.0); atacado = escenario()
pa = picos(atacado, k=2); va = sorted(atacado[pa], reverse=True)
piso = np.median(np.abs(atacado))
print(f"picos atacado en chips {sorted(pa)} alturas {va[0]:.2f}/{va[1]:.2f}")
assert len(pa) == 2 and va[1] > 5*piso, "debería haber doble pico"
print("LISTO: spoofing 6.3")
