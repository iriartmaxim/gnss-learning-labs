# Clase 0.3 — Soluciones

## Blancos de la teoría

- **B1**: por **Newton** (Newton-Raphson) sobre f(E) = E − e·sinE − M; con e = 0.01 converge en **3 iteraciones** (a tol 1e-12).
- **B2**: T ≈ **11 h 58 m** (43 077 s) — medio día sidéreo (86 164/2 = 43 082 s).
- **B3**: **−0.039 °/día**.

## Ejercicios a mano

### E1 — tercera ley sin μ

a₂ = a₁·(T₂/T₁)^(2/3) = 26 560 · (50 686/43 077)^(2/3)
= 26 560 · (1.17663)^(2/3) = 26 560 · 1.1145 ≈ **29 601 km** ✓
(coincide con el a de Galileo de la Parte C: 29 600 km).

### E2 — un paso de Newton

E₀ = M = 1. f(E₀) = 1 − 0.1·0.8415 − 1 = −0.08415.
f'(E₀) = 1 − 0.1·0.5403 = 0.94597.
E₁ = 1 − (−0.08415)/0.94597 = 1 + 0.08896 = **1.08896**.

La Parte F del lab lo confirma: E₁ = 1.08895 (redondeo de sin/cos),
exacto 1.08860 → error de 3.6×10⁻⁴ rad después de UNA iteración.

### E3 — tiempo de vuelo

- Cénit: 20 200 / 299 792.458 ≈ **67.4 ms**.
- Horizonte: √(26 560² − 6378²) = √664 754 716 ≈ 25 783 km → **86.0 ms**.

Rango: la pseudodistancia GPS "vive" entre ~67 y ~86 ms de luz. En la
clase 1.2, el sesgo de reloj de +2.5 ms (≈750 km) se destaca justamente
contra esta escala.

## Fermi

- **F1**: T = medio día sidéreo ⇒ **2 vueltas por día sidéreo**
  (≈ 2.005 por día solar). Consecuencia: el satélite reaparece sobre el
  mismo punto de la Tierra cada día sidéreo — el ground track se repite
  (4 min más temprano cada día solar).
- **F2**: si el satélite da exactamente 2 vueltas mientras la Tierra da 1,
  la geometría satélite-Tierra se repite: operativamente predecible
  (mismo cielo a la misma hora sidérea). Costo: resonancia 2:1 — las
  mismas anomalías del geopotencial "empujan" siempre en el mismo lugar
  de la órbita y el efecto se ACUMULA (hay que gastar más combustible en
  mantenimiento). Galileo eligió 17 vueltas cada 10 días para repartir
  ese empuje.
- **F3**: f_D = f·v_r/c = 1575.42 MHz × 0.9/299 792 ≈ **±4.7 kHz**.
  Por eso la búsqueda de adquisición (módulo 2) barre ~±5 kHz.

## Mini-simulacro

1. M = E − e·sin(E): M anomalía media, E excéntrica, e excentricidad.
2. M (reloj, lineal en t) → E (resolver Kepler) → ν (semiángulo; la geométrica real).
3. T ≈ 11 h 58 m = **medio día sidéreo**: elegido para que el ground track se repita a diario.
4. Ω̇ = −(3/2)·J2·(Re/p)²·n·cos(i); **negativo** (regresión hacia el oeste) para órbitas progradas (i < 90°).
5. **OMEGA_DOT** (y también idot como pariente).

## Notas de la corrida de referencia

```text
A: e=0.001->E=1.000842(3it) 0.01->1.008460(3) 0.3->1.288091(5) 0.7->1.694639(6)
B: M=1, e=0.7 -> E=1.6946 -> nu=2.4310 rad (139.3°)
C: ISS 1h32m 7.66 | GPS 11h57m 3.87 | Galileo 14h04m 3.67 | GEO 23h56m 3.07
D: T²/a³ = 9.904e-14 = 4π²/μ
E: GPS -0.039 °/día | Galileo -0.026 | ISS -4.952
F: E1=1.08895 vs 1.08860 (err 3.56e-4)
```
