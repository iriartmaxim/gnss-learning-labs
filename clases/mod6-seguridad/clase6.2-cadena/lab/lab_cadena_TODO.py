# %% [markdown]
# # Lab 6.2 — Cadena de confianza OSNMA de punta a punta (ESQUELETO)
#
# Encadená las primitivas de 6.1 en el flujo real y verificá un stream de
# subframes (incluido uno manipulado, que debe fallar). Completá los TODO.
#
#     python3 clases/mod6-seguridad/clase6.2-cadena/lab/lab_cadena_TODO.py

# %%
import hmac, sys
from pathlib import Path
RAIZ = Path(__file__).resolve().parents[4].parent
sys.path.insert(0, str(RAIZ / "clases/mod6-seguridad/clase6.1-osnma/lab/soluciones"))
sys.path.insert(0, str(RAIZ / "clases/mod6-seguridad/clase6.2-cadena/lab/soluciones"))
from lab_osnma_solucion import (verificar_clave_tesla, tag_tesla,
                                prueba_inclusion, verificar_inclusion, verificar_firma_kroot)
from lab_cadena_solucion import montar_infraestructura, emitir_stream

# %% [markdown]
# ## TODO 1 — verificar la cadena antes de confiar en un frame
# Orden: (1) pubkey incluida en Merkle, (2) firma del KROOT válida,
# (3) por frame: clave TESLA pertenece a la cadena y el tag cierra.

# %%
def verifica(infra, stream, tamper_en=None):
    if not verificar_inclusion(infra["hojas"][0], prueba_inclusion(infra["niveles"], 0), infra["raiz"]):
        return "FALLA Merkle"
    if not verificar_firma_kroot(infra["pub"], infra["kroot"], infra["firma"]):
        return "FALLA firma"
    aut = rec = 0
    for (e, nav, tag) in stream:
        clave = infra["cadena"][e]
        if not verificar_clave_tesla(infra["kroot"], clave, e):
            rec += 1; continue
        datos = nav.replace(b"af0=-7.5e-4", b"af0=+9.9e-3") if tamper_en == e else nav
        # TODO 1: si tag_tesla(clave, datos) == tag → aut += 1, si no rec += 1
        ...
    return aut, rec

# %%
infra = montar_infraestructura(20); stream = emitir_stream(infra, 20)
assert verifica(infra, stream) == (20, 0)
assert verifica(infra, stream, tamper_en=10) == (19, 1)
print("CADENA OSNMA OK: limpio 20/0, manipulado 19/1")
print("LISTO: cadena 6.2")
