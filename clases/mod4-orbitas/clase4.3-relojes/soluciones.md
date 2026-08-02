# Soluciones — Clase 4.3 (relojes)

Referencia: día 166, 10:00–14:00, Galileo. Los produce el lab.

## Lab

| Métrica | Referencia |
|---|---|
| Satélites | 30 |
| Error broadcast−preciso (mediana) | 1.75 m |
| Más estable | E34 σy≈1.2e-11 (PHM) |
| Menos estable | E19 σy≈1.3e-10 (RAFS) |
| Razón peor/mejor | ×11.6 |

(Los SV concretos más/menos estable pueden variar levemente al re-ejecutar
según los datos; lo robusto es la **dispersión** ~×10 entre dos familias.)

**TODO 1:** `af0 + af1*(t-toc) + af2*(t-toc)**2`.
**TODO 2:** `d2 = y[2:]-2*y[1:-1]+y[:-2]; sqrt(mean(d2**2)/2)`.

## E1 — af0 en metros

−0.75 ms × c = −0.75e-3 × 299792458 ≈ **−224.8 km**. El receptor DEBE
aplicarlo: si lo ignora, cada pseudodistancia de ese satélite queda corrida
224 km → la posición es basura. El reloj es la corrección más grande del
mensaje.

## E2 — deriva por estabilidad

σy = 10⁻¹¹ a 300 s → error de tiempo ~ σy·τ = 10⁻¹¹·300 = 3e-9 s = 3 ns →
×c ≈ **0.9 m** en 300 s. Con RAFS (10⁻¹⁰): ~9 m. Por eso el PHM (más
estable) necesita menos correcciones y da mejor rango entre actualizaciones.

## E3 — af2 diminuto pero no cero

El envejecimiento (aging) es la deriva lenta de la frecuencia del reloj
físico: real pero pequeña en escalas de horas. Se incluye para que el
polinomio siga siendo bueno hasta la próxima actualización; ponerlo en cero
degradaría al final del arco.

## F1 — deriva entre actualizaciones

Con σy ~10⁻¹¹ y ~600 s entre re-emisiones: error ~10⁻¹¹·600·c ≈ 1.8 m. Ese
crecimiento es el que justifica re-emitir cada ~10 min: mantener el error
de reloj por debajo del metro-y-algo.

## F2 — preciso vs broadcast

6 ns / 0.1 ns = **×60** mejor el preciso. El PPP (7.4) gana ese factor en el
término de reloj — aunque, como viste, con código el techo lo pone el
ruido/multipath, no el reloj.

## Mini-simulacro

1. δt=af0+af1(t−toc)+af2(t−toc)²: sesgo, deriva, envejecimiento. 2. ~30 cm.
3. la estabilidad de frecuencia a un tau. 4. PHM, ~10×. 5. el rango es
tiempo de vuelo × c → el error de reloj entra 1:1.
