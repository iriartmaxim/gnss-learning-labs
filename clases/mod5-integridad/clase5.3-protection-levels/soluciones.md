# Soluciones — Clase 5.3 (protection levels)

Números de referencia: día 166, 12:00–13:00, LPGS. Los produce el propio
lab; si al re-ejecutar difieren, se investiga (regla 3).

## Lab

| Métrica | Referencia |
|---|---|
| Épocas RAIM (≥5) | 121 |
| HPL med / máx | 6.72 / 13.29 m |
| VPL med / máx | 17.03 / 20.86 m |
| pbias | ≈ 6.71 |
| Disponibilidad LPV-200 | 100 % |

**TODO 1 (geometría ENU):** por cada satélite, versor ECEF
$u=(x_{sat}-rec)/\lVert\cdot\rVert$, rotado con `matriz_enu` a ENU; la fila
es $(-u_E,-u_N,-u_U,1)$. El 1 es la columna del reloj (igual que en 1.4).

**TODO 2 (slopes y PL):** con $S=(G^\top G)^{-1}G^\top$ y $P=GS$:
$\text{slope}_{H,i}=\lVert S_{[:2],i}\rVert/\sqrt{1-P_{ii}}$;
$HPL=\max_i\text{slope}_{H,i}\cdot p_{bias}$. El vertical usa $|S_{2,i}|$.

## E1 — disponibilidad

HPL=45 > HAL=40 → **no disponible** para LPV. Si la operación es NPA
(HAL=185 m), 45 < 185 → **disponible**. La misma posición sirve o no según
la exigencia de la operación: el AL lo pone la operación, no el receptor.

## E2 — máscara de elevación

Subir el cutoff a 25° elimina satélites bajos: mejora el multipath (3.4)
pero **empeora la geometría** — quedan menos satélites y peor repartidos,
el slope máximo crece y con él el HPL/VPL. Puede pasar el PL por encima
del AL → pierde disponibilidad. Es el trade-off geometría vs ruido: no
hay cutoff óptimo universal.

## E3 — por qué VAL < HAL pero más difícil

La componente vertical de la geometría es intrínsecamente más débil
(todos los satélites están *arriba* del receptor, ninguno debajo → mala
observabilidad vertical, VDOP > HDOP). Por eso el VPL es mayor que el HPL
aunque el VAL sea numéricamente más chico: la vertical es la que casi
siempre limita.

## F1 — margen vertical

A 200 pies (~60 m) sobre pista en aproximación, el VAL de 35 m es el
colchón: garantiza que el error vertical real no acerque al avión al
terreno más de lo previsto. Si el VPL supera 35 m, no hay garantía
suficiente → se aborta la guía vertical.

## F2 — eventos aceptables

Riesgo $2\times10^{-7}$/aprox × $10^6$ aprox/año = **0.2 eventos/año** de
integridad "aceptables" — es decir, se tolera ~1 cada 5 años. De ahí la
exigencia extrema del PL.

## Mini-simulacro

1. §3.1. 2. PL < AL. 3. error de posición por unidad de estadístico; su
máximo lo fija el peor satélite de la geometría. 4. PFA → umbral; PMD →
tamaño de fallo detectable; juntos dan λ (pbias). 5. 17<35 disponible;
con VAL=15, 17>15 → no disponible.
