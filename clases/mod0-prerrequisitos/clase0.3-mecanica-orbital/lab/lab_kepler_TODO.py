# %% [markdown]
# # Lab 0.3 — Mecánica orbital mínima (versión TODO)
#
# Completá cada `TODO`. Al final de cada parte hay un auto-test.
# Objetivo: lo JUSTO de mecánica orbital para leer una efeméride GNSS
# en la clase 1.3 — ni más ni menos.
#
# Referencias esperadas:
#
# | Parte | Qué | Valor esperado |
# |---|---|---|
# | A | E(M=1, e=0.01) / iteraciones | 1.008460 / 3 |
# | A | E(M=1, e=0.7) / iteraciones | 1.694639 / 6 |
# | B | ν(M=1, e=0.7) | 2.4310 rad (139.3°) |
# | C | T GPS (a=26 560 km) | 11 h 57 m ≈ 43 077 s |
# | C | v GPS | 3.87 km/s |
# | D | T²/a³ | 9.904e-14 = 4π²/μ |
# | E | Ω̇ GPS (i=55°) | −0.039 °/día |
# | E | Ω̇ ISS (i=51.6°) | −4.952 °/día |

# %%
import numpy as np

MU = 3.986004418e14        # parámetro gravitacional terrestre [m^3/s^2]
RE = 6_378_137.0           # radio ecuatorial [m]
J2 = 1.08263e-3            # achatamiento dinámico
OMEGA_E = 7.2921151467e-5  # rotación terrestre [rad/s]

# %% [markdown]
# ## Parte A — la ecuación de Kepler por Newton
#
# M = E − e·sin(E) es trascendente: no se despeja E. Se resuelve por
# Newton sobre f(E) = E − e·sin(E) − M, con f'(E) = 1 − e·cos(E).
# Arrancá desde E₀ = M (funciona bien para e < 0.8).

# %%
def kepler_newton(M, e, tol=1e-12, max_iter=30):
    """Devuelve (E, iteraciones)."""
    E = M if e < 0.8 else np.pi
    for k in range(1, max_iter + 1):
        f = None   # TODO: E - e*sin(E) - M
        fp = None  # TODO: derivada
        dE = None  # TODO: paso de Newton
        E = None   # TODO: actualizar
        if abs(dE) < tol:
            return E, k
    raise RuntimeError("Kepler no convergió")

# --- auto-test A ---
E_gnss, it_gnss = kepler_newton(1.0, 0.01)
E_alta, it_alta = kepler_newton(1.0, 0.7)
assert abs(E_gnss - 1.008460) < 1e-5, f"E={E_gnss}"
assert abs(E_alta - 1.694639) < 1e-5, f"E={E_alta}"
print(f"A ok: e=0.01 -> E={E_gnss:.6f} ({it_gnss} it) | "
      f"e=0.7 -> E={E_alta:.6f} ({it_alta} it)")

# %% [markdown]
# ## Parte B — la cadena M → E → ν
#
# La anomalía verdadera sale de E con la fórmula del semiángulo
# (robusta en los cuatro cuadrantes):
#
# ν = 2·atan2( √(1+e)·sin(E/2), √(1−e)·cos(E/2) )
#
# Esta cadena es EXACTAMENTE lo que hace un receptor con cada efeméride.

# %%
def anomalia_verdadera(E, e):
    return None  # TODO

# --- auto-test B ---
e, M = 0.7, 1.0
E, _ = kepler_newton(M, e)
nu = anomalia_verdadera(E, e)
assert abs(nu - 2.4310) < 1e-3, f"nu={nu}"
assert np.isclose(E - e * np.sin(E), M), "Kepler no se satisface"
print(f"B ok: M={M} -> E={E:.4f} -> nu={nu:.4f} rad ({np.degrees(nu):.1f}°)")

# %% [markdown]
# ## Parte C — las órbitas que importan
#
# T = 2π√(a³/μ) y v_circular = √(μ/a). Completá la tabla para
# ISS (a=6798 km), GPS (26 560), Galileo (29 600) y GEO (42 164).

# %%
def periodo(a):
    return None  # TODO

def vel_circular(a):
    return None  # TODO

orbitas = [("ISS", 6_798e3), ("GPS", 26_560e3),
           ("Galileo", 29_600e3), ("GEO", 42_164e3)]
for nombre, a in orbitas:
    T = periodo(a)
    print(f"{nombre:<8} T = {int(T//3600)}h {int(T%3600//60):02d}m | "
          f"v = {vel_circular(a)/1e3:.2f} km/s")

# --- auto-test C ---
assert abs(periodo(26_560e3) - 43_077) < 30, "T GPS debe dar ~11h58m"
assert abs(vel_circular(26_560e3) - 3874) < 5, "v GPS ~3.87 km/s"
print("C ok: GPS es medio día SIDÉREO -> el ground track se repite cada día")

# %% [markdown]
# ## Parte D — tercera ley de Kepler
#
# T²/a³ debe dar la MISMA constante 4π²/μ para todas las órbitas.
# Es el chequeo de consistencia más barato que existe.

# %%
ctes = None  # TODO: lista de T²/a³ para las cuatro órbitas

# --- auto-test D ---
assert np.allclose(ctes, 4 * np.pi**2 / MU)
print(f"D ok: T²/a³ = {ctes[0]:.3e} = 4π²/μ para todas")

# %% [markdown]
# ## Parte E — J2: la Tierra achatada mueve el plano orbital
#
# El achatamiento hace precesar el nodo ascendente:
#
# Ω̇ = −(3/2)·J2·(Re/p)²·n·cos(i),  con n = √(μ/a³), p = a(1−e²)
#
# Calculalo para GPS (i=55°), Galileo (56°) e ISS (51.6°), en °/día.
# ESTE número es la razón por la que la efeméride trae OMEGA_DOT.

# %%
def regresion_nodal_J2(a, e, i_rad):
    return None  # TODO [rad/s]

# --- auto-test E ---
od_gps = np.degrees(regresion_nodal_J2(26_560e3, 0.01, np.radians(55))) * 86400
od_iss = np.degrees(regresion_nodal_J2(6_798e3, 0.01, np.radians(51.6))) * 86400
assert abs(od_gps - (-0.039)) < 0.002, f"GPS: {od_gps}"
assert abs(od_iss - (-4.952)) < 0.05, f"ISS: {od_iss}"
print(f"E ok: GPS {od_gps:+.3f} °/día | ISS {od_iss:+.3f} °/día")

# %% [markdown]
# Con esto ya podés leer una efeméride sin miedo: a, e, M₀, i, Ω, ω son
# los elementos; Kepler te da E; el semiángulo te da ν; y OMEGA_DOT/idot
# son las perturbaciones que la clase 1.3 va a aplicar tal cual dice el
# ICD. Registrá tus números en `bitacora.md`.
