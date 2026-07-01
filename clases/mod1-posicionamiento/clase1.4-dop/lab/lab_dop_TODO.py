# %% [markdown]
# # Clase 1.4 — Lab: DOP y geometría (ESQUELETO)
#
# Todo sale de una sola matriz: $Q = (G^\top G)^{-1}$, con la $G$ que ya
# construiste en la clase 1.2. Completá los `TODO` en orden.

# %%
import json
from itertools import combinations
from pathlib import Path

import numpy as np

DATA = Path("..") / "data" / "escenario_10sats.json"   # ajustar si hace falta
with open(DATA) as f:
    esc = json.load(f)

sats = np.array(esc["sat_ecef_m"])            # (10, 3)
azel = np.array(esc["sat_azel_deg"])          # (10, 2) az, el
pr = np.array(esc["pseudodistancias_m"])
r_true = np.array(esc["verdad"]["receptor_ecef_m"])
lat, lon, _ = esc["verdad"]["receptor_geodetico"]
print("escenario cargado:", sats.shape)

# %% [markdown]
# ## TODO 1 — La G de la clase 1.2
# Fila $i$: $[-\mathbf{u}_i^\top,\; 1]$ (n×4). Si ya la tenés de la 1.2, traela.

# %%
def matriz_G(x3, sats):
    # TODO (3 líneas): rho, unitarios, hstack con columna de unos
    raise NotImplementedError

G = matriz_G(r_true, sats)
assert G.shape == (10, 4)
assert np.allclose(G[:, 3], 1.0)
print("auto-test 1 OK")

# %% [markdown]
# ## TODO 2 — GDOP, PDOP, TDOP
# $Q = (G^\top G)^{-1}$; GDOP = $\sqrt{\mathrm{tr}(Q)}$; PDOP usa el bloque
# 3×3 de posición; TDOP es $\sqrt{Q_{44}}$.
# Criterio: GDOP² = PDOP² + TDOP² (¡verificalo!).
# Referencia con los 10 sats: GDOP 1.770 | PDOP 1.558 | TDOP 0.839.

# %%
def dops_ecef(G):
    # TODO
    raise NotImplementedError

Q, gdop, pdop, tdop = dops_ecef(G)
print(f"GDOP={gdop:.3f} PDOP={pdop:.3f} TDOP={tdop:.3f}")
assert abs(gdop**2 - (pdop**2 + tdop**2)) < 1e-9
assert abs(gdop - 1.770) < 0.01
print("auto-test 2 OK (identidad y valor de referencia)")

# %% [markdown]
# ## TODO 3 — HDOP y VDOP (rotar a ENU)
# El bloque de posición de $Q$ está en ECEF; rotalo a ENU con la matriz
# $R$ (filas: este, norte, arriba) y sacá HDOP = $\sqrt{Q_{ee}+Q_{nn}}$,
# VDOP = $\sqrt{Q_{uu}}$.
# Referencia: HDOP 0.879 | VDOP 1.286. ¿Por qué VDOP > HDOP SIEMPRE?

# %%
def hdop_vdop(Q, lat_deg, lon_deg):
    # TODO: construir R (3x3), Q_enu = R @ Q[:3,:3] @ R.T
    raise NotImplementedError

hdop, vdop = hdop_vdop(Q, lat, lon)
print(f"HDOP={hdop:.3f} VDOP={vdop:.3f}")
assert vdop > hdop
assert abs(hdop - 0.879) < 0.01
print("auto-test 3 OK")

# %% [markdown]
# ## Experimento 1 — Barrido de la máscara de elevación
# Para máscaras de 0° a 45° (paso 5°): filtrá los satélites con el ≥ máscara,
# recalculá PDOP/HDOP/VDOP y armá la tabla. Referencia: PDOP pasa de 1.56
# (10 sats) a 7.83 (4 sats con máscara 45°). ¿Qué DOP se degrada más rápido
# y por qué?

# %%
# TODO

# %% [markdown]
# ## Experimento 2 — Mejor y peor subconjunto de 4
# Recorré `combinations(range(10), 4)` (son 210) y encontrá el GDOP mínimo
# y máximo. Referencia: mejor 2.30 (un sat alto + tres bajos repartidos:
# ¡el tetraedro!); peor ≈ 1204 (cuatro casi coplanares). Dibujá ambos en
# el skyplot a mano y explicá la diferencia.

# %%
# TODO

# %% [markdown]
# ## Experimento 3 — El DOP predice el error (Monte Carlo)
# 300 corridas: agregá ruido σ = 1 m a las pseudodistancias, resolvé con tu
# solver de la 1.2 y calculá el error RMS 3D. Compará con PDOP × σ.
# Referencia: 1.56 m vs 1.56 m (cociente 1.00). Guardá tu cociente en la
# bitácora.

# %%
# TODO

# %% [markdown]
# ### Cierre
# Volvé al README: ejercicios (la inversa 3×3 a mano te espera),
# mini-simulacro, rúbrica y bitácora.
