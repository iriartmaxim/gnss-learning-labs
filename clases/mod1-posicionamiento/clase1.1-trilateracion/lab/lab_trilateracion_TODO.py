# %% [markdown]
# # Clase 1.1 — Lab: trilateración pura (ESQUELETO)
#
# Completá los `TODO` en orden; cada bloque tiene **auto-tests**. Acá NO hay
# reloj: los rangos son distancias verdaderas (el sesgo aparece en la 1.2).
# Incógnitas: `x = [x, y, z]` en ECEF, metros.

# %%
import json
from pathlib import Path

import numpy as np

DATA = Path("..") / "data" / "escenario_trilat.json"   # ajustar si hace falta
with open(DATA) as f:
    esc = json.load(f)

buenas = np.array(esc["balizas_buenas_ecef_m"])   # (4, 3)
malas = np.array(esc["balizas_malas_ecef_m"])
rg = np.array(esc["rangos_buenas_m"])             # rangos EXACTOS
rg_ruido = np.array(esc["rangos_buenas_ruido1m_m"])
r_true = np.array(esc["verdad"]["receptor_ecef_m"])
print("escenario cargado:", buenas.shape)

# %% [markdown]
# ## TODO 1 — Rangos
# $r_i = \lVert \mathbf{b}_i - \mathbf{x} \rVert$

# %%
def rangos(x, balizas):
    # TODO: una línea con numpy
    raise NotImplementedError

assert np.allclose(rangos(r_true, buenas), rg)
print("auto-test 1 OK")

# %% [markdown]
# ## TODO 2 — Jacobiano
# Fila $i$: $-\mathbf{u}_i^\top$, con $\mathbf{u}_i$ unitario receptor→baliza.
# Es la $G$ de la clase 1.2 **sin** la columna de reloj (n×3).

# %%
def matriz_J(x, balizas):
    # TODO
    raise NotImplementedError

_J = matriz_J(r_true, buenas)
assert _J.shape == (4, 3)
assert np.allclose(np.linalg.norm(_J, axis=1), 1.0)
print("auto-test 2 OK")

# %% [markdown]
# ## TODO 3 y 4 — Paso de Gauss-Newton e iteración

# %%
def resolver_trilat(balizas, r_med, x0=None, tol=1e-4, max_iter=30):
    x = np.zeros(3) if x0 is None else np.array(x0, dtype=float)
    hist = [x.copy()]
    # TODO: iterar: dr = r_med - rangos(x); delta = lstsq(J, dr); x += delta
    raise NotImplementedError
    return x, np.array(hist)

# %% [markdown]
# ## Validación A — rangos exactos, desde el centro de la Tierra
# Criterio: error < 1e-4 m en ≤ 8 iteraciones (referencia: 5 it, ~1e-9 m).

# %%
x, hist = resolver_trilat(buenas, rg)
err = np.linalg.norm(x - r_true)
print(f"iteraciones: {len(hist) - 1} | error: {err:.3e} m")
assert err < 1e-4 and len(hist) - 1 <= 8
print("VALIDACIÓN A OK")

# %% [markdown]
# ## Validación B — ruido σ = 1 m
# Criterio: error < 5 m (referencia: ~1.3 m con esta geometría).

# %%
xb, _ = resolver_trilat(buenas, rg_ruido)
print(f"error con ruido: {np.linalg.norm(xb - r_true):.2f} m")
assert np.linalg.norm(xb - r_true) < 5.0
print("VALIDACIÓN B OK")

# %% [markdown]
# ## Experimento 1 — La solución espejo (3 balizas)
# Con solo 3 balizas hay DOS puntos que satisfacen las 3 distancias: el
# verdadero y su reflexión respecto del plano de las balizas.
# 1. Resolvé con `buenas[:3]` arrancando del centro de la Tierra.
# 2. Calculá el punto espejo (reflejá `r_true` respecto del plano: normal
#    `n = cross(b1-b0, b2-b0)` normalizada; `espejo = p - 2*dot(p-b0, n)*n`)
#    y arrancá el solver desde cerca de ahí.
# 3. Verificá que AMBAS soluciones dan residuo ~0 y medí su separación
#    (referencia: ~32 800 km). ¿Por qué en GNSS esto casi nunca molesta?

# %%
# TODO

# %% [markdown]
# ## Experimento 2 — Monte Carlo: geometría buena vs. mala
# Con σ = 1 m, 500 corridas por geometría: error RMS 3D de cada una y el
# factor $\sqrt{\mathrm{tr}((J^\top J)^{-1})}$ en la posición verdadera.
# Referencia: RMS ~1.6 m vs ~10.7 m (amplificación ×6.8) y factores
# 1.61 vs 10.50. ¿Notás que el factor geométrico PREDICE el RMS? Eso ES
# el DOP — lo formalizamos en la clase 1.4.

# %%
# TODO

# %% [markdown]
# ### Cierre
# Volvé al README: ejercicios, mini-simulacro, rúbrica y bitácora.
