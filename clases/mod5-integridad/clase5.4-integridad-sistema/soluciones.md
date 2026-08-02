# Soluciones — Clase 5.4 (integridad de sistema)

Escenarios sintéticos deterministas. "la cadena de integridad del sistema OK".

## Lab

| Capa | Escenarios que cubre sola |
|---|---|
| consistencia (6.4) | 4/5 |
| tierra (monitoreo) | 3/5 |
| RAIM (5.1) | 3/5 |
| física (4.1) | 2/5 |
| OSNMA (6.1) | 1/5 |
| **Todas combinadas** | **5/5** |
| Solo usuario (sin tierra) | 4/5 |

**TODO 1:** `return any(flags[c] for c in capas_activas)`.

## E1 — por qué el replay es el caso difícil

El replay re-emite la señal auténtica con retardo: los datos y sus tags
OSNMA son reales (OSNMA no lo ve), la efeméride es plausible (física no lo
ve), y si es coherente puede pasar RAIM. Solo la **consistencia** (salto de
posición/tiempo, C/N0) lo caza. Es el recordatorio de que ninguna capa
alcanza.

## E2 — usuario vs tierra

El **usuario** (RAIM, consistencia, OSNMA, física) ve lo que le llega a su
antena — incluido el spoofing local que la tierra no ve. El **segmento de
tierra** ve la salud del sistema (SISRE anómalo, satélite enfermo) que el
usuario no puede diagnosticar solo. Se complementan: la integridad es una
cadena usuario↔sistema.

## E3 — por qué SBAS es "integridad de sistema"

SBAS es el ejemplo operacional: el segmento de tierra monitorea la
constelación y transmite correcciones **e integridad** (los σ, 5.3) al
usuario. Une las dos mitades de la cadena: monitoreo de tierra + decisión
de usuario (protection levels).

## Mini-simulacro

1. RAIM+consistencia+OSNMA+física+tierra. 2. porque cada ataque tiene su
punto ciego; combinadas cubren 5/5. 3. el replay (solo consistencia). 4. la
tierra ve salud del sistema; el usuario, lo local. 5. SBAS (correcciones +
integridad de tierra al usuario).
