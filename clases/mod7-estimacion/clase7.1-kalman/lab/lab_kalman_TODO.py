# %% [markdown]
# # Clase 7.1 — Lab: filtro de Kalman desde cero (ESQUELETO)
#
# Completá los `TODO` en orden; cada bloque tiene auto-tests. Correr
# desde la raíz del repo (requiere `resultados_1_5.json` de la clase 1.5):
#
#     python3 clases/mod7-estimacion/clase7.1-kalman/lab/lab_kalman_TODO.py

# %%
import json
import numpy as np

rng = np.random.default_rng(71)

# %% [markdown]
# ## TODO 1 — el ciclo del KF (el corazón de la clase)
#
# Cinco ecuaciones (README §3.1): predicción de x y P, innovación,
# ganancia, corrección de x y P. Devolvé estados filtrados e innovaciones.

# %%
def kf(z, F, H, Q, R, x0, P0):
    x, P = x0.copy(), P0.copy()
    xs, inns = [], []
    for zk in z:
        # TODO 1: predicción (x, P), innovación y = zk - H x⁻,
        #         S = H P⁻ Hᵀ + R, ganancia K, corrección de x y P
        ...
        xs.append(x.copy()); inns.append(y.copy())
    return np.array(xs), np.array(inns)

# %% [markdown]
# ## TODO 2 — Parte A: la constante (el KF ES el promedio)

# %%
verdad = 5.0
z = verdad + rng.normal(0, 1.0, 50)
# TODO 2: F, H, Q, R para estimar una constante (todo escalar 1x1; Q=0)
F, H, Q, R = ..., ..., ..., ...
xs, _ = kf(z[:, None], F, H, Q, R, np.zeros(1), np.eye(1) * 100)
print(f"[A] KF: {xs[-1,0]:.4f} | promedio: {z.mean():.4f}")
assert abs(xs[-1, 0] - z.mean()) < 5e-3
print("TODO 2 OK")

# %% [markdown]
# ## TODO 3 — Parte B: la rampa (el modelo trabaja)
#
# Estado (pos, vel), medición solo pos. σa = 0.05, R = 4, dt = 1.

# %%
dt = 1.0
t = np.arange(80.0)
pos = 2.0 + 0.7 * t
z = pos + rng.normal(0, 2.0, len(t))
# TODO 3: F (con dt), H, Q (modelo de aceleración blanca, README §12), R
F, H = ..., ...
Q, R = ..., ...
xs, _ = kf(z[:, None], F, H, Q, R, np.zeros(2), np.eye(2) * 100)
rms_kf = np.sqrt(((xs[:, 0] - pos) ** 2).mean())
print(f"[B] RMS KF {rms_kf:.2f} m | v estimada {xs[-1,1]:.3f}")
assert abs(xs[-1, 1] - 0.7) < 0.05 and rms_kf < 0.9
print("TODO 3 OK")

# %% [markdown]
# ## TODO 4 — Parte C: la serie REAL del 1.5
#
# Estado (E,N,U,vE,vN,vU); medición ENU. σa = 1e-4 m/s², R = diag(var
# por eje de la serie), dt = mediana de los saltos de tiempo. Después:
# scatter crudo vs filtrado, velocidad final y ρ(1) de innovaciones.

# %%
d = json.load(open("clases/mod1-posicionamiento/clase1.5-pvt/data/resultados_1_5.json"))
S = np.array(d["serie"])
tiempo, enu = S[:, 0], S[:, 1:4]
# TODO 4: armá F, H, Q, R y corré kf(); calculá std por eje (últimos 2/3),
#         velocidad final en mm/s y rho(1) de las innovaciones por eje
...
print(f"    scatter KF: {std_kf.round(2)} | v: {v_final.round(1)} mm/s | rho1: {rho1.round(2)}")
n = len(enu) // 3
std_raw = enu[n:].std(axis=0)
assert (std_kf < 0.75 * std_raw).all(), "no redujo el scatter"
assert (np.abs(v_final) < 10).all(), "la estación no se mueve"
assert (np.abs(rho1) < 0.35).all(), "innovaciones no blancas"
print("TODO 4 OK")

# %%
print("LISTO: KF construido, validado y auditado por sus innovaciones")
