# %% [markdown]
# # Visión global — Lab: el arco GNSS en tu disco (ESQUELETO)
#
# La idea: si entendés el arco señal → observables → mensaje → verdad →
# solución, tenés el mapa de TODO el path. Este lab lo comprueba con los
# archivos reales que ya bajaste y produjiste. Correr desde la raíz:
#
#     python3 clases/mod0-prerrequisitos/vision-global/lab/lab_vision_TODO.py

# %%
from pathlib import Path

# %% [markdown]
# ## TODO 1 — el mapa etapa → huella en disco
#
# Completá los patrones glob de cada etapa (mirá qué hay en `data/raw/`
# y en `clases/*/*/data/`). Pista: IQ = .dat, obs = *_MO.rnx,
# nav = BRDC*_MN.rnx, precisos = *ORB.SP3 y *CLK.CLK,
# productos = resultados_*.json.

# %%
ETAPAS = [
    ("SEÑAL (muestras IQ crudas)",     "clase 2.2",        [...]),   # TODO 1
    ("OBSERVABLES (RINEX obs)",        "clase 1.5",        [...]),
    ("MENSAJE / ÓRBITAS broadcast",    "clase 1.3",        [...]),
    ("VERDAD PRECISA (SP3 + CLK)",     "clases 1.3/4.x",   [...]),
    ("SOLUCIÓN Y ERRORES (productos)", "labs 1.5/3.x/4.1", [...]),
]

# %% [markdown]
# ## TODO 2 — inventario: archivos y MB por etapa

# %%
def inventario():
    filas = []
    for nombre, clase, patrones in ETAPAS:
        # TODO 2: juntá los archivos de todos los patrones (Path('.').glob)
        # y calculá los MB totales de la etapa
        archivos, mb = ..., ...
        filas.append((nombre, clase, archivos, mb))
    return filas

# %% [markdown]
# ## TODO 3 — imprimir el arco con TUS archivos (hasta 4 por etapa)

# %%
for nombre, clase, archivos, mb in inventario():
    # TODO 3: imprimí etapa, clase que la trabaja, cantidad y algunos nombres
    ...

# %% [markdown]
# ## TODO 4 — el chequeo: ¿está completo el arco?

# %%
filas = inventario()
vacias = [n for n, _, a, _ in filas if not a]
assert not vacias, f"etapas sin archivos: {vacias}"
assert sum(len(a) for _, _, a, _ in filas) >= 15
print("ARCO COMPLETO: las 5 etapas tienen datos reales en tu máquina")
