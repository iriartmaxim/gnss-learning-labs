# %% [markdown]
# # Lab 4.2 — Broadcast vs SP3 con descomposición RTN (ESQUELETO)
#
# Propagá la broadcast (motor de 1.3), interpolá el SP3, y descomponé la
# diferencia en Radial/Along/Cross por constelación. Completá los TODO.
# Los lectores de nav/SP3 y la interpolación están en la solución.
#
#     python3 clases/mod4-orbitas/clase4.2-pod/lab/lab_pod_TODO.py

# %%
import sys, warnings
from pathlib import Path
import numpy as np
RAIZ = Path(__file__).resolve().parents[4].parent
sys.path.insert(0, str(RAIZ / "clases/mod1-posicionamiento/clase1.3-efemerides/lab/soluciones"))
sys.path.insert(0, str(RAIZ / "clases/mod4-orbitas/clase4.2-pod/lab/soluciones"))
import georinex as gr
from lab_efemerides_solucion import kepler_a_ecef, elegir_efemeride
from lab_pod_solucion import NAV, SP3, registros, leer_sp3_multi, lagrange

# %% [markdown]
# ## TODO 1 — la terna RTN
# Con la posición r y la velocidad v del satélite:
#   R = r/|r| (radial) ; Cross = (r×v)/|r×v| (normal al plano) ; Along = Cross×R.
# Proyectá la diferencia dpos en esos tres ejes.

# %%
def rtn(dpos, r_sat, v_sat):
    # TODO 1: R, Cross, Along y devolvé [dpos·R, dpos·Along, dpos·Cross]
    ...

# %% [markdown]
# ## TODO 2 — diferencia broadcast − SP3 por época
# Para cada satélite y época: posición broadcast (kepler_a_ecef), velocidad
# por diferencia finita, posición SP3 (lagrange, en metros), y RTN de la resta.

# %%
def evaluar(efs, sp3):
    difs = []
    ts_eval = 86400 + np.arange(10*3600, 14*3600+1, 300.0)   # sow, día 166 = lunes
    for s, recs in efs.items():
        if s not in sp3: continue
        for t in ts_eval:
            ef = elegir_efemeride(recs, t)
            if abs(t - ef["Toe"]) > 3600: continue
            xb = kepler_a_ecef(ef, t)
            vb = (kepler_a_ecef(ef, t+1) - kepler_a_ecef(ef, t-1)) / 2.0
            xp = lagrange(*sp3[s], t) * 1000.0
            # TODO 2: difs.append(rtn(xb - xp, xb, vb))
            ...
    return np.array(difs)

# %%
warnings.filterwarnings("ignore")
sp3 = leer_sp3_multi(str(RAIZ/SP3))
efs = registros(gr.load(str(RAIZ/NAV), use="E"), "E")
d = evaluar(efs, sp3)
rms = np.sqrt((d**2).mean(axis=0))
print(f"Galileo RMS  R={rms[0]:.2f}  A={rms[1]:.2f}  C={rms[2]:.2f} m  |  3D={np.sqrt((d**2).sum(1).mean()):.2f} m")
assert 0.3 < rms[0] < 2.0 and len(d) > 100, "radial fuera de rango"
print("LISTO: POD 4.2")
