# %% [markdown]
# # Clase 0.4 — Lab: censo y cruce de datos GNSS reales (ESQUELETO)
#
# Completá los `TODO` en orden. Cada bloque tiene **auto-tests** contra el
# día de referencia 2026-06-15 (DOY 166): si pasan, seguí; si no, revisá
# el formato en el README §3. No abras la solución antes de intentarlo.
#
# Correr desde la raíz del repo (con `data/raw/2026/166` ya bajado por
# `tools/fetch_data.py`, ver clase 0.4 §5):
#
#     python3 clases/mod0-prerrequisitos/clase0.4-pipeline-datos/lab/lab_pipeline_TODO.py

# %%
import sys
from collections import Counter
from pathlib import Path

CARPETA = Path(sys.argv[1] if len(sys.argv) > 1 else "data/raw/2026/166")
NAV = next(CARPETA.glob("BRDC*_MN.rnx"))
SP3 = next(CARPETA.glob("*ORB.SP3"))
NOMBRES = {"G": "GPS", "E": "Galileo", "R": "GLONASS", "C": "BeiDou",
           "J": "QZSS", "I": "NavIC", "S": "SBAS"}
ES_REF = CARPETA.as_posix().rstrip("/").endswith("2026/166")
print(f"nav: {NAV.name}\nsp3: {SP3.name}")

# %% [markdown]
# ## TODO 1 — censo del RINEX nav crudo
#
# En RINEX 3 nav, cada efeméride empieza con una línea de cabecera
# `Xnn AAAA MM DD hh mm ss ...` (X = letra de constelación, nn = número
# de satélite). Las líneas siguientes (parámetros) empiezan con espacios.
# Contá efemérides por constelación **sin librerías**, leyendo línea por
# línea, y juntá el set de SV Galileo únicos (`'E02'`, `'E03'`, ...).

# %%
def censo_nav(nav):
    """Devuelve (Counter por letra de constelación, set de SV Galileo)."""
    con, sv_gal = Counter(), set()
    with open(nav) as f:
        for linea in f:
            # TODO 1: detectá la línea de cabecera (pista: linea[:1] y
            # linea[1:3]), sumá en `con` y agregá los Galileo a `sv_gal`.
            ...
    return con, sv_gal


CON, SV_GAL = censo_nav(NAV)
for c in sorted(CON):
    print(f"  {NOMBRES[c]:8s} {CON[c]:6d} efemerides")
if ES_REF:
    assert CON["G"] == 450, f"GPS: esperaba 450, tenés {CON.get('G')}"
    assert CON["E"] == 11119, f"Galileo: esperaba 11119, tenés {CON.get('E')}"
    assert CON["C"] == 901, f"BeiDou: esperaba 901, tenés {CON.get('C')}"
    assert len(SV_GAL) == 30, f"SV Galileo únicos: esperaba 30, tenés {len(SV_GAL)}"
print("TODO 1 OK")

# %% [markdown]
# ## TODO 2 — satélites del header SP3
#
# El header SP3 declara los satélites en líneas que empiezan con `'+ '`:
# los IDs viven en las columnas 10–60, en grupos de 3 caracteres. La
# sección termina donde empiezan las líneas `'++'` (precisiones).

# %%
def sats_sp3(sp3):
    """Lista de IDs ('G01', 'E02', ...) declarados en el header."""
    sats = []
    for linea in open(sp3):
        # TODO 2: juntá los IDs de las líneas '+ ' y cortá en '++'.
        ...
    return [s for s in sats if s[:1] in NOMBRES]


SATS = sats_sp3(SP3)
CSP3 = Counter(s[0] for s in SATS)
print(f"  {len(SATS)} satelites: "
      + ", ".join(f"{NOMBRES[c]} {n}" for c, n in sorted(CSP3.items())))
if ES_REF:
    assert len(SATS) == 116, f"esperaba 116 satélites, tenés {len(SATS)}"
    assert CSP3["E"] == 30, f"Galileo en SP3: esperaba 30, tenés {CSP3.get('E')}"
print("TODO 2 OK")

# %% [markdown]
# ## TODO 3 — cruce nav ∩ SP3
#
# Dos fuentes independientes (BKG compila lo que emiten los satélites;
# CODE calcula órbitas con una red global) describen la MISMA
# constelación. Cruzá los Galileo de ambas.

# %%
# TODO 3: armá el set de Galileo del SP3 e intersecalo con SV_GAL.
GAL_SP3 = ...
INTER = ...
print(f"  cruce Galileo nav∩SP3: {len(INTER)} en comun")
if ES_REF:
    assert len(INTER) == 30 and SV_GAL == GAL_SP3, \
        f"esperaba 30 y sin diferencias; dif = {sorted(SV_GAL ^ GAL_SP3)}"
print("TODO 3 OK")

# %% [markdown]
# ## TODO 4 — tasa de re-emisión
#
# GPS emite una efeméride nueva cada 2 h; Galileo re-emite cada ~10 min
# y por varios canales (I/NAV en E1/E5b, F/NAV en E5a). Calculá cuántas
# efemérides por satélite y por día guarda el BRDC mixto, y cada cuántos
# minutos equivale.

# %%
for c in ("G", "E"):
    # TODO 4: tasa = efemérides / satélites (usá CON y CSP3); minutos = 1440/tasa.
    tasa = ...
    print(f"  {NOMBRES[c]:8s} {tasa:6.1f} efem por sat/dia "
          f"(una cada {1440/tasa:4.0f} min)")
if ES_REF:
    assert 10 <= CON["G"] / CSP3["G"] <= 20, "GPS: esperaba ~14 efem/sat/día"
    assert 300 <= CON["E"] / CSP3["E"] <= 450, "Galileo: esperaba ~370 efem/sat/día"
print("TODO 4 OK")

# %% [markdown]
# Si llegaste acá con los 4 TODO en verde: el pipeline está entendido,
# no solo corrido. Anotá tus números en `bitacora.md` y contestá el
# Checkpoint del Módulo 0 (README §16) antes de saltar al módulo 1.

# %%
print("LISTO: lab 0.4 completo")
