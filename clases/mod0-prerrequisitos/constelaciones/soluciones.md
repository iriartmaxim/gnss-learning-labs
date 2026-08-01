# Soluciones — Constelaciones

## Lab — censo comparado (día 166)

| Sistema | SVs BRDC | nominal |
|---|---|---|
| GPS | 32 | ~31 |
| GLONASS | 27 | ~24 |
| Galileo | 30 | ~28 |
| BeiDou | 37 | ~35 |
| Globales | **126** | — |

El BRDC lista todo satélite que **emitió** ese día, incluidos los
marginales o en pruebas; por eso supera el nominal y difiere del SP3
preciso (que solo trae los de órbita calculada: E30, C30…). No es error:
es la diferencia entre "quién transmitió" y "quién tiene producto fino".

## E1 — más alto / más bajo / período

Más alto: **Galileo** (~23 200 km); más bajo: **GLONASS** (~19 100 km).
Por la 3ª ley ($T \propto a^{3/2}$), más alto = período más largo →
**Galileo** tiene el período más largo de los cuatro (~14 h vs ~11h58 de
GPS). Es la cuenta de diseño que hiciste en la clase 0.3 (E1).

## E2 — qué gana el multi-GNSS

Además de cantidad: (1) **geometría** — más satélites bien repartidos
bajan el DOP (clase 1.4), mejorando la precisión con el mismo ruido; (2)
**redundancia** — más ecuaciones que incógnitas permiten detectar y
excluir fallos (RAIM, mod5); (3) **disponibilidad** en cañones urbanos y
bajo follaje, donde con una sola constelación no alcanzan 4 satélites.

## E3 — por qué SBAS no es un 5º global

SBAS no provee navegación autónoma: sus GEO transmiten **correcciones e
integridad** sobre los GNSS existentes (dónde está cada satélite mejor
estimado, y si es confiable). Sin un GNSS abajo, SBAS no te posiciona.
Es una capa de servicio, no una constelación de navegación.

## F1 — satélites visibles

Con ~120 globales y aprox. la mitad del lado visible del planeta, y de
esos los que superan el horizonte y la máscara de elevación: del orden de
**30–40 satélites** simultáneos desde cielo abierto multi-GNSS. (Un
receptor GPS-only ve típicamente 8–12.)

## F2 — retardo extra de Galileo

$\Delta h = 23\,200 - 20\,200 = 3\,000$ km. $\Delta t = 3\,000 / c
\approx 3\,000 / 299\,792 \approx 10$ ms de tiempo de vuelo adicional
(en el cénit). Nada dramático para el PVT, pero sí cambia la geometría.

## C1 — por qué mejora con más constelaciones

Porque la precisión de posición es $\sigma_{pos} \approx \text{DOP}
\times \sigma_{med}$: con el mismo $\sigma_{med}$, más satélites bien
distribuidos **bajan el DOP** (mejor condicionamiento de la matriz de
geometría, clase 1.4). Y la redundancia habilita el control de calidad
(mod5). Mismo receptor, mismo ruido, mejor y más confiable posición.

## C2 — GLONASS FDMA

GLONASS legado da a cada satélite su **propia frecuencia** (FDMA), no un
código distinto en la misma frecuencia (CDMA). Un receptor CDMA común
correla todos los satélites contra la misma portadora; con FDMA hay que
sintonizar y procesar canales de frecuencia distintos, más sesgos
inter-canal. Más hardware/procesamiento por poca ganancia → el path lo
menciona y sigue con los CDMA.

## C3 — Galileo primaria

Documentación abierta y prolija (OS SIS ICD), señales E1/E5a bien
definidas, F/NAV limpio para efemérides (1.3), y —clave— es el único con
**OSNMA** (autenticación, mod6), que es el diferencial del perfil de
ciberseguridad. GPS entra donde suma como contraste histórico (Klobuchar,
C/A). No es que GPS sea peor: es que Galileo enseña más cosas nuevas.

## Mini-simulacro

1. GPS (EE.UU.), GLONASS (Rusia), Galileo (UE), BeiDou (China). 2.
GLONASS: FDMA, cada satélite su frecuencia → receptor más complejo. 3.
global GPS · regional QZSS · aumentación EGNOS. 4. E1 (OSNMA). 5. porque
cuenta todo el que emitió, incluidos marginales/pruebas, no solo la
constelación nominal.
