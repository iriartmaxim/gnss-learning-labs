# Soluciones — Clase 6.6 (threat model)

El lab valida la coherencia de la matriz. "THREAT MODEL OK".

## Lab

| Capa | Ataques que toca |
|---|---|
| detectores (6.4) | 5/5 |
| SAS/ACAS | 3/5 |
| física (4.1) | 2/5 |
| OSNMA | 1/5 (solo datos) |

**TODO 1a:** `if not any(fila[c] for c in CAPAS): problemas.append(...)`.
**TODO 1b:** `if amenazas[a]["OSNMA"]: problemas.append("OSNMA no cubre rango")`.

## El documento (estilo ADR)

**Decisión:** la autenticación GNSS se diseña **en capas**, no con una sola
herramienta.

**Contexto:** OSNMA (6.1/6.2) autentica los **datos** de navegación con
criptografía fuerte, pero **no autentica el rango**: un replay/meaconing de
la señal auténtica con retardo mueve la posición sin tocar los datos.

**Capas y qué cubre cada una:**
- **OSNMA** (cripto): falsificación de efeméride/reloj. No cubre rango.
- **SAS/ACAS** (autenticación a nivel de señal, sobre E6-C): ayuda contra
  spoofing de rango y replay (la señal misma lleva un secreto).
- **Detectores de consistencia** (6.4): C/N0, deriva de reloj, salto de
  posición, cruce entre constelaciones. Cubren lo que la cripto no ve.
- **Sanidad física de efeméride** (4.1): semieje MEO plausible, saltos de
  empalme, coherencia orbital. Defensa ortogonal (cripto + física).

**Consecuencia:** ningún ataque queda sin defensa, pero cada uno tiene un
**residuo**. El jamming no se autentica (se detecta y se sobrevive con INS,
7.5). La seguridad es un sistema, no una casilla.

## E1 — por qué OSNMA no basta

Autentica el mensaje, no la señal ni el rango. Un atacante que **re-emita**
la señal auténtica (con sus tags válidos) con retardo pasa OSNMA pero
desplaza tu posición/tiempo. Necesitás SAS (nivel señal) o detección de
consistencia/física.

## E2 — la capa física como defensa ortogonal

La sanidad de efeméride (4.1) no usa criptografía: chequea que la órbita
tenga sentido (semieje MEO, sin saltos imposibles). Es ortogonal a la
cripto: un atacante que rompa una no rompe la otra. Combinarlas eleva
mucho el costo del ataque.

## Mini-simulacro

1. OSNMA datos, SAS señal/rango, detectores consistencia, física coherencia.
2. no autentica el rango. 3. replay/meaconing. 4. en capas. 5. el jamming
(se detecta y se puentea con INS, no se autentica).
