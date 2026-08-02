# %% [markdown]
# # Lab 6.1 — Las tres primitivas de OSNMA (ESQUELETO)
#
# TESLA (claves encadenadas por hash), Merkle (prueba de inclusión) y ECDSA
# P-256 (firma del KROOT). Vectores autogenerados y reproducibles. Completá
# los TODO; los asserts validan cada primitiva. Usa la librería cryptography.
#
#     python3 clases/mod6-seguridad/clase6.1-osnma/lab/lab_osnma_TODO.py

# %%
import hashlib, hmac, os, sys
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import Prehashed

# %% [markdown]
# ## TODO 1 — cadena TESLA
# K[i] = H(K[i+1]); la KROOT es K[0]. Verificar una clave revelada = hashearla
# 'indice' veces y comparar con la KROOT.

# %%
def construir_cadena_tesla(semilla, n):
    claves = [b""]*n; claves[-1] = semilla
    for i in range(n-2, -1, -1):
        # TODO 1a: claves[i] = sha256(claves[i+1])
        ...
    return claves

def verificar_clave_tesla(kroot, clave, indice):
    x = clave
    # TODO 1b: hashear 'indice' veces y comparar con kroot (hmac.compare_digest)
    ...

# %% [markdown]
# ## TODO 2 — Merkle: verificar inclusión
# Reconstruir la raíz desde la hoja y el camino de hermanos.

# %%
def _h(b): return hashlib.sha256(b).digest()

def construir_merkle(hojas):
    nivel = [_h(x) for x in hojas]; niveles=[nivel]
    while len(nivel) > 1:
        if len(nivel)%2: nivel = nivel+[nivel[-1]]
        nivel = [_h(nivel[i]+nivel[i+1]) for i in range(0,len(nivel),2)]
        niveles.append(nivel)
    return nivel[0], niveles

def prueba_inclusion(niveles, idx):
    camino=[]
    for nivel in niveles[:-1]:
        j = idx^1
        if j>=len(nivel): j=idx
        camino.append((nivel[j], idx&1)); idx//=2
    return camino

def verificar_inclusion(hoja, camino, raiz):
    x = _h(hoja)
    for hermano, soy_derecha in camino:
        # TODO 2: x = _h(hermano+x) si soy_derecha, si no _h(x+hermano)
        ...
    return hmac.compare_digest(x, raiz)

# %% [markdown]
# ## TODO 3 — ECDSA P-256: verificar la firma del KROOT

# %%
def verificar_firma_kroot(clave_pub, kroot, firma):
    dig = hashlib.sha256(kroot).digest()
    try:
        # TODO 3: clave_pub.verify(firma, dig, ec.ECDSA(Prehashed(hashes.SHA256())))
        ...
        return True
    except Exception:
        return False

# %%
cadena = construir_cadena_tesla(os.urandom(32), 50); kroot = cadena[0]
assert verificar_clave_tesla(kroot, cadena[7], 7)
assert not verificar_clave_tesla(kroot, os.urandom(32), 7)
hojas = [f"pk_{i}".encode() for i in range(8)]; raiz, niv = construir_merkle(hojas)
assert verificar_inclusion(hojas[3], prueba_inclusion(niv, 3), raiz)
priv = ec.generate_private_key(ec.SECP256R1()); pub = priv.public_key()
firma = priv.sign(hashlib.sha256(kroot).digest(), ec.ECDSA(Prehashed(hashes.SHA256())))
assert verificar_firma_kroot(pub, kroot, firma)
print("OSNMA PRIMITIVAS OK: TESLA + Merkle + ECDSA")
print("LISTO: 6.1")
