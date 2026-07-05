# %% [markdown]
# # Lab 3.4 — Multipath y ruido: la combinación código−fase (TODO)
#
# El último error del módulo es el único que no viene del cielo: viene de
# TU entorno. Las reflexiones (suelo, edificios, mástiles) suman réplicas
# retrasadas que sesgan el correlador de código en decímetros; la fase,
# en cambio, queda acotada a λ/4 ≈ 5 cm. Esa asimetría permite construir
# el observable MP: código menos fases, que elimina geometría, relojes,
# tropo **e iono**, y deja multipath + ruido desnudos.
#
# Acá lo medís con LPGS: magnitudes, firma en elevación, y el σ_P que
# venís asumiendo desde la 1.5, por fin medido.
#
# Correr desde la raíz del repo (~3 min).

# %%
import sys
import warnings
from pathlib import Path

import numpy as np

warnings.filterwarnings("ignore")
RAIZ = Path.cwd()
sys.path.insert(0, str(RAIZ / "clases/mod1-posicionamiento/clase1.5-pvt/lab/soluciones"))
sys.path.insert(0, str(RAIZ / "clases/mod3-errores/clase3.2-ionofree/lab/soluciones"))
import lab_pvt_solucion as pvt
from lab_pvt_solucion import (C, GAMMA, NAV, OBS, POS_OFICIAL, a_sow,
                              elegir_efemeride, kepler_a_ecef)
from lab_ionofree_solucion import el_az

LAM1, LAM5 = C / 1575.42e6, C / 1176.45e6

# %% [markdown]
# ## Parte A — Los coeficientes
#
# Con P₁ = ρ + I, Φ₁ = ρ − I + B₁ y Φ₅ = ρ − γI + B₅ (todo en metros),
# despejá I de las dos fases y reemplazalo en P₁ − Φ₁ − 2I:
#
# $$ MP_1 = P_1 - \left(1+\tfrac{2}{\gamma-1}\right)\Phi_1
#           + \tfrac{2}{\gamma-1}\,\Phi_5 + \mathrm{cte} $$
#
# Para MP₅ el retardo es γI y sale k' = 2γ/(γ−1).

# %%
K1 = None    # TODO: 2/(GAMMA-1)      -> 2.521
K5 = None    # TODO: 2*GAMMA/(GAMMA-1) -> 4.521


def combinaciones_mp(o):
    """MP1 y MP5 [m] de un satélite. Ojo: georinex da la fase en CICLOS."""
    P1, P5 = o["C1X"].values, o["C5X"].values
    F1 = None    # TODO: o["L1X"].values * LAM1
    F5 = None    # TODO: o["L5X"].values * LAM5
    mp1 = None   # TODO: P1 - (1+K1)*F1 + K1*F5
    mp5 = None   # TODO: P5 - K5*F1 + (K5-1)*F5
    return mp1, mp5


def sub_arcos(v, salto=1.0, min_ep=10):
    """Tramos válidos [i, j) partidos por NaN y por saltos (cycle slips)."""
    arcos, n, i = [], len(v), 0
    while i < n:
        if np.isnan(v[i]):
            i += 1
            continue
        j = i
        while j + 1 < n and not np.isnan(v[j + 1]) \
                and abs(v[j + 1] - v[j]) < salto:
            j += 1
        if j - i + 1 >= min_ep:
            arcos.append((i, j + 1))
        i = j + 1
    return arcos


def detrend(v):
    """Resta la media por sub-arco: absorbe la constante (ambigüedades)."""
    out = np.full_like(v, np.nan)
    for i, j in sub_arcos(v):
        out[i:j] = v[i:j] - np.nanmean(v[i:j])
    return out


# %% [markdown]
# ## Parte B — Medir en LPGS y buscar la firma de elevación

# %%
import georinex as gr
print("cargando nav + obs (paciencia)...")
ds = gr.load(NAV, use="E")
efs = pvt.registros_fnav(ds)
obs = gr.load(OBS, use="E", tlim=("2026-06-15T12:00", "2026-06-15T12:45"))

el = np.full((len(obs.time), len(obs.sv)), np.nan)
for it, t64 in enumerate(obs.time.values):
    t = a_sow(t64)
    for isv, sv in enumerate(obs.sv.values):
        if sv in efs:
            ef = elegir_efemeride(efs[sv], t)
            el[it, isv] = el_az(kepler_a_ecef(ef, t), POS_OFICIAL)[0]

MP1 = np.full_like(el, np.nan)
MP5 = np.full_like(el, np.nan)
for isv, sv in enumerate(obs.sv.values):
    mp1, mp5 = combinaciones_mp(obs.sel(sv=sv))
    MP1[:, isv], MP5[:, isv] = detrend(mp1), detrend(mp5)

rms1 = float(np.sqrt(np.nanmean(MP1**2)))
rms5 = float(np.sqrt(np.nanmean(MP5**2)))
print(f"RMS MP1 = {rms1*100:.1f} cm | RMS MP5 = {rms5*100:.1f} cm")
bajo = (el >= 10) & (el < 30)
alto = el >= 45
r_bajo = float(np.sqrt(np.nanmean(MP1[bajo]**2)))
r_alto = float(np.sqrt(np.nanmean(MP1[alto]**2)))
print(f"MP1 con elevación <30°: {r_bajo*100:.1f} cm | >45°: {r_alto*100:.1f} cm")

# %% [markdown]
# ## Auto-test
#
# (La repetición sideral Galileo —la geometría vuelve cada 10 días— está
# en la solución: pide el día 176 vía
# `python3 tools/fetch_data.py --date 2026-06-25 --que obs`.)

# %%
assert abs(K1 - 2.521) < 0.001 and abs(K5 - 4.521) < 0.001
assert 0.05 < rms1 < 0.70 and 0.05 < rms5 < 0.70
assert r_bajo > 1.5 * r_alto, "el multipath vive cerca del horizonte"
print("OK: el multipath medido — y con él, el σ_P de todo el curso")
