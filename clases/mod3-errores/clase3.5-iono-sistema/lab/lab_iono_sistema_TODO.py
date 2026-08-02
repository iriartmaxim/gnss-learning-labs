# %% [markdown]
# # Lab 3.5 — De medir la iono a estimarla: VTEC (ESQUELETO)
#
# A partir del retardo iono medido (3.2), obtené el TEC oblicuo, proyectalo
# a vertical (VTEC) y ubicalo. Completá los TODO. Reusa la cadena de 3.2.
#
#     python3 clases/mod3-errores/clase3.5-iono-sistema/lab/lab_iono_sistema_TODO.py

# %%
import sys, warnings
from pathlib import Path
import numpy as np
RAIZ = Path(__file__).resolve().parents[4].parent
for m in ("clases/mod1-posicionamiento/clase1.5-pvt/lab/soluciones",
          "clases/mod3-errores/clase3.5-iono-sistema/lab/soluciones"):
    sys.path.insert(0, str(RAIZ / m))
import georinex as gr
from lab_pvt_solucion import (NAV, OBS, POS_OFICIAL, GAMMA, a_sow, registros_fnav,
                              elegir_efemeride, pseudorango_corregido, ecef_a_geodetica)
from lab_iono_sistema_solucion import oblicuidad, F1
RE = 6371e3; H_ION = 350e3

# %% [markdown]
# ## TODO 1 — TEC oblicuo y VTEC
# I1 = (P5−P1)/(gamma−1) [m]. STEC[TECU] = I1 / (40.3/F1²) / 1e16.
# VTEC = STEC · oblicuidad(el).

# %%
def vtec_de(P1, P5, el):
    I1 = (P5 - P1) / (GAMMA - 1)
    # TODO 1: stec = I1/(40.3/F1**2)/1e16 ; return stec*oblicuidad(el)
    ...

# %%
warnings.filterwarnings("ignore")
efs = registros_fnav(gr.load(str(RAIZ/NAV), use="E"))
obs = gr.load(str(RAIZ/OBS), use="E", tlim=("2026-06-15T12:00","2026-06-15T12:30"))
vt = []
for i in range(len(obs.time)):
    ep = obs.isel(time=i); t_rx = a_sow(obs.time.values[i])
    for s in ep.sv.values:
        s = str(s)
        if s not in efs: continue
        try: P1 = float(ep.sel(sv=s)["C1X"]); P5 = float(ep.sel(sv=s)["C5X"])
        except (KeyError, TypeError): continue
        if not (np.isfinite(P1) and np.isfinite(P5)): continue
        _, _, el = pseudorango_corregido(elegir_efemeride(efs[s], t_rx), (GAMMA*P1-P5)/(GAMMA-1), t_rx, POS_OFICIAL)
        if el is None or el < np.radians(20): continue
        v = vtec_de(P1, P5, el)
        if 0 < v < 100: vt.append(v)
print(f"VTEC mediana {np.median(vt):.1f} TECU ({len(vt)} muestras)")
assert 5 < np.median(vt) < 60
print("LISTO: iono-sistema 3.5")
