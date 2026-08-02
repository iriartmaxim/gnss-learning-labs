# %% [markdown]
# # Lab 6.4 — Detectores de consistencia anti-spoofing (ESQUELETO)
#
# Cuatro chequeos físicos sobre series sintéticas (limpia vs atacada).
# Completá los TODO; deben disparar en el ataque y NO en datos limpios.
#
#     python3 clases/mod6-seguridad/clase6.4-detectores/lab/lab_detectores_TODO.py

# %%
import sys
from pathlib import Path
import numpy as np
RAIZ = Path(__file__).resolve().parents[4].parent
sys.path.insert(0, str(RAIZ / "clases/mod6-seguridad/clase6.4-detectores/lab/soluciones"))
from lab_detectores_solucion import escenario, ATAQUE

# %% [markdown]
# ## TODO 1 — detector de salto de C/N0
# El spoofer sube la potencia para ganar el correlador. Dispará si el C/N0
# medio supera su línea base inicial + k dB.

# %%
def det_cn0(cn0, k=5.0):
    base = cn0[:100].mean()
    m = cn0.mean(axis=1)
    # TODO 1: return m > base + k
    ...

# %% [markdown]
# ## TODO 2 — detector cruzado GPS/Galileo
# Un spoofer barato falsifica una constelación, no ambas coherentemente.
# Dispará si la discrepancia GPS−Galileo supera un umbral físico (m).

# %%
def det_cruzado(dgps_gal, umbral=15.0):
    # TODO 2: return np.abs(dgps_gal) > umbral
    ...

# %%
limpio = escenario(spoof=False, seed=1); atacado = escenario(spoof=True, seed=2)
d_lim = det_cn0(limpio["cn0"]) | det_cruzado(limpio["dgps_gal"])
d_ata = det_cn0(atacado["cn0"]) | det_cruzado(atacado["dgps_gal"])
fa = d_lim.mean(); det = d_ata[ATAQUE].mean()
print(f"falsa alarma {100*fa:.1f}% | detección {100*det:.1f}%")
assert fa < 0.05 and det > 0.8, "ajustá los umbrales"
print("LISTO: detectores 6.4")
