# %% [markdown]
# # Constelaciones — Lab: censo y comparación orbital multi-GNSS (ESQUELETO)
#
# Completá los `TODO` en orden; los auto-tests validan contra el día de
# referencia 2026-06-15. Correr desde la raíz del repo (requiere
# `data/raw/2026/166`, clase 0.4):
#
#     python3 clases/mod0-prerrequisitos/constelaciones/lab/lab_constelaciones_TODO.py

# %%
from collections import defaultdict
from pathlib import Path

MU = 3.986004418e14
RE = 6371.0
NAV = Path("data/raw/2026/166/BRDC00IGS_R_20261660000_01D_MN.rnx")
NOMBRES = {"G": "GPS", "E": "Galileo", "R": "GLONASS", "C": "BeiDou",
           "J": "QZSS", "I": "NavIC", "S": "SBAS"}
LINEAS = NAV.read_text().splitlines()

# %% [markdown]
# ## TODO 1 — censo de SATÉLITES únicos por constelación
#
# En la clase 0.4 contaste *efemérides* (registros); acá contá *satélites*
# (SV únicos). Cabecera de registro: letra de constelación + 2 dígitos.

# %%
def censo_svs():
    svs = defaultdict(set)
    for l in LINEAS:
        # TODO 1: detectá cabeceras y agregá el SV (p.ej. 'E12') a svs[letra]
        ...
    return svs


SVS = censo_svs()
for c in sorted(SVS):
    print(f"  {NOMBRES[c]:8s} {len(SVS[c]):3d} satélites")
assert len(SVS["G"]) == 32, f"GPS: esperaba 32, tenés {len(SVS.get('G', ()))}"
assert len(SVS["E"]) == 30 and len(SVS["R"]) == 27
assert len(SVS["C"]) == 37, "BeiDou trae MEO+IGSO+GEO en el nav (37)"
print("TODO 1 OK")

# %% [markdown]
# ## TODO 2 — semieje mayor por constelación (de las efemérides keplerianas)
#
# Para G/E/C/J: el campo `sqrtA` es el **4º valor de la línea 3** del
# registro (campos de 19 chars desde la columna 4). a = sqrtA² (en m).
# Devolvé la MEDIANA de a[km] por constelación (BeiDou mezcla órbitas:
# la mediana cae en los MEO).

# %%
def campo(i, fila, k):
    s = LINEAS[i + fila][4 + 19 * k: 4 + 19 * (k + 1)]
    return float(s.replace("D", "E").replace("d", "e"))


def a_por_constelacion():
    aes = defaultdict(dict)
    for i, l in enumerate(LINEAS):
        if l[:1] in "GEC" and l[1:3].isdigit() and l[:3] not in aes[l[0]]:
            # TODO 2: leé sqrtA con campo(i, 2, 3) y guardá a[km] del SV
            ...
    med = {}
    for c, d in aes.items():
        vals = sorted(d.values())
        med[c] = vals[len(vals) // 2]
    return med


A = a_por_constelacion()
print({NOMBRES[c]: round(a) for c, a in A.items()})
assert abs(A["G"] - 26560) < 30 and abs(A["E"] - 29600) < 30
assert 27800 < A["C"] < 28000
print("TODO 2 OK")

# %% [markdown]
# ## TODO 3 — GLONASS: el formato delata el diseño
#
# Un registro GLONASS NO tiene sqrtA: trae **vectores de estado**
# (x, y, z en km en el primer campo de las líneas 1, 2 y 3). Calculá
# |r| de la primera efeméride de cada SV y quedate con la mediana.

# %%
def r_glonass():
    rs = {}
    for i, l in enumerate(LINEAS):
        if l[:1] == "R" and l[1:3].isdigit() and l[:3] not in rs:
            # TODO 3: x=campo(i,1,0), y=campo(i,2,0), z=campo(i,3,0) -> |r|
            ...
    vals = sorted(rs.values())
    return vals[len(vals) // 2]


RG = r_glonass()
print(f"  GLONASS |r| mediana: {RG:.0f} km")
assert abs(RG - 25500) < 150
print("TODO 3 OK")

# %% [markdown]
# ## TODO 4 — la tabla comparada: períodos y alturas
#
# T = 2π·√(a³/μ) (clase 0.3). Armá la tabla GPS/Galileo/GLONASS/BeiDou
# con a, T[h] y altura (a − R⊕) y verificá los períodos.

# %%
import math
tabla = {}
for nombre, a_km in [("GPS", A["G"]), ("Galileo", A["E"]),
                     ("GLONASS", RG), ("BeiDou", A["C"])]:
    # TODO 4: calculá T_h y altura y guardá (a_km, T_h, altura)
    ...
for n, (a, T, h) in tabla.items():
    print(f"  {n:8s} a={a:6.0f} km  T={T:5.2f} h  h={h:6.0f} km")
assert abs(tabla["GPS"][1] - 11.97) < 0.05
assert abs(tabla["Galileo"][1] - 14.08) < 0.05
assert abs(tabla["GLONASS"][1] - 11.26) < 0.05
print("TODO 4 OK")

# %% [markdown]
# Las cuatro vuelan distinto a propósito: períodos que no resuenan igual
# con la rotación terrestre (clase 0.3, ground tracks) y alturas que
# cambian la geometría. Anotá tus números en `bitacora.md`.

# %%
print("LISTO: lab constelaciones completo")
