# %% [markdown]
# # Lab 0.2 — Mínimos cuadrados, Gauss-Newton y rotaciones (versión TODO)
#
# Completá cada `TODO`. Al final de cada parte hay un auto-test: si no
# explota, vas bien. **Prohibido** `scipy.optimize` y `np.polyfit`
# (solo se permite `np.linalg.lstsq` para COTEJAR tu resultado).
#
# Referencias esperadas (con los datos de `data/datos_ajuste.json`):
#
# | Parte | Qué | Valor esperado |
# |---|---|---|
# | A | recta (a, b) | a≈2.011, b≈3.062 |
# | A | ortogonalidad máx |A'r| | < 1e-9 |
# | B | MC 1000: RMS sin/con pesos | 0.512 / 0.280 (mejora ×1.8) |
# | C | Gauss-Newton (p0, p1) | ≈(2.0278, 0.4968) en 8 iteraciones |
# | D | var(a) empírica / teórica | ≈1.00 (0.85–1.15) |
# | E | Rz(90°)Rx(90°)·ẑ vs Rx(90°)Rz(90°)·ẑ | (1,0,0) vs (0,−1,0) |
# | F | cond(M) a 90°/30°/5° | 1.00 / 3.73 / 22.90 |

# %%
import json
from pathlib import Path

import numpy as np

def cargar():
    ruta = Path(__file__).resolve().parents[1] / "data" / "datos_ajuste.json"
    with open(ruta) as f:
        return json.load(f)

d = cargar()

# %% [markdown]
# ## Parte A — recta por ecuaciones normales
#
# Modelo: y = a + b·x. Armá la matriz de diseño A = [1 | x] y resolvé
# x̂ = (AᵀA)⁻¹ Aᵀy **a mano** (con `np.linalg.solve`, no invirtiendo).
# Después verificá la propiedad geométrica clave: el residuo r = y − Ax̂
# es ORTOGONAL a las columnas de A (Aᵀr = 0).

# %%
x = np.array(d["recta"]["x"])
y = np.array(d["recta"]["y"])
sig = np.array(d["recta"]["sigma"])

A = None      # TODO: np.column_stack([...])
p_ls = None   # TODO: resolver (A'A) p = A'y con np.linalg.solve

# --- auto-test A ---
p_np, *_ = np.linalg.lstsq(A, y, rcond=None)
assert np.allclose(p_ls, p_np), "tus ecuaciones normales no coinciden con lstsq"
r = y - A @ p_ls
assert np.abs(A.T @ r).max() < 1e-9, "el residuo debe ser ortogonal a col(A)"
print(f"A ok: a={p_ls[0]:.3f} b={p_ls[1]:.3f} (verdad 2, 3)")

# %% [markdown]
# ## Parte B — mínimos cuadrados PONDERADOS
#
# La mitad de los puntos tiene σ=0.5 y la otra mitad σ=3.0 (¡6× peor!).
# Implementá W = diag(1/σ²) y x̂ = (AᵀWA)⁻¹ AᵀWy.
#
# OJO: en UNA realización cualquiera de las dos puede "ganar". La ventaja
# de ponderar es **estadística**: repetí 1000 veces con ruido nuevo
# (seed 123) y comparé el RMS del error de parámetros.

# %%
def ls_ponderado(A, b, sigmas):
    W = None  # TODO
    return None  # TODO: resolver (A'WA) p = A'Wb

rngB = np.random.default_rng(123)
err_ls2, err_w2 = 0.0, 0.0
N = 1000
for _ in range(N):
    yy = 2.0 + 3.0 * x + rngB.normal(0, sig)
    # TODO: acumular el error cuadrático de ambos estimadores
    pass

rms_ls = None  # TODO: np.sqrt(err_ls2 / N)
rms_w = None   # TODO

# --- auto-test B ---
assert rms_w < rms_ls, "en promedio, ponderar con los sigma correctos gana"
print(f"B ok: RMS sin pesos {rms_ls:.3f} | con pesos {rms_w:.3f} "
      f"(esperado 0.512 / 0.280)")

# %% [markdown]
# ## Parte C — Gauss-Newton a mano
#
# Modelo NO lineal: y = p0·exp(p1·x). No hay fórmula cerrada: se
# **linealiza** alrededor del punto actual y se itera:
#
# 1. r = y − f(x, p)
# 2. J = ∂f/∂p (jacobiano, n×2): columnas [exp(p1·x), p0·x·exp(p1·x)]
# 3. resolver (JᵀJ) δ = Jᵀr y actualizar p ← p + δ
# 4. repetir hasta ‖δ‖ < tol
#
# Este loop ES el que vas a escribir en la clase 1.2 para posicionar:
# ahí f serán las pseudodistancias y p = (x, y, z, c·dt).

