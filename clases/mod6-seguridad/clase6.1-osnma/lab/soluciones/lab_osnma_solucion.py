#!/usr/bin/env python3
"""Solución 6.1 — Las tres primitivas criptográficas de OSNMA.

OSNMA (autenticación del mensaje de navegación de Galileo) se apoya en tres
piezas. Acá las implementamos y verificamos con vectores autogenerados
(reproducibles), que es la forma correcta de entender el mecanismo antes de
correrlo contra el feed real (clase 6.2):

  1. Cadena TESLA  — claves encadenadas por hash, reveladas con retardo.
  2. Árbol de Merkle — prueba de inclusión contra una raíz embebida.
  3. Firma ECDSA P-256 — autentica la raíz de la cadena (DSM-KROOT).

Correr:  python3 lab_osnma_solucion.py   → "OSNMA PRIMITIVAS OK".
"""
import hashlib
import hmac
import sys

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import Prehashed


# ---------------------------------------------------------------------------
# 1) CADENA TESLA — claves encadenadas hacia atrás por hash
# ---------------------------------------------------------------------------
def construir_cadena_tesla(semilla: bytes, n: int):
    """Genera una cadena TESLA de n claves: K[i] = H(K[i+1]).

    La KROOT es K[0]. Las claves se REVELAN en orden K[1], K[2], ...; cada
    una se verifica hasheándola hasta llegar a la KROOT ya conocida.
    """
    claves = [b""] * n
    claves[-1] = semilla
    for i in range(n - 2, -1, -1):
        claves[i] = hashlib.sha256(claves[i + 1]).digest()
    return claves


def verificar_clave_tesla(kroot: bytes, clave: bytes, indice: int) -> bool:
    """Verifica que 'clave' (revelada en posición 'indice') pertenece a la
    cadena cuya raíz es kroot: hashear 'indice' veces debe dar la KROOT."""
    x = clave
    for _ in range(indice):
        x = hashlib.sha256(x).digest()
    return hmac.compare_digest(x, kroot)


def tag_tesla(clave: bytes, datos_nav: bytes) -> bytes:
    """Tag de autenticación (MAC) de los datos de navegación con la clave
    TESLA de esa época (HMAC-SHA256, truncado como en OSNMA)."""
    return hmac.new(clave, datos_nav, hashlib.sha256).digest()[:10]


# ---------------------------------------------------------------------------
# 2) ÁRBOL DE MERKLE — prueba de inclusión contra la raíz embebida
# ---------------------------------------------------------------------------
def _h(b: bytes) -> bytes:
    return hashlib.sha256(b).digest()


def construir_merkle(hojas: list[bytes]):
    """Devuelve (raíz, niveles) de un árbol de Merkle binario."""
    nivel = [_h(x) for x in hojas]
    niveles = [nivel]
    while len(nivel) > 1:
        if len(nivel) % 2:
            nivel = nivel + [nivel[-1]]           # duplicar el último si impar
        nivel = [_h(nivel[i] + nivel[i + 1]) for i in range(0, len(nivel), 2)]
        niveles.append(nivel)
    return nivel[0], niveles


def prueba_inclusion(niveles, idx: int):
    """Camino de hashes hermanos para probar la hoja idx."""
    camino = []
    for nivel in niveles[:-1]:
        j = idx ^ 1                                # hermano
        if j >= len(nivel):
            j = idx                                # se duplicó
        camino.append((nivel[j], idx & 1))
        idx //= 2
    return camino


def verificar_inclusion(hoja: bytes, camino, raiz: bytes) -> bool:
    """Reconstruye la raíz desde la hoja y su camino; compara con la raíz."""
    x = _h(hoja)
    for hermano, soy_derecha in camino:
        x = _h(hermano + x) if soy_derecha else _h(x + hermano)
    return hmac.compare_digest(x, raiz)


# ---------------------------------------------------------------------------
# 3) FIRMA ECDSA P-256 — autentica el DSM-KROOT
# ---------------------------------------------------------------------------
def firmar_kroot(clave_priv, kroot: bytes) -> bytes:
    """La autoridad firma la KROOT con su clave privada P-256 (sobre SHA-256)."""
    dig = hashlib.sha256(kroot).digest()
    return clave_priv.sign(dig, ec.ECDSA(Prehashed(hashes.SHA256())))


def verificar_firma_kroot(clave_pub, kroot: bytes, firma: bytes) -> bool:
    """El receptor verifica la firma con la clave pública embebida."""
    dig = hashlib.sha256(kroot).digest()
    try:
        clave_pub.verify(firma, dig, ec.ECDSA(Prehashed(hashes.SHA256())))
        return True
    except Exception:
        return False


def main() -> int:
    ok = 0

    # === 1. TESLA ===========================================================
    import os
    cadena = construir_cadena_tesla(os.urandom(32), n=50)
    kroot = cadena[0]
    # el receptor conoce la KROOT; le revelan la clave 7 y la verifica
    assert verificar_clave_tesla(kroot, cadena[7], 7), "TESLA: clave válida rechazada"
    # una clave falsa NO debe verificar
    assert not verificar_clave_tesla(kroot, os.urandom(32), 7), "TESLA: aceptó clave falsa"
    # un tag autentica los datos SOLO con la clave correcta
    nav = b"efemeride Galileo E21 Toe=129600 ..."
    t = tag_tesla(cadena[7], nav)
    assert t == tag_tesla(cadena[7], nav), "TESLA: tag no determinista"
    assert t != tag_tesla(cadena[8], nav), "TESLA: distinta clave, mismo tag?!"
    print("[1] TESLA: cadena por hash, revelación diferida y tag — OK"); ok += 1

    # === 2. MERKLE ==========================================================
    hojas = [f"pubkey_chain_{i}".encode() for i in range(8)]
    raiz, niveles = construir_merkle(hojas)
    for idx in (0, 3, 7):
        camino = prueba_inclusion(niveles, idx)
        assert verificar_inclusion(hojas[idx], camino, raiz), f"Merkle: hoja {idx} falló"
    # una hoja falsa no debe incluirse
    assert not verificar_inclusion(b"pubkey_falsa", prueba_inclusion(niveles, 3), raiz)
    print("[2] MERKLE: prueba de inclusión contra la raíz embebida — OK"); ok += 1

    # === 3. ECDSA P-256 =====================================================
    priv = ec.generate_private_key(ec.SECP256R1())
    pub = priv.public_key()
    firma = firmar_kroot(priv, kroot)
    assert verificar_firma_kroot(pub, kroot, firma), "ECDSA: firma válida rechazada"
    assert not verificar_firma_kroot(pub, b"kroot_falsa" + kroot[11:], firma), \
        "ECDSA: aceptó KROOT alterada"
    print("[3] ECDSA P-256: firma del DSM-KROOT — OK"); ok += 1

    # === cadena de confianza completa (mini end-to-end) =====================
    #  raíz Merkle → (clave pública incluida) → firma KROOT → TESLA → tag datos
    assert verificar_inclusion(hojas[2], prueba_inclusion(niveles, 2), raiz)
    assert verificar_firma_kroot(pub, kroot, firma)
    assert verificar_clave_tesla(kroot, cadena[7], 7)
    assert tag_tesla(cadena[7], nav) == t
    print("[4] cadena de confianza Merkle→ECDSA→TESLA→tag — OK"); ok += 1

    print(f"\nOSNMA PRIMITIVAS OK: {ok}/4 bloques verificados")
    return 0


if __name__ == "__main__":
    sys.exit(main())
