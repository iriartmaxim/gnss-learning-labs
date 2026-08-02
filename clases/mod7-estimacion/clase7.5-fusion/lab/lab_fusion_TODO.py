# %% [markdown]
# # Lab 7.5 — Fusión GNSS+INS loosely-coupled (ESQUELETO)
#
# INS (acelerómetros) integra y deriva; GNSS ancla pero tiene cortes. El KF
# los fusiona. Todo sintético y determinista (seed 42). Completá los TODO.
# Depende del KF de la clase 7.1.
#
#     python3 clases/mod7-estimacion/clase7.5-fusion/lab/lab_fusion_TODO.py

# %%
import sys
from pathlib import Path
import numpy as np
RAIZ = Path(__file__).resolve().parents[4].parent
sys.path.insert(0, str(RAIZ / "clases/mod7-estimacion/clase7.5-fusion/lab/soluciones"))
from lab_fusion_solucion import (DT, T, GNSS_CADA, CORTE, SIG_GNSS, SIG_ACC,
                                 BIAS_ACC, trayectoria, ins_solo)

# %% [markdown]
# ## TODO 1 — el modelo de predicción del KF
# Estado [x, y, vx, vy]. F propaga con velocidad constante en DT; B convierte
# la aceleración medida (control) en cambio de estado (½DT² a posición, DT a
# velocidad).

# %%
def matrices():
    # TODO 1: F (4x4, velocidad constante), B (4x2, entrada de aceleración)
    F = ...
    B = ...
    H = np.array([[1, 0, 0, 0], [0, 1, 0, 0]], float)
    return F, B, H

# %% [markdown]
# ## TODO 2 — el ciclo predecir/corregir
# Cada paso: predecir con el IMU (F,B). Si hay GNSS en ese paso, corregir
# con la ganancia de Kalman. Si no (corte), seguir solo con la predicción.

# %%
def fusion(a_med, gnss):
    F, B, H = matrices()
    Q = np.diag([0.01, 0.01, 0.02, 0.02]); R = np.eye(2) * SIG_GNSS**2
    x = np.array([0.0, 0.0, 8.0, 0.0]); P = np.eye(4) * 10
    out = []
    for k, am in enumerate(a_med):
        # TODO 2a: predicción  x = F@x + B@am ;  P = F@P@F.T + Q
        ...
        if gnss[k] is not None:
            z = gnss[k]
            # TODO 2b: S = H@P@H.T + R ; K = P@H.T@inv(S) ; x += K@(z-H@x) ; P = (I-K@H)@P
            ...
        out.append(x[:2].copy())
    return np.array(out)

# %%
rng = np.random.default_rng(42)
t, p, v, a = trayectoria()
a_med = a + BIAS_ACC + rng.normal(0, SIG_ACC, a.shape)
gnss = [None]*len(t)
for k in range(len(t)):
    if k % GNSS_CADA == 0 and not (CORTE[0] <= t[k] <= CORTE[1]):
        gnss[k] = p[k] + rng.normal(0, SIG_GNSS, 2)
p_ins = ins_solo(a_med); p_kf = fusion(a_med, gnss)
rms_ins = np.sqrt(np.mean(np.sum((p_ins-p)**2, axis=1)))
rms_kf = np.sqrt(np.mean(np.sum((p_kf-p)**2, axis=1)))
print(f"RMS INS solo {rms_ins:.1f} m | fusión KF {rms_kf:.2f} m")
assert rms_kf < rms_ins, "la fusión debería superar al INS solo"
print("LISTO: fusión 7.5")
