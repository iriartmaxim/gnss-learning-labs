# %% [markdown]
# # Clase 7.2 — Lab: EKF sobre pseudodistancias y Doppler (ESQUELETO)
#
# Completá los `TODO` en orden. Reusa el motor de la 1.5 (imports abajo).
# Correr desde la raíz del repo (requiere data/raw/2026/166):
#
#     python3 clases/mod7-estimacion/clase7.2-ekf/lab/lab_ekf_TODO.py

# %%
import sys
import warnings
from pathlib import Path

import numpy as np

warnings.filterwarnings("ignore")
RAIZ = Path(__file__).resolve().parents[3].parent
sys.path.insert(0, str(RAIZ / "clases/mod1-posicionamiento/clase1.5-pvt/lab/soluciones"))
import georinex as gr
from lab_pvt_solucion import (C, GAMMA, NAV, OBS, POS_OFICIAL, a_sow,
                              elegir_efemeride, gauss_newton_pvt,
                              kepler_a_ecef, pseudorango_corregido,
                              registros_fnav)

F1 = 1575.42e6
LAM1 = C / F1

# %% [markdown]
# ## TODO 1 — velocidad del satélite (derivada centrada del propagador 1.3)

# %%
def vel_sat(ef, t_tx, dt=0.5):
    # TODO 1: (r(t+dt) - r(t-dt)) / (2 dt) con kepler_a_ecef
    ...


# auto-test: |v| de un Galileo ~ 3.6-3.8 km/s
print("cargando nav (georinex)...")
EFS = registros_fnav(gr.load(str(RAIZ / NAV), use="E"))
ef0 = elegir_efemeride(EFS["E19"], 129600.0)
v0 = np.linalg.norm(vel_sat(ef0, 129600.0))
assert 3500 < v0 < 3800, f"|v|={v0:.0f} m/s"
print(f"TODO 1 OK (|v| E19 = {v0:.0f} m/s)")

# %% [markdown]
# ## TODO 2 — las dos filas por satélite (código y Doppler)
#
# h_P = |s−p| + cδt, H_P = (−u, 0, 1, 0) · h_D = u·(vs−v) + cδṫ,
# H_D = (0, −u, 0, 1) · medición Doppler: ρ̇ = −λ₁·D1X.

# %%
def filas_sat(x, xyz, Pc, rr, vs):
    d = xyz - x[:3]
    rho = np.linalg.norm(d)
    u = d / rho
    # TODO 2: devolvé (H 2x8, z 2, h 2) con las dos filas
    ...
    return H, z, h

# %% [markdown]
# ## TODO 3 — el ciclo EKF de 8 estados
#
# F: CV en posición + cδt integra cδṫ. Q: aceleración blanca (σa=1e-3)
# + deriva RW (σd=0.03). R: diag(σP²=1, σD²=0.05²) por satélite.

# %%
def ekf_paso(x, P, sats, dt=30.0):
    # TODO 3: predicción (F, Q), detector de salto de ms (TODO 4),
    #         apilar filas de todos los sats, ganancia y corrección
    ...
    return x, P

# %% [markdown]
# ## TODO 4 — el detector de salto de milisegundo
#
# Antes de corregir: innovación mediana de los CÓDIGOS; si ≈ k·c·1ms
# (|k|≥1), sumá k·c·1ms al estado cδt. Jamás a la posición.

# %% [markdown]
# ## Corrida completa (ya armada): frío -> GN -> EKF -> números

# %%
def medir_epoca(ep, t_rx, efs, rec):
    sats = []
    for s in ep.sv.values:
        s = str(s)
        if s not in efs:
            continue
        try:
            P1 = float(ep.sel(sv=s)["C1X"]); P5 = float(ep.sel(sv=s)["C5X"])
            D1 = float(ep.sel(sv=s)["D1X"])
        except (KeyError, TypeError):
            continue
        if not (np.isfinite(P1) and np.isfinite(P5) and np.isfinite(D1)):
            continue
        Pif = (GAMMA * P1 - P5) / (GAMMA - 1)
        ef = elegir_efemeride(efs[s], t_rx)
        xyz, Pc, el = pseudorango_corregido(ef, Pif, t_rx, rec)
        if el is not None and el < np.radians(10):
            continue
        sats.append((s, xyz, Pc, -LAM1 * D1, vel_sat(ef, t_rx - Pif / C)))
    return sats


print("cargando obs 12:00-13:00...")
obs = gr.load(str(RAIZ / OBS), use="E", tlim=("2026-06-15T12:00", "2026-06-15T13:00"))
tiempos = obs.time.values
t0 = a_sow(tiempos[0])
s0 = medir_epoca(obs.isel(time=0), t0, EFS, None)
fx, _, _ = gauss_newton_pvt(np.array([s[1] for s in s0]), np.array([s[2] for s in s0]))
x = np.zeros(8); x[:3], x[6] = fx[:3], fx[3]
P = np.diag([50.0**2] * 3 + [2.0**2] * 3 + [100.0**2, 500.0**2])
errs, vels, drifts = [], [], []
for tt in tiempos[1:]:
    sats = medir_epoca(obs.sel(time=tt), a_sow(tt), EFS, x[:3])
    x, P = ekf_paso(x, P, sats)
    errs.append(np.linalg.norm(x[:3] - POS_OFICIAL))
    vels.append(np.linalg.norm(x[3:6])); drifts.append(x[7])
errs = np.array(errs)
conv = errs[len(errs)//3:]
print(f"3D medio {conv.mean():.2f} m | |v| {np.mean(vels[40:])*1e3:.0f} mm/s | deriva {np.mean(drifts[40:]):+.2f} m/s")
assert conv.mean() < 2.5, "esperaba ~1.2 m"
assert np.mean(vels[40:]) * 1e3 < 40
assert abs(np.mean(drifts[40:]) + 196.1) < 1.0, "la deriva es -196.1 m/s"
print("LISTO: EKF sobre observables reales, saltos de ms incluidos")
