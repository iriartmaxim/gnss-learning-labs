# %% [markdown]
# # Lab 4.3 — Relojes broadcast vs precisos y estabilidad (ESQUELETO)
#
# Compará la corrección af0/af1/af2 con el reloj preciso CLK por satélite,
# y medí la estabilidad para distinguir PHM (máser H) de RAFS (rubidio).
# Los lectores están en la solución. Completá los TODO.
#
#     python3 clases/mod4-orbitas/clase4.3-relojes/lab/lab_relojes_TODO.py

# %%
import sys, warnings
from pathlib import Path
import numpy as np
RAIZ = Path(__file__).resolve().parents[4].parent
sys.path.insert(0, str(RAIZ / "clases/mod1-posicionamiento/clase1.3-efemerides/lab/soluciones"))
sys.path.insert(0, str(RAIZ / "clases/mod4-orbitas/clase4.3-relojes/lab/soluciones"))
import georinex as gr
from lab_efemerides_solucion import elegir_efemeride
from lab_relojes_solucion import NAV, CLK, C, registros_clock, leer_clk

# %% [markdown]
# ## TODO 1 — reloj broadcast (polinomio af0/af1/af2)
# corrección = af0 + af1·(t−toc) + af2·(t−toc)²

# %%
def clock_broadcast(recs, t):
    ef = elegir_efemeride(recs, t)
    dt = t - ef["toc"]
    # TODO 1: return ef["af0"] + ef["af1"]*dt + ef["af2"]*dt**2
    ...

# %% [markdown]
# ## TODO 2 — estabilidad (proxy de Allan a un paso)
# Con la serie de bias preciso y[k] (cada 300 s): segunda diferencia
# d2 = y[k+1]−2y[k]+y[k−1]; σ ≈ sqrt(mean(d2²)/2). Menor σ = reloj más estable.

# %%
def estabilidad(serie):
    y = np.asarray(serie)
    # TODO 2: d2 = y[2:] - 2*y[1:-1] + y[:-2] ; return sqrt(mean(d2**2)/2)
    ...

# %%
warnings.filterwarnings("ignore")
bc = registros_clock(gr.load(str(RAIZ/NAV), use="E")); clk = leer_clk(str(RAIZ/CLK))
ts = 86400 + np.arange(10*3600, 14*3600, 300.0)
rms, allan = {}, {}
for s in sorted(set(bc) & set(clk)):
    difs, serie = [], []; tsc, csc = clk[s]
    for t in ts:
        try: cb = clock_broadcast(bc[s], t)
        except Exception: continue
        cp = float(np.interp(t, tsc, csc)); difs.append((cb-cp)*C); serie.append(cp)
    if len(difs) > 10:
        rms[s] = np.sqrt(np.mean(np.square(difs))); allan[s] = estabilidad(serie)
mejor, peor = min(allan, key=allan.get), max(allan, key=allan.get)
print(f"error broadcast−preciso mediana {np.median(list(rms.values())):.2f} m")
print(f"más estable {mejor} σy={allan[mejor]:.2e} (PHM) | menos {peor} σy={allan[peor]:.2e} (RAFS)")
assert allan[peor] > allan[mejor], "debería haber dispersión de estabilidad"
print("LISTO: relojes 4.3")
