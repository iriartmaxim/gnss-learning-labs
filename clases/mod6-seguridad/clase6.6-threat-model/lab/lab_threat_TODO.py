# %% [markdown]
# # Lab 6.6 — Threat model como matriz verificable (ESQUELETO)
#
# Completá los chequeos de coherencia de la matriz ataque × defensa.
# El análisis (residuos) ya está en la solución; acá validás la lógica.
#
#     python3 clases/mod6-seguridad/clase6.6-threat-model/lab/lab_threat_TODO.py

# %%
import sys
from pathlib import Path
RAIZ = Path(__file__).resolve().parents[4].parent
sys.path.insert(0, str(RAIZ / "clases/mod6-seguridad/clase6.6-threat-model/lab/soluciones"))
from lab_threat_solucion import AMENAZAS, CAPAS

# %% [markdown]
# ## TODO 1 — validar que ningún ataque queda sin defensa
# Para cada ataque, alguna capa debe mitigarlo. Y OSNMA NO debe figurar como
# cobertura de los ataques de RANGO (autentica datos, no rango).

# %%
def validar(amenazas):
    problemas = []
    for ataque, fila in amenazas.items():
        # TODO 1a: cubierto = any(fila[c] for c in CAPAS) ; si no, agregá problema
        ...
    rango = ["spoofing de rango (señal falsa alineada)", "replay / meaconing (dentro de la ventana)"]
    for a in rango:
        # TODO 1b: si amenazas[a]["OSNMA"] es True → problema conceptual
        ...
    return problemas

# %%
problemas = validar(AMENAZAS)
cob = {c: sum(1 for f in AMENAZAS.values() if f.get(c)) for c in CAPAS}
print("cobertura por capa:", cob)
assert not problemas, problemas
assert cob["detectores_6.4"] == len(AMENAZAS)
assert not AMENAZAS["spoofing de rango (señal falsa alineada)"]["OSNMA"]
print("THREAT MODEL OK")
print("LISTO: 6.6")
