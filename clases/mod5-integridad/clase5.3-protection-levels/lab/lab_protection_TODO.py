# %% [markdown]
# # Lab 5.3 — Protection levels y disponibilidad de integridad (ESQUELETO)
#
# Sobre las épocas reales de LPGS: geometría en ENU → HPL/VPL por RAIM
# clásico (slope × pbias) → disponibilidad contra LPV-200 (HAL=40, VAL=35).
# Reusa el motor de 1.5 y la cadena de 5.1. Completá los TODO.
#
#     python3 clases/mod5-integridad/clase5.3-protection-levels/lab/lab_protection_TODO.py

# %%
import sys, warnings
from pathlib import Path
import numpy as np
from scipy.stats import chi2, ncx2

RAIZ = Path(__file__).resolve().parents[4].parent
for m in ("clases/mod1-posicionamiento/clase1.5-pvt/lab/soluciones",
          "clases/mod5-integridad/clase5.1-raim/lab/soluciones"):
    sys.path.insert(0, str(RAIZ / m))
import georinex as gr
from lab_pvt_solucion import (NAV, OBS, POS_OFICIAL, a_sow, registros_fnav,
                              ecef_a_geodetica, matriz_enu)
from lab_raim_solucion import SIGMA, PFA, epoca_sats
HAL, VAL, PMD = 40.0, 35.0, 1e-3

# %% [markdown]
# ## TODO 1 — geometría en ENU
# Cada fila de G: el versor receptor→satélite rotado a ENU, con signo menos,
# más un 1 para el reloj. (El versor ECEF se rota con matriz_enu(lat,lon).)

# %%
def geometria_enu(sats, rec):
    lat, lon, _ = ecef_a_geodetica(rec)
    R = matriz_enu(lat, lon)
    G = []
    for _, xyz, _pc in sats:
        # TODO 1: u = versor ECEF a sat; u_enu = R @ u; fila = [-uE,-uN,-uU,1]
        ...
    return np.array(G)

# %% [markdown]
# ## TODO 2 — slopes y protection levels
# S=(GᵀG)⁻¹Gᵀ ; P=G S ; slope_H,i=‖S[:2,i]‖/√(1-Pii) ; HPL=max(slope_H)·pbias.
# pbias=√λ con λ la no-centralidad (ncx2) que da PMD al umbral chi2(PFA,dof).

# %%
def _lambda_pbias(T_umbral, dof, pmd):
    lo, hi = 0.0, 2000.0
    for _ in range(80):
        mid = 0.5*(lo+hi)
        lo, hi = (mid, hi) if ncx2.cdf(T_umbral, dof, mid) > pmd else (lo, mid)
    return 0.5*(lo+hi)

def protection_levels(G, n):
    S = np.linalg.solve(G.T @ G, G.T)
    P = G @ S
    dof = n - 4
    pbias = np.sqrt(_lambda_pbias(chi2.ppf(1-PFA, dof), dof, PMD))
    diag = np.clip(1 - np.diag(P), 1e-9, None)
    # TODO 2: slope_h, slope_v y hpl=slope_h.max()*pbias, vpl=slope_v.max()*pbias
    ...
    return hpl, vpl, pbias

# %%
warnings.filterwarnings("ignore")
efs = registros_fnav(gr.load(str(RAIZ/NAV), use="E"))
obs = gr.load(str(RAIZ/OBS), use="E", tlim=("2026-06-15T12:00","2026-06-15T13:00"))
hpls, vpls, disp, n_ep = [], [], 0, 0
for i in range(len(obs.time)):
    sats = epoca_sats(obs.isel(time=i), a_sow(obs.time.values[i]), efs, POS_OFICIAL)
    if len(sats) < 5: continue
    hpl, vpl, pbias = protection_levels(geometria_enu(sats, POS_OFICIAL), len(sats))
    hpls.append(hpl); vpls.append(vpl); n_ep += 1
    if hpl < HAL and vpl < VAL: disp += 1
disponibilidad = 100.0*disp/n_ep
print(f"épocas {n_ep} | HPL med {np.median(hpls):.2f} | VPL med {np.median(vpls):.2f} | disp {disponibilidad:.1f}%")
assert (np.array(vpls) >= np.array(hpls)).mean() > 0.5, "VPL debería superar a HPL"
assert disponibilidad == 100.0, "con LPV-200 y cielo abierto debería dar 100%"
print("LISTO: protection levels 5.3")
