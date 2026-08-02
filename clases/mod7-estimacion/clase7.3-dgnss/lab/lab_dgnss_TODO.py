# %% [markdown]
# # Lab 7.3 — DGNSS: la base corrige al rover (ESQUELETO)
#
# LPGS (base, coords conocidas) genera correcciones de pseudodistancia
# (PRC) por satélite; CORD (rover) las aplica. Baseline ~715 km: verás
# cancelar el reloj/órbita (común) y decorrelacionar iono/tropo. E1
# monofrecuencia (donde el diferencial rinde). Completá los TODO.
#
#     python3 clases/mod7-estimacion/clase7.3-dgnss/lab/lab_dgnss_TODO.py

# %%
import sys, warnings
from pathlib import Path
import numpy as np
RAIZ = Path(__file__).resolve().parents[4].parent
sys.path.insert(0, str(RAIZ / "clases/mod1-posicionamiento/clase1.5-pvt/lab/soluciones"))
import georinex as gr
from lab_pvt_solucion import (NAV, POS_OFICIAL, a_sow, registros_fnav,
                              elegir_efemeride, pseudorango_corregido, gauss_newton_pvt)
OBS_BASE = "data/raw/2026/166/LPGS00ARG_R_20261660000_01D_30S_MO.rnx"
OBS_ROVER = "data/raw/2026/166/CORD00ARG_R_20261660000_01D_30S_MO.rnx"
POS_BASE = POS_OFICIAL
POS_ROVER = np.array([2345503.9452, -4910842.9601, -3316365.5474])

def observables(ep):
    e1 = next((c for c in ("C1X","C1C","C1B") if c in ep), None)
    if e1 is None: return {}
    out = {}
    for s in ep.sv.values:
        s = str(s)
        try: P1 = float(ep.sel(sv=s)[e1])
        except (KeyError, TypeError): continue
        if np.isfinite(P1): out[s] = P1
    return out

# %% [markdown]
# ## TODO 1 — la corrección de la base (PRC)
# Desde la base CONOCIDA, para cada satélite:
#   PRC = rango_geométrico(base→sat) − pseudodistancia_corregida_base
# Absorbe reloj de satélite, órbita y atmósfera vistos en la base.

# %%
def prc_base(obs_sv, t_rx, efs, pos_base):
    prc = {}
    for s, P1 in obs_sv.items():
        if s not in efs: continue
        ef = elegir_efemeride(efs[s], t_rx)
        xyz, Pc, el = pseudorango_corregido(ef, P1, t_rx, pos_base)
        if el is not None and el < np.radians(10): continue
        # TODO 1: prc[s] = norma(xyz - pos_base) - Pc
        ...
    return prc

# %% [markdown]
# ## TODO 2 — el rover aplica la corrección
# Igual que un PVT normal, pero si hay PRC para el satélite, sumásela a su
# pseudodistancia corregida antes de resolver.

# %%
def resolver_rover(obs_sv, t_rx, efs, pos_aprox, prc=None):
    xyz_l, pr_l = [], []
    for s, P1 in obs_sv.items():
        if s not in efs: continue
        ef = elegir_efemeride(efs[s], t_rx)
        xyz, Pc, el = pseudorango_corregido(ef, P1, t_rx, pos_aprox)
        if el is not None and el < np.radians(10): continue
        if prc is not None:
            if s not in prc: continue
            # TODO 2: Pc += prc[s]
            ...
        xyz_l.append(xyz); pr_l.append(Pc)
    if len(xyz_l) < 4: return None
    fx, _, _ = gauss_newton_pvt(np.array(xyz_l), np.array(pr_l), pos_aprox)
    return fx[:3]

# %%
warnings.filterwarnings("ignore")
efs = registros_fnav(gr.load(str(RAIZ/NAV), use="E"))
tlim = ("2026-06-15T12:00", "2026-06-15T13:00")
ob = gr.load(str(RAIZ/OBS_BASE), use="E", tlim=tlim)
orv = gr.load(str(RAIZ/OBS_ROVER), use="E", tlim=tlim)
tb = {str(t)[:19]: i for i, t in enumerate(ob.time.values)}
es, ed = [], []
for j, t in enumerate(orv.time.values):
    k = str(t)[:19]
    if k not in tb: continue
    t_rx = a_sow(t)
    prc = prc_base(observables(ob.isel(time=tb[k])), t_rx, efs, POS_BASE)
    fs = resolver_rover(observables(orv.isel(time=j)), t_rx, efs, POS_ROVER)
    fd = resolver_rover(observables(orv.isel(time=j)), t_rx, efs, POS_ROVER, prc)
    if fs is not None and np.all(np.isfinite(fs)): es.append(np.linalg.norm(fs-POS_ROVER))
    if fd is not None and np.all(np.isfinite(fd)): ed.append(np.linalg.norm(fd-POS_ROVER))
rms_s, rms_d = np.sqrt(np.mean(np.square(es))), np.sqrt(np.mean(np.square(ed)))
print(f"RMS standalone {rms_s:.2f} m | DGNSS {rms_d:.2f} m | mejora {100*(1-rms_d/rms_s):.0f}%")
assert rms_d < rms_s, "DGNSS debería mejorar"
print("LISTO: DGNSS 7.3")
