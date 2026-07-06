# %% [markdown]
# # Lab 4.1 — Propagador kepleriano vs realidad (TODO)
#
# Empezamos el módulo de órbitas con una pregunta incómoda: si sabemos
# resolver Kepler desde la clase 0.3, ¿por qué la efeméride broadcast
# trae DIECISÉIS parámetros y no seis? Porque la órbita real NO es una
# elipse de dos cuerpos: la Tierra está achatada (J2), el Sol y la Luna
# tiran, la presión de radiación empuja. El ICD mete correcciones que
# absorben esas perturbaciones sobre un arco de ~3 h.
#
# Acá vas a MEDIR cuánto vale cada corrección: propagás la misma
# efeméride apagando grupos de parámetros y ves cuánto se despega de la
# broadcast completa. Reusás el propagador de la 1.5, ahora con perillas.
#
# Correr desde la raíz del repo (~1 min, sin descargas).

# %%
import sys
import warnings
from pathlib import Path

import numpy as np

warnings.filterwarnings("ignore")
RAIZ = Path.cwd()
sys.path.insert(0, str(RAIZ / "clases/mod1-posicionamiento/clase1.5-pvt/lab/soluciones"))
import lab_pvt_solucion as pvt
from lab_pvt_solucion import MU, NAV, OMEGA_E, wrap_tk

# %% [markdown]
# ## Parte A — El propagador con perillas
#
# Partí del `kepler_a_ecef` de la 1.5 y agregá tres flags que apagan
# familias de correcciones:
# - `deltan`: la corrección Δn al movimiento medio (n = n₀ + Δn)
# - `armonicos`: los seis Cxx (Cus/Cuc en el argumento de latitud,
#   Crs/Crc en el radio, Cis/Cic en la inclinación)
# - `idot`: la deriva lineal de la inclinación (IDOT·tk)
#
# La rotación del nodo (Ω) queda SIEMPRE: sin ella el resultado no está
# en un marco Tierra-fija y la comparación no tiene sentido.

# %%
def propagar(ef, t_sow, armonicos=True, idot=True, deltan=True):
    A = ef["sqrtA"] ** 2
    e = ef["Eccentricity"]
    tk = wrap_tk(t_sow - ef["Toe"])
    n = np.sqrt(MU / A**3) + (ef["DeltaN"] if deltan else 0.0)  # TODO: perilla deltan
    M = ef["M0"] + n * tk
    E = M
    for _ in range(40):
        E += (M - (E - e * np.sin(E))) / (1 - e * np.cos(E))
    nu = 2 * np.arctan2(np.sqrt(1 + e) * np.sin(E / 2),
                        np.sqrt(1 - e) * np.cos(E / 2))
    phi = nu + ef["omega"]
    s2, c2 = np.sin(2 * phi), np.cos(2 * phi)
    if armonicos:        # TODO: cuando armonicos=False, u=phi, r=A(1-e cosE), i=Io
        u = None    # TODO: phi + Cus*s2 + Cuc*c2
        r = None    # TODO: A*(1-e*cosE) + Crs*s2 + Crc*c2
        i = None    # TODO: Io + Cis*s2 + Cic*c2
    else:
        u, r, i = phi, A * (1 - e * np.cos(E)), ef["Io"]
    if idot:
        i = i + ef["IDOT"] * tk
    Om = ef["Omega0"] + (ef["OmegaDot"] - OMEGA_E) * tk - OMEGA_E * ef["Toe"]
    xp, yp = r * np.cos(u), r * np.sin(u)
    return np.array([xp * np.cos(Om) - yp * np.cos(i) * np.sin(Om),
                     xp * np.sin(Om) + yp * np.cos(i) * np.cos(Om),
                     yp * np.sin(i)])


# %% [markdown]
# ## Parte B — Medir cada corrección con datos reales

# %%
import georinex as gr
print("cargando BRDC día 166 (Galileo)...")
ds = gr.load(NAV, use="E")
efs = pvt.registros_fnav(ds)
sv = max(efs, key=lambda s: len(efs[s]))
lista = sorted(efs[sv], key=lambda e: e["Toe"])
ef = lista[len(lista) // 2]
print(f"satélite {sv}: a={ef['sqrtA']**2/1000:.0f} km, i={np.degrees(ef['Io']):.1f}°")

tks = np.arange(-7200, 7201, 300.0)
full = {tk: propagar(ef, ef["Toe"] + tk) for tk in tks}
for nom, kw in {"Δn": dict(deltan=False),
                "armónicos": dict(armonicos=False),
                "IDOT": dict(idot=False),
                "2 cuerpos": dict(armonicos=False, idot=False, deltan=False)}.items():
    d = np.array([np.linalg.norm(propagar(ef, ef["Toe"]+tk, **kw) - full[tk])
                  for tk in tks])
    print(f"  sin {nom:12s}: max {d.max():7.1f} m | en Toe {d[len(d)//2]:6.1f} m")

# %% [markdown]
# ## Auto-test
#
# La solución agrega la Parte C (extrapolar la elipse pura 12 h → km) y
# el análisis de los saltos en los empalmes entre efemérides.

# %%
d_dn = np.array([np.linalg.norm(propagar(ef, ef["Toe"]+tk, deltan=False) - full[tk])
                 for tk in tks])
d_2c = np.array([np.linalg.norm(propagar(ef, ef["Toe"]+tk, armonicos=False,
                 idot=False, deltan=False) - full[tk]) for tk in tks])
i0 = len(tks) // 2
assert d_dn[i0] < 1, "Δn depende de tk: en Toe debe anularse"
assert d_dn.max() > 100, "sin Δn el residuo llega a cientos de m"
assert d_2c.max() > 100, "la elipse pura se despega cientos de m en el arco"
print("OK: la broadcast es un kepleriano parcheado — y medimos los parches")
