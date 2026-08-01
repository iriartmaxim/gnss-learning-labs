# %% [markdown]
# # Clase 5.2 — Lab: identificación y exclusión (ESQUELETO)
#
#     python3 clases/mod5-integridad/clase5.2-exclusion/lab/lab_exclusion_TODO.py

# %%
import sys, warnings
from pathlib import Path
import numpy as np
from scipy.stats import chi2

warnings.filterwarnings("ignore")
RAIZ = Path(__file__).resolve().parents[3].parent
for m in ("clases/mod1-posicionamiento/clase1.5-pvt/lab/soluciones",
          "clases/mod5-integridad/clase5.1-raim/lab/soluciones"):
    sys.path.insert(0, str(RAIZ / m))
import georinex as gr
from lab_pvt_solucion import NAV, OBS, POS_OFICIAL, a_sow, registros_fnav
from lab_raim_solucion import epoca_sats, estadistico

print("cargando datos (georinex)...")
EFS = registros_fnav(gr.load(str(RAIZ / NAV), use="E"))
obs = gr.load(str(RAIZ / OBS), use="E", tlim=("2026-06-15T12:00", "2026-06-15T13:00"))
SATS = epoca_sats(obs.isel(time=0), a_sow(obs.time.values[0]), EFS, POS_OFICIAL)
NOMBRES = [s[0] for s in SATS]
BIAS, CULPABLE = 50.0, 0    # 50 m en E07

# %% [markdown]
# ## TODO 1 — los n subconjuntos leave-one-out (con el bias re-indexado)

# %%
def t_subconjuntos(sats, bias_en, bias):
    T_full, err_full, _, _ = estadistico(sats, bias_en, bias)
    Ts = []
    for k in range(len(sats)):
        # TODO 1: armá el subconjunto sin k, re-indexá bias_en si hace
        # falta, y calculá (nombre, T_k, err_k)
        ...
    return T_full, err_full, Ts


T_full, err_full, Ts = t_subconjuntos(SATS, CULPABLE, BIAS)
for nom, Tk, ek in Ts:
    print(f"  sin {nom}: T={Tk:9.1f} err={ek:6.2f}")
assert abs(T_full - 1663) < 5
print("TODO 1 OK")

# %% [markdown]
# ## TODO 2 — identificar: mínimo + separación

# %%
# TODO 2: ordená por T, identificá al culpable y calculá separación 2º/1º
...
print(f"identificado: {ident} | separación x{separacion:.0f}")
assert ident == "E07" and separacion > 10
print("TODO 2 OK")

# %% [markdown]
# ## TODO 3 — excluir, re-resolver, verificar

# %%
# TODO 3: subconjunto sin el identificado; T y err post; umbral con su dof
...
print(f"post-exclusión: T={T_post:.1f} err={err_post:.2f}")
assert T_post < 16.3 and err_post < 3.0
print("TODO 3 OK")

# %% [markdown]
# ## TODO 4 — ¿desde qué bias se puede señalar?

# %%
# TODO 4: barré b=2..40; identificación confiable = culpable correcto y
# separación > 3. Primer b que cumple:
...
print(f"identificación confiable desde ~{b_ident:.0f} m (detección era 4 m)")
assert 4 <= b_ident <= 30
print("LISTO: FDE completo — gritar, señalar, sacar y verificar")
