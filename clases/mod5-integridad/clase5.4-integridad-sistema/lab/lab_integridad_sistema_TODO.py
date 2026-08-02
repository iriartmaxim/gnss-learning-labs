# %% [markdown]
# # Lab 5.4 — La cadena de integridad del sistema (ESQUELETO)
#
# Combiná RAIM + consistencia + OSNMA + física + tierra en un monitor único.
# Completá el TODO: la combinación debe cubrir escenarios que ninguna capa
# sola cubre.
#
#     python3 clases/mod5-integridad/clase5.4-integridad-sistema/lab/lab_integridad_sistema_TODO.py

# %%
import sys
from pathlib import Path
RAIZ = Path(__file__).resolve().parents[4].parent
sys.path.insert(0, str(RAIZ / "clases/mod5-integridad/clase5.4-integridad-sistema/lab/soluciones"))
from lab_integridad_sistema_solucion import ESCENARIOS, CAPAS

# %% [markdown]
# ## TODO 1 — el monitor combinado
# Alerta si ALGUNA capa activa detecta el escenario.

# %%
def monitor(flags, capas_activas):
    # TODO 1: return any(flags[c] for c in capas_activas)
    ...

# %%
solo = {c: sum(1 for e in ESCENARIOS.values() if e[c]) for c in CAPAS}
comb = sum(1 for e in ESCENARIOS.values() if monitor(e, CAPAS))
print("cobertura por capa sola:", solo)
print(f"combinadas: {comb}/{len(ESCENARIOS)}")
assert comb == len(ESCENARIOS) and max(solo.values()) < len(ESCENARIOS)
print("LISTO: integridad-sistema 5.4")