# %%
exp_x = np.array(d["exponencial"]["x"])
exp_y = np.array(d["exponencial"]["y"])

def f_exp(x, p):
    return None  # TODO

def jac_exp(x, p):
    return None  # TODO: np.column_stack([...])  (n×2)

def gauss_newton(f, jac, p0, x, y, tol=1e-10, max_iter=50):
    p = np.array(p0, dtype=float)
    n_iter = 0
    for _ in range(max_iter):
        # TODO: r, J, delta, actualizar p, cortar si ||delta|| < tol
        n_iter += 1
    return p, n_iter

p_gn, it = gauss_newton(f_exp, jac_exp, [1.0, 1.0], exp_x, exp_y)

# --- auto-test C ---
assert np.allclose(p_gn, [2.0278, 0.4968], atol=1e-3), f"p_gn={p_gn}"
print(f"C ok: p={p_gn.round(4)} en {it} iteraciones (esperado 8)")

# %% [markdown]
# ## Parte D — la covarianza del estimador (semilla del DOP)
#
# Teoría: si el ruido es N(0, σ²), entonces cov(x̂) = σ² (AᵀA)⁻¹.
# Verificalo por Monte Carlo: 2000 realizaciones de ruido σ=1 sobre la
# recta verdadera (seed 99), estimá con LS y comparé la covarianza
# EMPÍRICA de los parámetros contra la teórica.
#
# En la clase 1.4 esta misma fórmula, aplicada a la geometría
# receptor-satélites, se llama **DOP**.

# %%
sigma_d = 1.0
rngD = np.random.default_rng(99)
M = 2000
params = np.zeros((M, 2))
for i in range(M):
    yy = 2.0 + 3.0 * x + rngD.normal(0, sigma_d, size=x.size)
    params[i] = None  # TODO: LS simple

cov_emp = None   # TODO: np.cov(params.T)
cov_teo = None   # TODO: sigma_d**2 * inv(A'A)

# --- auto-test D ---
ratio = cov_emp[0, 0] / cov_teo[0, 0]
assert 0.85 < ratio < 1.15, f"ratio={ratio:.3f}"
print(f"D ok: var(a) empírica/teórica = {ratio:.3f} (esperado ≈1.00)")

# %% [markdown]
# ## Parte E — rotaciones 3D
#
# Escribí Rx(θ), Ry(θ), Rz(θ) (convención activa, mano derecha).
# Verificá que son ortogonales con det=+1 y que NO conmutan.
# En la clase 0.3 las usás para pasar del plano orbital a ECEF.

# %%
def Rx(t):
    return None  # TODO

def Ry(t):
    return None  # TODO

def Rz(t):
    return None  # TODO

# --- auto-test E ---
for R in (Rx(0.7), Ry(-1.2), Rz(2.1)):
    assert np.allclose(R @ R.T, np.eye(3), atol=1e-12)
    assert np.isclose(np.linalg.det(R), 1.0)
z = np.array([0.0, 0.0, 1.0])
v1 = Rz(np.pi / 2) @ Rx(np.pi / 2) @ z
v2 = Rx(np.pi / 2) @ Rz(np.pi / 2) @ z
assert np.allclose(v1, [1, 0, 0], atol=1e-12)
assert np.allclose(v2, [0, -1, 0], atol=1e-12)
print("E ok: ortogonales, det=+1, y el orden importa:", v1.round(3), "vs", v2.round(3))

# %% [markdown]
# ## Parte F — condicionamiento: por qué existirá el DOP
#
# Armá matrices 2×2 cuyas columnas unitarias formen 90°, 30° y 5°.
# Calculá cond(M) y √tr((MᵀM)⁻¹). Columnas casi paralelas =
# mediciones casi redundantes = el error se AMPLIFICA.

# %%
def M_angulo(grados):
    t = np.radians(grados)
    return None  # TODO: columnas [1,0] y [cos t, sin t]

# --- auto-test F ---
conds = [np.linalg.cond(M_angulo(a)) for a in (90, 30, 5)]
assert conds[0] < conds[1] < conds[2], "a menor ángulo, peor condicionamiento"
print("F ok: cond(M) =", [f"{c:.2f}" for c in conds], "(esperado 1.00, 3.73, 22.90)")

# %% [markdown]
# Si llegaste acá con todos los "ok": tenés el motor matemático completo
# del módulo 1. Compará tus números con la tabla del README y registrá
# los resultados en `bitacora.md`.
