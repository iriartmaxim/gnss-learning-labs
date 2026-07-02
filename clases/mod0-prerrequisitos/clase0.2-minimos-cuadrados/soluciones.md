# Clase 0.2 — Soluciones

## Blancos de la teoría

- **B1**: Aᵀr = **0** (el residuo es ortogonal al espacio columna de A).
- **B2**: la norma del paso cae **cuadráticamente** (el error nuevo ~ error²: 1.7e-2 → 9.6e-5 → 7.8e-7).
- **B3**: **DOP** (dilución de la precisión); GDOP = √tr((GᵀG)⁻¹).

## Ejercicios a mano

### E1 — LS 3×2

A = [[1,0],[0,1],[1,1]], b = (1, 1, 3).

- AᵀA = [[2, 1], [1, 2]], Aᵀb = (4, 4).
- Sistema: 2x₁ + x₂ = 4; x₁ + 2x₂ = 4 → x̂ = (4/3, 4/3).
- Ax̂ = (4/3, 4/3, 8/3) → r = b − Ax̂ = (−1/3, −1/3, 1/3).
- Aᵀr = (−1/3 + 1/3, −1/3 + 1/3) = (0, 0) ✓

### E2 — gradiente de la norma

f(x, y) = √(x²+y²) ⇒ ∇f = (x, y)/√(x²+y²).
En (3, 4): ∇f = (3/5, 4/5) = **(0.6, 0.8)** — el vector UNITARIO desde el
origen hacia el punto. En la clase 1.2, cada fila del jacobiano de una
pseudodistancia es exactamente esto: −uᵀ (unitario receptor→satélite) más
la columna del reloj.

### E3 — un paso de GN para x² = 9

- x₀ = 2: f = 4, r = 9 − 4 = 5, J = 2·2 = 4.
- δ = (JᵀJ)⁻¹Jᵀr = r/J = 5/4 = 1.25 → **x₁ = 3.25**.
- x₁ = 3.25: f = 10.5625, r = −1.5625, J = 6.5 → δ = −0.2404 → **x₂ ≈ 3.0096**.

Errores: 1 → 0.25 → 0.0096. Cada error es aproximadamente el cuadrado del
anterior (convergencia cuadrática): 0.25² = 0.0625... y de hecho
0.25²·(1/2·f''/f' evaluado) ≈ 0.0096. La secuencia del lab
(1.7e-2 → 9.6e-5 → 7.8e-7) muestra lo mismo.

## Fermi

- **F1**: error ∝ 1/√n ⇒ mitad de error = **4× mediciones**.
- **F2**: 2 puntos exactos definen la recta sin redundancia: cero residuos,
  cero diagnóstico, y cualquier error de medición pasa DIRECTO a los
  parámetros. 100 puntos ruidosos promedian el ruido (σ_param ∝ 1/√100) y
  los residuos permiten detectar outliers y validar el modelo. Para
  predecir: los 100. La redundancia es información — la misma razón por la
  que en GNSS querés más de 4 satélites (RAIM, clase 1.4).
- **F3**: para columnas unitarias a ángulo θ chico, cond(M) ≈ 2/θ(rad)
  (los valores singulares van como √(2±2cosθ) → 2 y θ·(1/√2)·√2...).
  Con θ = 1° = 0.0175 rad: cond ≈ **~115** (el cálculo exacto da 114.6).
  Regla verificable con la referencia: a 5° dio 22.9 ≈ 2/0.0873.

## Mini-simulacro

1. (AᵀWA)x̂ = AᵀWb con W = diag(1/σᵢ²).
2. Es ortogonal: Aᵀr = 0.
3. (JᵀJ)δ = Jᵀr (las ecuaciones normales del problema linealizado).
4. cov(x̂) = σ²(AᵀA)⁻¹.
5. **Falso**. Con ẑ: Rz(90°)Rx(90°)ẑ = (1,0,0) pero Rx(90°)Rz(90°)ẑ = (0,−1,0).

## Notas de la corrida de referencia

```text
A: a=2.011 b=3.062 | ortogonalidad 7.7e-13
B: una tirada con pesos (1.886, 2.989); MC 1000: RMS 0.512 vs 0.280 (x1.8)
C: p=(2.0278, 0.4968) en 8 iteraciones
D: cov teórica var(a)=0.18571, empírica 0.18628, cociente 1.003
E: (1,0,0) vs (0,-1,0)
F: cond 1.00 / 3.73 / 22.90 ; sqrt(tr) 1.41 / 2.83 / 16.23
```
