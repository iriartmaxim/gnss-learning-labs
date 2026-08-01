# %% [markdown]
# # Lab-lite — mapear tus datos al arco señal→observable→órbita (ESQUELETO)
#
# No hay número que calcular: el ejercicio es **reconocer** qué eslabón
# del arco alimenta cada archivo que bajaste en la clase 0.4. Completá el
# TODO y el auto-test confirma tu mapeo.
#
# Correr desde la raíz del repo:
#
#     python3 clases/mod0-prerrequisitos/vision-global/lab/lab_arco_TODO.py

# %%
import sys
from pathlib import Path

# %% [markdown]
# ## TODO 1 — clasificá cada tipo de archivo
#
# Completá la función devolviendo el eslabón del arco según el nombre:
# - `.dat` (capturas IQ) → **señal**
# - `..._MO.rnx` (observación) → **observable**
# - `...ORB.SP3` (órbita precisa) → **órbita (precisa)**
# - `...CLK.CLK` (relojes) → **error/reloj**
# - `..._MN.rnx` (navegación broadcast) → **órbita (broadcast)**

# %%
def clasificar(nombre):
    n = nombre.upper()
    # TODO 1: devolvé una tupla (eslabon, clase_que_lo_usa) por cada tipo.
    ...


raiz = Path("data/raw")
archivos = sorted(p.name for p in raiz.rglob("*") if p.is_file()) if raiz.exists() else []
conteo = {}
for a in archivos:
    eslabon, clase = clasificar(a)
    conteo[eslabon] = conteo.get(eslabon, 0) + 1
    print(f"  {a:48s} -> {eslabon:20s} [{clase}]")

esperados = {"señal", "observable", "órbita (broadcast)", "órbita (precisa)", "error/reloj"}
assert not (esperados - set(conteo)), f"faltan eslabones: {esperados - set(conteo)}"
print("\nMAPEO OK: reconociste el arco en tus propios datos")

# %%
print("LISTO: lab-lite de visión global completo")
