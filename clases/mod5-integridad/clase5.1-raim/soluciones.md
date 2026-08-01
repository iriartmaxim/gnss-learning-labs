# Soluciones — Clase 5.1 (RAIM)

## Lab

**TODO 1**: GN → d = |xyz − p̂| → r = P − (d + cδt) → T = rᵀr/σ².
Referencia 12:00: T=8.4, err 1.96 m, 8 sats. **TODO 2**: dof = 7−4 = 3,
umbral χ²(0.999, 3) = 16.3, disparan 3/121 (épocas genuinamente sucias).
**TODO 3**: 278 / 1663 / 6581 — todos detectados; daño 6.7/16.7/33.5 m.
**TODO 4**: b_min = 4 m.

## E1

Media = dof = 3; varianza = 2·dof = 6 → σ_T ≈ 2.45. El umbral 16.3 queda
a (16.3−3)/2.45 ≈ **5.4 σ** — la χ² tiene cola pesada: no es "5 sigmas
gaussianos" de improbable, por eso se usa la ppf y no la intuición.

## E2

slope = 33.5/100 = 0.335. Con slope 0.5 y zona ciega de 4 m: hasta
0.5 × 4 = **2 m de error garantizado invisible** — más el que ya hay. El
PL de 5.3 es exactamente esta cuenta hecha con el PEOR slope y el peor
bias no detectable.

## E3

El LSQ absorbe parte del bias (mueve la solución) y deja fracción fija
en los residuos: r ∝ b → T = Σr² ∝ b². Por eso duplicar el bias
cuadruplica T (278 → ~1100 ≈ el 1663 medido con 2.5×).

## F1

86 400/30 = 2880 épocas/día × 1e-3 ≈ **~3 alarmas/día**. Aviación pide
Pfa ~1e-5/h: umbral más alto → zona ciega mayor → por eso necesita PL y
no solo detección.

## F2

dof = 1, media T = 1: un fallo debe sobresalir de UNA χ²(1) — cola
pesadísima. La detectabilidad se derrumba: la redundancia ES la
integridad.

## C1

Detectar: hace falta al menos 1 grado de libertad → n ≥ 5. Identificar:
el subconjunto sin el culpable debe seguir siendo redundante → n ≥ 6
(sacás 1 y te quedan 5). Es pura aritmética de dof.

## C2

Del modelo: σ=1 gaussiano blanco es optimista para épocas con multipath
o satélite rasante. En receptor: se investigan (¿qué sat? ¿qué
elevación?), se des-pesa o excluye la medición sospechosa — RAIM como
control de calidad continuo, no solo alarma.

## C3

T suma TODOS los residuos: un fallo de 60 m o dos de 30 m dan T
parecido. La hipótesis de fallo único es la base del RAIM clásico;
romperla (fallos múltiples, correlacionados, constelación entera) es el
punto de partida de **ARAIM** (lectura del módulo).

## Mini-simulacro

1. T = rᵀr/σ² ~ χ²(n−4) sin fallos.
2. De chi2.ppf(1−Pfa, dof); Pfa menor compra menos gritos falsos al
   precio de zona ciega más grande.
3. ~4× (cuadrático): ~1100.
4. De σ real, el número de satélites (dof) y la geometría (slopes).
5. Detectar: T y umbral (≥5). Identificar: subconjuntos (≥6, 5.2).
   Excluir: identificar + re-resolver y re-chequear.

## Entrevista — guión

"RAIM mide la coherencia interna: con más satélites que incógnitas, los
residuos deben parecer ruido; un estadístico χ² con umbral por falsa
alarma decide. Garantiza detectar fallos que sobresalen del ruido con
probabilidad calculable. NO garantiza: fallos dentro del ruido, fallos
múltiples que se disfrazan, ni error chico sin fallo — para acotar eso
existen los protection levels."

## Mini-caso

T=40 sostenido no es un pico estadístico (χ²(3) no vive ahí 10 min):
hay una medición envenenada. Con ≥6 sats: identificar y excluir (5.2) y
seguir con bandera amarilla. Con 5: no podés señalar → subís PL o bajás
la bandera de servicio. La decisión la manda el nivel de servicio
comprometido, no el orgullo del fix.
