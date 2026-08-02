#!/usr/bin/env python3
"""Solución 6.3 — Anatomía de un spoofing en la adquisición.

Reproduce la firma de un ataque de spoofing sobre la función de ambigüedad
(CAF): además del pico auténtico aparece un SEGUNDO pico (el falso), más
fuerte, que "arrastra" al correlador. Núcleo sintético reproducible sobre
el código C/A real de la clase 2.1; el escenario TEXBAT real se baja aparte
(ver README §4). Correr: python3 lab_spoofing_solucion.py → "SPOOFING OK".
"""
import json
import sys
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[4].parent
sys.path.insert(0, str(RAIZ / "clases/mod2-senales/clase2.1-codigos/lab/soluciones"))
from lab_codigos_solucion import chips  # noqa: E402  (±1 del código C/A)

FS_CHIP = 1                      # 1 muestra por chip (adquisición en chips)
CODE_LEN = 1023


def escenario(prn=1, delay_auth=100, delay_spoof=140,
              amp_auth=1.0, amp_spoof=1.6, ruido=0.7, seed=42):
    """Señal = código auténtico (delay_auth) + copia spoofeada (delay_spoof,
    más fuerte) + ruido. Devuelve la CAF (correlación con la réplica limpia)."""
    rng = np.random.default_rng(seed)
    c = chips(prn).astype(float)
    señal = (amp_auth * np.roll(c, delay_auth) +
             amp_spoof * np.roll(c, delay_spoof) +
             rng.normal(0, ruido, CODE_LEN))
    # adquisición: correlación circular con la réplica local
    R = np.fft.ifft(np.fft.fft(señal) * np.conj(np.fft.fft(c))).real
    return R / CODE_LEN


def picos(caf, k=2):
    """Índices de los k picos más altos, separados > 3 chips."""
    orden = np.argsort(caf)[::-1]
    sel = []
    for i in orden:
        if all(abs(i - j) > 3 for j in sel):
            sel.append(int(i))
        if len(sel) == k:
            break
    return sel


def main() -> int:
    limpio = escenario(amp_spoof=0.0)               # solo auténtico
    atacado = escenario()                            # auténtico + spoofer

    p_limpio = picos(limpio, k=2)
    p_atacado = picos(atacado, k=2)
    v_limpio = sorted(limpio[p_limpio], reverse=True)
    v_atacado = sorted(atacado[p_atacado], reverse=True)

    # ¿el segundo pico sobresale del ruido? (firma de spoofing)
    piso = np.median(np.abs(atacado))
    doble = v_atacado[1] > 5 * piso

    print(f"[A] limpio: 1 pico dominante en chip {p_limpio[0]} "
          f"(2º/1º = {v_limpio[1]/v_limpio[0]:.2f}, o sea ruido)")
    print(f"[B] atacado: DOS picos — auténtico y falso")
    print(f"      picos en chips {sorted(p_atacado)}  "
          f"alturas {v_atacado[0]:.2f} y {v_atacado[1]:.2f}")
    print(f"[C] el pico spoofeado es {v_atacado[0]/v_atacado[1]:.2f}× el auténtico "
          f"→ el correlador lo prefiere y engancha la posición FALSA")
    print(f"[D] firma de spoofing (2º pico sobre el ruido): {'SÍ' if doble else 'no'}")

    dest = RAIZ / "clases/mod6-seguridad/clase6.3-spoofing/data"
    dest.mkdir(parents=True, exist_ok=True)
    json.dump({"caf_limpio": limpio.tolist(), "caf_atacado": atacado.tolist(),
               "picos_atacado": sorted(p_atacado), "razon": v_atacado[0]/v_atacado[1],
               "doble_pico": bool(doble)}, open(dest / "resultados_6_3.json", "w"))

    assert len(p_atacado) == 2 and doble, "debería haber doble pico"
    assert v_limpio[1] / v_limpio[0] < 0.3, "el limpio debería tener un solo pico"
    print("\nSPOOFING OK: el doble pico en la CAF es la firma del ataque")
    return 0


if __name__ == "__main__":
    sys.exit(main())
