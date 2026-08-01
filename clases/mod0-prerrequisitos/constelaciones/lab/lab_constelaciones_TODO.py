# %% [markdown]
# # Lab — censo comparado de constelaciones (ESQUELETO)
#
# Contá los satélites de cada sistema en el BRDC real del día 166 y
# contrastalos con su capacidad nominal. Completá los TODO; los
# auto-tests validan contra el archivo real.
#
# Correr desde la raíz del repo (requiere data/raw/2026/166):
#
#     python3 clases/mod0-prerrequisitos/constelaciones/lab/lab_constelaciones_TODO.py

# %%
import sys
from collections import defaultdict
from pathlib import Path

NAV = "data/raw/2026/166/BRDC00IGS_R_20261660000_01D_MN.rnx"
FICHA = {"G": "GPS", "R": "GLONASS", "E": "Galileo", "C": "BeiDou",
         "J": "QZSS", "I": "NavIC", "S": "SBAS"}

# %% [markdown]
# ## TODO 1 — contar SVs únicos por constelación
#
# En RINEX nav, cada efeméride abre con `Xnn ...` (X = constelación, nn =
# número). El mismo satélite aparece muchas veces (re-emite): guardá los
# **IDs únicos** en un set por constelación.

# %%
def svs_por_constelacion(nav):
    vistos = defaultdict(set)
    with open(nav) as f:
        for linea in f:
            # TODO 1: si es cabecera (linea[:1] en FICHA y linea[1:3] dígitos),
            # agregá linea[:3] al set de esa constelación.
            ...
    return vistos


vistos = svs_por_constelacion(Path(NAV))
for c in ("G", "R", "E", "C", "J", "I", "S"):
    print(f"  {FICHA[c]:9s} {len(vistos.get(c, ())):3d} SVs")

# %% [markdown]
# ## TODO 2 — sumar los sistemas globales
#
# GPS, GLONASS, Galileo y BeiDou son **globales**; QZSS/NavIC son
# regionales y SBAS es aumentación. Sumá solo los cuatro globales.

# %%
# TODO 2: globales = suma de SVs de G, R, E, C.
globales = ...
print(f"\nSVs globales (G+R+E+C): {globales}")

assert len(vistos["G"]) == 32 and len(vistos["E"]) == 30, "revisá el conteo GPS/Galileo"
assert globales == 126, f"globales esperados 126, tenés {globales}"
print("CENSO OK: G32 · R27 · E30 · C37 · globales 126")

# %%
print("LISTO: censo de constelaciones completo")
