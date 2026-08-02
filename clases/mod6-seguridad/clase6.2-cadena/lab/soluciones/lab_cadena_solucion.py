#!/usr/bin/env python3
"""Solución 6.2 — La cadena de confianza OSNMA de punta a punta.

Encadena las tres primitivas de 6.1 en el flujo operativo real: raíz de
Merkle (embebida) → clave pública → firma del KROOT → claves TESLA reveladas
época a época → tags que autentican los datos de navegación. Simula un
stream de subframes (reproducible) y verifica frame a frame, incluyendo un
frame manipulado que DEBE fallar. El feed real (galmon) se conecta aparte
(README §4). Correr: python3 lab_cadena_solucion.py → "CADENA OSNMA OK".
"""
import hashlib
import hmac
import os
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[4].parent
sys.path.insert(0, str(RAIZ / "clases/mod6-seguridad/clase6.1-osnma/lab/soluciones"))
from cryptography.hazmat.primitives import hashes, serialization  # noqa: E402
from cryptography.hazmat.primitives.asymmetric import ec  # noqa: E402
from cryptography.hazmat.primitives.asymmetric.utils import Prehashed  # noqa: E402
from lab_osnma_solucion import (  # noqa: E402
    construir_cadena_tesla, verificar_clave_tesla, tag_tesla,
    construir_merkle, prueba_inclusion, verificar_inclusion,
    firmar_kroot, verificar_firma_kroot)


def montar_infraestructura(n_epocas=20):
    """Lo que hace el sistema Galileo (una vez): árbol de claves, cadena
    TESLA, KROOT firmado. Devuelve lo que el receptor recibe/embebe."""
    # árbol de Merkle de claves públicas (una activa)
    priv = ec.generate_private_key(ec.SECP256R1())
    pub = priv.public_key()
    pub_bytes = pub.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo)
    hojas = [pub_bytes] + [f"otra_pk_{i}".encode() for i in range(7)]
    raiz, niveles = construir_merkle(hojas)
    # cadena TESLA y firma del KROOT
    cadena = construir_cadena_tesla(os.urandom(32), n=n_epocas + 1)
    kroot = cadena[0]
    firma = firmar_kroot(priv, kroot)
    return dict(raiz=raiz, niveles=niveles, hojas=hojas, pub=pub, pub_bytes=pub_bytes,
                cadena=cadena, kroot=kroot, firma=firma)


def emitir_stream(infra, n):
    """Genera n subframes: (época, datos_nav, tag) con la clave TESLA de cada
    época. La clave se 'revela' en el subframe SIGUIENTE (revelación diferida)."""
    stream = []
    for e in range(1, n + 1):
        nav = f"E21 Toe={129600+e*600} af0=-7.5e-4 sqrtA=5440.6".encode()
        tag = tag_tesla(infra["cadena"][e], nav)
        stream.append((e, nav, tag))
    return stream


def receptor_verifica(infra, stream, tamper_en=None):
    """Verifica la cadena completa como un receptor OSNMA."""
    # 1) la clave pública activa está en el árbol (contra la raíz embebida)
    idx = 0
    if not verificar_inclusion(infra["hojas"][idx], prueba_inclusion(infra["niveles"], idx), infra["raiz"]):
        return "FALLA: pubkey no incluida en Merkle"
    # 2) la firma del KROOT valida con esa pública
    if not verificar_firma_kroot(infra["pub"], infra["kroot"], infra["firma"]):
        return "FALLA: firma del KROOT inválida"
    # 3) frame a frame: la clave TESLA revelada pertenece a la cadena y el tag cierra
    autenticados, rechazados = 0, 0
    for (e, nav, tag) in stream:
        clave = infra["cadena"][e]                       # revelada en e+1
        if not verificar_clave_tesla(infra["kroot"], clave, e):
            rechazados += 1; continue
        datos = nav
        if tamper_en == e:                               # atacante altera los datos
            datos = nav.replace(b"af0=-7.5e-4", b"af0=+9.9e-3")
        if hmac.compare_digest(tag_tesla(clave, datos), tag):
            autenticados += 1
        else:
            rechazados += 1
    return autenticados, rechazados


def main() -> int:
    infra = montar_infraestructura(n_epocas=20)
    stream = emitir_stream(infra, 20)

    # caso limpio: todo autentica
    aut, rec = receptor_verifica(infra, stream)
    print(f"[A] cadena Merkle→ECDSA→TESLA→tags verificada")
    print(f"[B] stream limpio: {aut} subframes autenticados, {rec} rechazados")

    # caso atacado: un frame con datos alterados debe fallar el tag
    aut2, rec2 = receptor_verifica(infra, stream, tamper_en=10)
    print(f"[C] stream con 1 frame manipulado (época 10): "
          f"{aut2} autenticados, {rec2} rechazado(s)")
    print(f"[D] el frame alterado NO autentica → OSNMA lo detecta")

    # relevo de cadena (Chain ID): una clave falsa no verifica contra la KROOT
    from os import urandom
    falsa_ok = verificar_clave_tesla(infra["kroot"], urandom(32), 5)
    print(f"[E] clave TESLA falsa contra la KROOT: {'aceptada (MAL)' if falsa_ok else 'rechazada (OK)'}")

    assert (aut, rec) == (20, 0), "el stream limpio debería autenticar todo"
    assert aut2 == 19 and rec2 == 1, "el frame manipulado debía ser el único rechazado"
    assert not falsa_ok
    print("\nCADENA OSNMA OK: autentica lo legítimo y rechaza lo alterado")
    return 0


if __name__ == "__main__":
    sys.exit(main())
