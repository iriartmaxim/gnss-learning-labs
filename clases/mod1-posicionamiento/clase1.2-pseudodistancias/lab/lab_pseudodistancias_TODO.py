# %% [markdown]
# # Clase 1.2 — Lab: pseudodistancias y sesgo de reloj (ESQUELETO)
#
# Completá los `TODO` en orden. Cada bloque tiene **auto-tests**: si pasan,
# seguí; si no, volvé a la teoría (README §Teoría). No abras la solución
# (`soluciones/`) hasta que los auto-tests pasen o lleves >30 min trabado.
#
# **Incógnitas**: `x = [x, y, z, c·dt]` — posición ECEF en metros y sesgo de
# reloj del receptor **en metros** (c·δt, no δt). Convención de la clase:
# fila de la matriz de diseño `[-u_x, -u_y, -u_z, 1]`, con `u` unitario
# receptor→satélite.

# %%
import json
from pathlib import Path

import numpy as np

C = 299_792_458.0  # m/s

DATA = Path("..") / "data" / "escenario_5sats.json"   # ajustar si hace falta
with open(DATA) as f:
    esc = json.load(f)

sats = np.array(esc["sat_ecef_m"])                    # (5, 3)
pr = np.array(esc["pseudodistancias_m"])              # (5,)  sin ruido
pr_ruido = np.array(esc["pseudodistancias_ruido1m_m"])
r_true = np.array(esc["verdad"]["receptor_ecef_m"])
cdt_true = esc["verdad"]["c_dt_receptor_m"]
print("escenario cargado:", sats.shape, "| c·dt verdadero =", cdt_true, "m")

# %% [markdown]
# ## TODO 1 — Rangos geométricos
# $\rho_i = \lVert \mathbf{r}^{s_i} - \mathbf{r}_r \rVert$

# %%
def rangos_geometricos(x, sats):
    """Distancia geométrica a cada satélite. x = [x, y, z, c·dt]."""
    # TODO: una línea con numpy (norma por filas de sats - x[:3])
    raise NotImplementedError

# auto-test 1
_rho = rangos_geometricos(np.array([*r_true, 0.0]), sats)
assert _rho.shape == (5,)
assert np.allclose(_rho, pr - cdt_true), "los rangos no cierran con P - c·dt"
print("auto-test 1 OK")

# %% [markdown]
# ## TODO 2 — Matriz de diseño G
# Fila $i$: $[-\mathbf{u}_i^\top,\; 1]$, con
# $\mathbf{u}_i = (\mathbf{r}^{s_i} - \mathbf{r}_r)/\rho_i$.
#
# *Pregunta para la bitácora:* ¿por qué la 4ª columna es toda de unos?

# %%
def matriz_G(x, sats):
    # TODO: calcular rho, los unitarios u (broadcasting) y apilar [-u | 1]
    raise NotImplementedError

# auto-test 2
_G = matriz_G(np.array([*r_true, 0.0]), sats)
assert _G.shape == (5, 4)
assert np.allclose(_G[:, 3], 1.0)
assert np.allclose(np.linalg.norm(_G[:, :3], axis=1), 1.0), "las filas -u no son unitarias"
print("auto-test 2 OK")

# %% [markdown]
# ## TODO 3 — Un paso de Gauss-Newton
# 1. pseudodistancia modelada: `pred = rho + x[3]`
# 2. residuo prefit: `dP = pr - pred`
# 3. resolver `G · delta = dP` en mínimos cuadrados (`np.linalg.lstsq`)
# 4. devolver `x + delta` y `‖delta‖`

# %%
def paso_gauss_newton(x, sats, pr):
    # TODO
    raise NotImplementedError

# %% [markdown]
# ## TODO 4 — Iterar hasta converger
# Desde `x0 = [0, 0, 0, 0]` (¡el centro de la Tierra, con reloj perfecto!),
# iterá hasta `‖delta‖ < 1e-4` m o 20 iteraciones. Guardá el historial.

# %%
def resolver_pvt(sats, pr, x0=None, tol=1e-4, max_iter=20):
    x = np.zeros(4) if x0 is None else np.array(x0, dtype=float)
    historial = [x.copy()]
    # TODO: bucle de iteración
    raise NotImplementedError
    return x, np.array(historial)

# %% [markdown]
# ## Validación A (sin ruido) — criterio de la clase
# Error de posición y de c·dt **< 1e-4 m** (0.1 mm) y ≤ 8 iteraciones.

# %%
x, hist = resolver_pvt(sats, pr)
err_pos = np.linalg.norm(x[:3] - r_true)
err_cdt = abs(x[3] - cdt_true)
print(f"iteraciones: {len(hist) - 1} | err pos: {err_pos:.3e} m | err c·dt: {err_cdt:.3e} m")
assert err_pos < 1e-4 and err_cdt < 1e-4 and len(hist) - 1 <= 8
print("VALIDACIÓN A OK")

# %% [markdown]
# ## Validación B (ruido σ = 1 m)
# Con `pr_ruido`: error de posición esperable de unos pocos metros
# (regla: ~PDOP × σ; acá PDOP ≈ 2.4). Criterio: **< 10 m**.

# %%
xn, _ = resolver_pvt(sats, pr_ruido)
err_b = np.linalg.norm(xn[:3] - r_true)
print(f"err pos con ruido: {err_b:.2f} m | err c·dt: {abs(xn[3] - cdt_true):.2f} m")
assert err_b < 10.0
print("VALIDACIÓN B OK")

# %% [markdown]
# ## Experimento 1 — ¿Y si ignoro el reloj?
# Resolvé SOLO `(x, y, z)` (matriz `-u`, 3 columnas) usando `pr` tal cual.
# Anotá en la bitácora: ¿de qué orden es el error? ¿mayor o menor que
# c·dt = 749.5 km? ¿por qué no es exactamente igual?

# %%
# TODO: variante de 3 incógnitas y comparar np.linalg.norm(x3 - r_true)

# %% [markdown]
# ## Experimento 2 — Solo 3 satélites
# Corré `resolver_pvt(sats[:3], pr[:3])`. G queda de 3×4: sistema
# subdeterminado. ¿Qué devuelve `lstsq`? ¿Es una posición confiable?

# %%
# TODO

# %% [markdown]
# ## Experimento 3 — Gráfico de convergencia
# Con el historial de la Validación A, graficá `‖x_k[:3] - r_true‖` en
# escala log vs. iteración (comparar con `img/fig2_convergencia.svg`).
# ¿Qué tipo de convergencia ves cerca de la solución?

# %%
# TODO: matplotlib, semilogy

# %% [markdown]
# ## Experimento 4 — Fallo de reloj en UN satélite (puente a RAIM, clase 5.1)
# Sumale `13.7e-6 * C` (el error del caso GPS de enero 2016) a la
# pseudodistancia del satélite 3 y resolvé de nuevo.
# 1. ¿Cuánto se corre la posición?
# 2. Calculá los residuos postfit `pr_falla - (rho(x̂) + x̂[3])`.
#    ¿El residuo del satélite fallado es el más grande? ¿Delata al culpable?

# %%
# TODO

# %% [markdown]
# ### Cierre
# Volvé al README: mini-simulacro, rúbrica de cierre y bitácora.
