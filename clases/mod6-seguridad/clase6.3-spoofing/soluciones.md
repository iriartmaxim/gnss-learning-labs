# Soluciones — Clase 6.3 (spoofing)

Núcleo sintético reproducible sobre el código C/A de 2.1. "SPOOFING OK".

## Lab

| Chequeo | Referencia |
|---|---|
| Limpio | 1 pico (2º/1º ≈ 0.11, ruido) |
| Atacado | 2 picos: auténtico (chip 100) y falso (chip 140) |
| Razón falso/auténtico | ~1.56× |
| Firma de doble pico | SÍ |

**TODO 1:** `señal = amp_auth*np.roll(c,delay_auth) + amp_spoof*np.roll(c,delay_spoof) + rng.normal(0,ruido,CODE_LEN)`.

**TEXBAT (escenario real):** el dataset clásico de spoofing (UT Austin) se
baja aparte (README §4). La firma es la misma que reproducís acá: un pico
falso que crece junto al auténtico y lo arrastra. La versión sintética es
100% reproducible; TEXBAT agrega realismo (dinámica, C/N0 real).

## E1 — por qué el falso debe ser más fuerte

El correlador engancha el pico más alto. Para "capturar" el lazo de
tracking sin que el receptor note un salto, el spoofer alinea su pico con
el auténtico y sube despacio la potencia hasta superarlo: se lleva el lazo
sin discontinuidad. Si fuera más débil, el receptor seguiría el auténtico.

## E2 — cómo se conecta con 6.4

El doble pico y el aumento de potencia del pico spoofeado son justo lo que
el detector de C/N0 (6.4) ve como salto anómalo. La adquisición muestra la
causa (dos picos); el C/N0, el síntoma (potencia sube). Complementarios.

## Mini-simulacro

1. un segundo pico en la CAF, más fuerte. 2. porque el correlador engancha
el más alto → arrastra al lazo. 3. alinearse y subir potencia de a poco. 4.
sube el C/N0 (6.4 lo detecta). 5. TEXBAT (UT Austin).
