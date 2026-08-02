# Clase 5.4 — La cadena de integridad del sistema: usuario + tierra

> Bloque del máster: B4 — System · Cadena de integridad y detección de ataques del sistema

**Objetivo en una frase**: integrar todas las defensas del path —RAIM (5.1),
consistencia (6.4), OSNMA (6.1), sanidad física (4.1) y monitoreo de tierra—
en una **cadena de integridad de sistema**, y ver por qué la combinación
cubre lo que ninguna capa aislada puede.

**Tiempo estimado**: 2.5 h (teoría 60' · lab-lite 50' · cierre 40'). Conceptual: la vista de sistema completa es del máster; acá la armás con las piezas del path.

## 1. Objetivos

- [ ] Mapear qué ataque/fallo detecta cada capa (usuario y tierra).
- [ ] Ver que ninguna capa sola cubre todo, pero la combinación sí.
- [ ] Distinguir monitoreo de usuario del de tierra (segmento de control).
- [ ] Entender SBAS como la integración operacional de ambas mitades.

## 2. ¿Dónde estamos?

Capstone de integridad y seguridad: junta 5.1–5.3 (RAIM, PL), 6.1–6.6
(cripto, ataques), 4.1 (física) y el monitoreo de tierra (4.2/4.3, SISRE) en
una sola visión de sistema. Es el ítem B4 que el máster conecta con el
segmento de control.

```mermaid
flowchart TB
    subgraph USUARIO
      RAIM[5.1 RAIM] · CONS[6.4 consistencia] · OSNMA[6.1 OSNMA] · FIS[4.1 física]
    end
    subgraph TIERRA
      MON[monitoreo del segmento: SISRE, salud (4.2/4.3)]
    end
    USUARIO --> DEC[decisión de integridad de sistema]
    TIERRA --> DEC
```

## 3. Teoría (con blancos B1–B5)

### 1. Dos mitades: usuario y sistema

La integridad se vigila en **dos lugares**: el **usuario** (lo que llega a
su antena: RAIM, consistencia, OSNMA, física) y el **segmento de tierra**
(la salud del sistema: SISRE anómalo, satélite enfermo). Cada mitad ve lo
que la otra no.

### 2. Cada capa, su punto ciego

- **RAIM** (5.1): fallos de rango, pero necesita redundancia.
- **Consistencia** (6.4): C/N0, cruce, saltos — caza el replay, pero un
  ataque sofisticado la evade.
- **OSNMA** (6.1): datos falsos, pero **no el rango**.
- **Física** (4.1): efeméride implausible, pero no fallos de reloj.
- **Tierra**: salud del sistema, pero no el spoofing **local** del usuario.

### 3. La combinación cubre lo que ninguna sola

Cada ataque/fallo lo detecta un **subconjunto distinto** de capas. El
replay solo lo ve la consistencia; la mala salud no señalada la ven RAIM +
física + tierra. Combinando todas, no queda escenario sin cobertura:
**defensa en capas** a nivel sistema.

### 4. SBAS: la integración operacional

SBAS es la cadena hecha producto: el **segmento de tierra** monitorea la
constelación y transmite correcciones **e integridad** (los σ, 5.3) al
**usuario**, que calcula sus protection levels y decide. Une monitoreo de
sistema + decisión de usuario en un servicio certificable.

### Lectura activa (B1–B5)

<details><summary>Completá y verificá</summary>

- **B1.** La integridad se vigila en dos mitades: el ______ y el segmento de ______.
- **B2.** OSNMA no ve el ______; solo la consistencia caza el replay.
- **B3.** La tierra ve la ______ del sistema; el usuario, lo ______.
- **B4.** Ninguna capa sola cubre todo → ______ en capas.
- **B5.** ______ integra tierra + usuario en un servicio con integridad.

Respuestas: B1 usuario / control (tierra) · B2 rango · B3 salud / local · B4 defensa · B5 SBAS
</details>

## 4. Lab-lite

```bash
python3 clases/mod5-integridad/clase5.4-integridad-sistema/lab/lab_integridad_sistema_TODO.py
```

Combinás las capas en un monitor único y ves que cubre 5/5 escenarios.
Solución en `lab/soluciones/`.

### Tabla de validación

| Capa | Escenarios que cubre sola |
|---|---|
| Consistencia (6.4) | **4/5** |
| Tierra / RAIM | 3/5 |
| Física (4.1) | 2/5 |
| OSNMA (6.1) | 1/5 |
| **Todas combinadas** | **5/5** |
| Solo usuario (sin tierra) | 4/5 |

El dato que ordena: **la combinación cubre todo, ninguna capa sola** — y la
tierra agrega el escenario que el usuario no ve por sí mismo.

## 5. Ejercicios a mano

**E1.** ¿Por qué el replay es el escenario más difícil de la tabla?

**E2.** Dá un ejemplo de algo que solo el segmento de tierra puede detectar
y otro que solo el usuario.

**E3.** ¿Cómo cierra SBAS la cadena entre tierra y usuario?

## 6. Estimaciones Fermi

**F1.** Si cada capa tiene 90 % de detección por su cuenta y son
independientes, ¿cuál es la probabilidad de que **al menos una** de 4 capas
detecte un ataque que las 4 pueden ver?

**F2.** El segmento de tierra actualiza la integridad cada ~6 s (SBAS).
¿Alcanza para una aproximación de aviación (alerta en < 6 s)? ¿Y para un
auto autónomo (< 100 ms)?

## 7. Preguntas conceptuales

<details><summary>C1. ¿Por qué la integridad es una cadena y no un producto único?</summary>

Porque los fallos y ataques son heterogéneos: reloj, órbita, datos, señal,
salud. Ninguna herramienta los cubre todos. La integridad emerge de
**combinar** capas independientes que se tapan los puntos ciegos.
</details>

<details><summary>C2. ¿Qué aporta el segmento de tierra que el usuario no puede?</summary>

Visión global del sistema: SISRE por satélite (4.2/4.3), salud de relojes,
detección de anomalías de constelación. El usuario solo ve su porción del
cielo y su entorno local.
</details>

<details><summary>C3. ¿Por qué el usuario sigue siendo imprescindible?</summary>

Porque el ataque local (spoofing/jamming en su ubicación) no lo ve ninguna
red de tierra: hay que detectarlo donde ocurre. Integridad = tierra
(sistema) + usuario (local), siempre las dos.
</details>

## 8. Pregunta de entrevista

> "Describí la cadena de integridad de un GNSS de extremo a extremo: qué
> monitorea el usuario, qué la tierra, y cómo SBAS los une. ¿Qué escenario
> se le escapa a cada uno?"

**Mini-caso**: diseñás la integridad de un sistema de aterrizaje
automático. ¿Qué capas combinás, qué latencia exigís, y qué residuo
comunicás?

## 9. Mini-simulacro (12 min)

1. Nombrá las capas de usuario y la de tierra.
2. ¿Por qué ninguna sola alcanza?
3. ¿Qué escenario solo ve la consistencia?
4. Usuario vs tierra: qué ve cada uno.
5. ¿Cómo integra SBAS ambas mitades?

<details><summary>Respuestas</summary>

1. usuario: RAIM, consistencia, OSNMA, física; tierra: monitoreo del
segmento. 2. cada ataque tiene su punto ciego; combinadas cubren 5/5. 3. el
replay. 4. tierra: salud del sistema; usuario: lo local. 5. transmite
correcciones + integridad (σ) al usuario, que decide con protection levels.
</details>

## 10. Caso real — EGNOS: la cadena de integridad certificada

EGNOS (el SBAS europeo) es esta clase hecha servicio operacional
certificado para aviación. Una red de **estaciones de tierra** (RIMS)
monitorea la constelación, centros de proceso calculan correcciones e
**integridad** (los límites de confianza por satélite y por celda
ionosférica), y satélites GEO los transmiten. El **receptor del avión**
combina eso con su propia decisión (protection levels vs alert limits, 5.3)
para habilitar o no una aproximación LPV-200. Es exactamente la cadena
usuario↔tierra de tu lab, con la diferencia de que cada eslabón está
certificado a un riesgo de integridad de 10⁻⁷. Llegaste, con el path, a
entender de punta a punta cómo se construye esa confianza.

## 11. Glosario ES/EN

| ES | EN | Nota |
|---|---|---|
| cadena de integridad | integrity chain | capas usuario + sistema |
| monitoreo de tierra | ground monitoring | segmento de control (RIMS) |
| SISRE | SISRE | error de rango en el espacio (4.2/4.3) |
| defensa en capas | defense in depth | combinar capas independientes |
| RIMS | RIMS | estaciones de monitoreo de EGNOS |
| riesgo de integridad | integrity risk | prob. de error no señalado |

## 12. Cheat sheet

```text
Usuario   RAIM (5.1) · consistencia (6.4) · OSNMA (6.1) · física (4.1)
Tierra    monitoreo del segmento: SISRE, salud de reloj/órbita (4.2/4.3)
Regla     ninguna capa sola cubre todo → combinar (defensa en capas)
Puntos ciegos  OSNMA no ve rango · física no ve reloj · tierra no ve lo local
SBAS/EGNOS  tierra (correcciones+integridad) → usuario (protection levels, 5.3)
Ref lab   combinadas 5/5 · mejor sola 4/5 · solo usuario 4/5
```

## 13. Errores comunes

1. Confiar en una sola capa (cada una tiene su punto ciego).
2. Creer que la tierra ve el spoofing local del usuario (no puede).
3. Olvidar que OSNMA no cubre el rango (replay lo evade).
4. Separar integridad de usuario y de sistema: son una sola cadena.
5. Ignorar la latencia: la integridad tarde no sirve para la operación.

## 14. Referencias

- ESA — EGNOS, arquitectura de integridad (RIMS, MCC).
- RTCA DO-229 — SBAS MOPS (integridad de sistema).
- Navipedia — "Integrity", "SBAS Fundamentals".
- Clases 5.1–5.3 (RAIM/PL), 6.1–6.6 (cripto/ataques), 4.1–4.3 (física/SISRE).

## 15. Rúbrica de autoevaluación

- ⭐ Distingo integridad de usuario y de tierra, y nombro las capas.
- ⭐⭐ Combino las capas en el lab y muestro que cubren lo que ninguna sola.
- ⭐⭐⭐ Diseño una cadena de integridad para un caso crítico y comunico el residuo.

## 16. Para tu bitácora

Copiá [`bitacora.md`](bitacora.md): tu cobertura combinada vs la tabla y una
frase sobre por qué usuario y tierra se necesitan mutuamente. Con esto
cerrás la visión de integridad de sistema del path.
