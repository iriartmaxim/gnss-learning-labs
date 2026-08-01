# %% [markdown]
# # Clase 5.1 — Lab: RAIM por residuos (ESQUELETO)
#
# Correr desde la raíz del repo (requiere data/raw/2026/166):
#
#     python3 clases/mod5-integridad/clase5.1-raim/lab/lab_raim_TODO.py

# %%
import sys
import warnings
from pathlib import Path

import numpy as np
from scipy.stats import chi2

warnings.filterwarnings("ignore")
RAIZ = Path(__file__).resolve().parents[3].parent
sys.path.insert(0, str(RAIZ / "clases/mod1-posicionamiento/clase1.5-pvt/lab/soluciones"))
sys.path.insert(0, str(RAIZ / "clases/mod5-integridad/clase5.1-raim/lab/soluciones"))
import georinex as gr
from lab_pvt_solucion import NAV, OBS, POS_OFICIAL, a_sow, gauss_newton_pvt, registros_fnav
from lab_raim_solucion import epoca_sats

SIGMA, PFA = 1.0, 1e-3

# %% [markdown]
# ## TODO 1 — el estadístico de residuos
#
# LSQ con `gauss_newton_pvt`, residuos r = P − (d + cδt), T = rᵀr/σ².

# %%
def estadistico(sats, bias_en=None, bias=0.0):
    xyz = np.array([s[1] for s in sats])
    pr = np.array([s[2] for s in sats], float)
    if bias_en is not None:
        pr[bias_en] += bias
    # TODO 1: resolvé el LSQ, calculá r y T; devolvé (T, err3d, n)
    ...
    return T, err3d, len(sats)


print("cargando datos (georinex)...")
EFS = registros_fnav(gr.load(str(RAIZ / NAV), use="E"))
obs = gr.load(str(RAIZ / OBS), use="E", tlim=("2026-06-15T12:00", "2026-06-15T13:00"))
s0 = epoca_sats(obs.isel(time=0), a_sow(obs.time.values[0]), EFS, POS_OFICIAL)
T0, e0, n0 = estadistico(s0)
print(f"época 12:00: T={T0:.1f} err={e0:.2f} m ({n0} sats)")
assert abs(T0 - 8.4) < 0.5 and n0 == 8
print("TODO 1 OK")

# %% [markdown]
# ## TODO 2 — umbral y barrido de las 121 épocas

# %%
# TODO 2: calculá dof (mediana de sats − 4), el umbral chi2 y cuántas
# épocas superan el umbral
...
print(f"dof={dof} umbral={umbral:.1f} disparan={fa}/121")
assert abs(umbral - 16.3) < 0.1 and fa <= 6
print("TODO 2 OK")

# %% [markdown]
# ## TODO 3 — inyectar fallos de 20/50/100 m

# %%
for b in (20, 50, 100):
    # TODO 3: T y error con bias b en el primer satélite; imprimí y decidí
    ...
print("TODO 3 OK")

# %% [markdown]
# ## TODO 4 — la zona ciega: el bias mínimo que dispara

# %%
# TODO 4: barré b = 2..40 y encontrá el primero con T > umbral
...
print(f"bias mínimo detectable: {b_min:.0f} m")
assert 2 <= b_min <= 12
print("LISTO: RAIM construido y calibrado sobre datos reales")
