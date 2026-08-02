# %% [markdown]
# # Lab 7.4 — PPP-lite: órbitas y relojes precisos + ZWD (ESQUELETO)
#
# Reemplazá la broadcast por productos precisos (SP3 órbita, CLK reloj) sobre
# observables iono-free, sumá la relatividad periódica (¡los CLK no la traen!)
# y estimá un ZWD batch. Compará contra el broadcast (~1.95 m). Completá TODO.
# La solución de referencia trae los lectores de SP3/CLK ya hechos.
#
#     python3 clases/mod7-estimacion/clase7.4-ppp/lab/lab_ppp_TODO.py

# %%
import sys, warnings
from pathlib import Path
import numpy as np
RAIZ = Path(__file__).resolve().parents[4].parent
sys.path.insert(0, str(RAIZ / "clases/mod1-posicionamiento/clase1.5-pvt/lab/soluciones"))
sys.path.insert(0, str(RAIZ / "clases/mod7-estimacion/clase7.4-ppp/lab/soluciones"))
import georinex as gr
from lab_pvt_solucion import (C, OBS, POS_OFICIAL, a_sow, ecef_a_geodetica, matriz_enu, el_y_h)
from lab_ppp_solucion import (SP3, CLK, OMEGA_E, leer_sp3, leer_clk,
                              sat_ecef_preciso, clk_interp, dt_relativista, observables_if)

# %% [markdown]
# ## TODO 1 — corrección de reloj precisa completa
# El reloj del satélite = valor del CLK + corrección relativista periódica.
# Los productos CLK NO incluyen el término -2(r·v)/c² → hay que sumarlo.

# %%
def reloj_sat_preciso(sp3, clk, s, t_tx):
    # TODO 1: return clk_interp(*clk[s], t_tx) + dt_relativista(sp3, s, t_tx)
    ...

# %% [markdown]
# ## TODO 2 — PVT con productos precisos (4 incógnitas)
# Como el PVT de 1.5 pero: posición del satélite del SP3, reloj del CLK+relat,
# y un ZWD fijo por el mapeo húmedo 1/sin(el).

# %%
def resolver(obs_if, t_rx, sp3, clk, x0, zwd=0.0):
    x = np.array([*x0[:3], 0.0])
    for _ in range(8):
        rows, res = [], []
        for s, Pif in obs_if.items():
            if s not in sp3 or s not in clk: continue
            tau = Pif / C
            for _k in range(2):
                xyz = sat_ecef_preciso(sp3, s, t_rx - tau)
                a = OMEGA_E * tau
                xyz = np.array([[np.cos(a), np.sin(a), 0],
                                [-np.sin(a), np.cos(a), 0], [0, 0, 1]]) @ xyz
                tau = np.linalg.norm(xyz - x[:3]) / C
            el, hh = el_y_h(xyz, x[:3])
            if el < np.radians(10): continue
            dt_sat = reloj_sat_preciso(sp3, clk, s, t_rx - tau)
            zhd = 2.3 * np.exp(-hh/7160.0) / np.sin(el); m_wet = 1.0/np.sin(el)
            rho = np.linalg.norm(xyz - x[:3])
            # TODO 2: pred = rho + x[3] - C*dt_sat + zhd + zwd*m_wet ; fila u=(x[:3]-xyz)/rho + [1]
            ...
        if len(rows) < 4: return None
        x = x + np.linalg.lstsq(np.array(rows), np.array(res), rcond=None)[0]
    return x

# %%
warnings.filterwarnings("ignore")
sp3, clk = leer_sp3(str(RAIZ/SP3)), leer_clk(str(RAIZ/CLK))
obs = gr.load(str(RAIZ/OBS), use="E", tlim=("2026-06-15T12:00","2026-06-15T13:00"))
errs = []
for i in range(len(obs.time)):
    x = resolver(observables_if(obs.isel(time=i)), a_sow(obs.time.values[i]), sp3, clk, np.array([*POS_OFICIAL]), zwd=0.14)
    if x is not None and np.all(np.isfinite(x)):
        errs.append(np.linalg.norm(matriz_enu(*ecef_a_geodetica(POS_OFICIAL)[:2]) @ (x[:3]-POS_OFICIAL)))
rms = np.sqrt(np.mean(np.square(errs)))
print(f"PPP-lite RMS 3D = {rms:.2f} m (broadcast ~1.95 m)")
assert rms < 2.0, "PPP-lite debería estar al nivel del broadcast o mejor"
print("LISTO: PPP-lite 7.4")
