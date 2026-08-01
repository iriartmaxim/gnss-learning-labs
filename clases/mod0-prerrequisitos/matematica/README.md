# Matemática previa — la rampa al motor de mínimos cuadrados

> Bloque del máster: Prerrequisitos (transversal)

Es el **"Refresco matemático dirigido"** del path: la cadena de
prerrequisitos que hace falta para cursar la [clase 0.2 (mínimos
cuadrados, Gauss-Newton y rotaciones)](../clase0.2-minimos-cuadrados/README.md)
entendiendo cada paso, no recitándolo. Material destilado del cuaderno
de estudio a mano; el criterio de diseño: **números antes que símbolos,
un concepto por vez, y verificación propia de cada regla**.

## La cadena de dependencias

```
Límites  ──►  Derivadas  ──►  Mínimos cuadrados  ──►  Jacobiano / Gauss-Newton / PVT
 (h→0)      (ritmo, ∂,        (ecuaciones            (clase 0.2 y puente
            cadena)           normales)               a la 1.2)
```

Cada flecha es un "necesito esto para entender lo siguiente". Se estudia
de izquierda a derecha.

## Orden de estudio

1. [limites.md](limites.md) — la idea de *acercarse* a un valor ($h \to 0$)
   y el caso $0/0$ indeterminado. El cimiento: **la derivada es un 0/0
   resuelto**.
2. [derivadas.md](derivadas.md) — ritmo de cambio medido con tablas, las
   4 piezas básicas y sus 2 reglas, la justificación analítica por
   definición, derivada parcial (congelar) y regla de la cadena — hasta
   derivar la $S$ completa y armar las **ecuaciones normales**.
3. **Clase 0.2** — acá se entra al lab: mínimos cuadrados con las
   ecuaciones normales, la versión ponderada, Gauss-Newton y rotaciones.
4. [jacobiano-y-linealizacion.md](jacobiano-y-linealizacion.md) — el
   cierre: gradiente → jacobiano (fila = observación, columna =
   parámetro), linealización y su error $h^2$, el loop de Gauss-Newton y
   el puente a la matriz de geometría $G$ del PVT. Deja respondido el
   **Checkpoint del Módulo 0**.
5. [repaso-autotests.md](repaso-autotests.md) — para las sesiones de
   repaso espaciado: toda la cadena en auto-tests plegados, bloque por
   bloque. Regla: **recuperar, no reconocer**.

## Cómo usar este material

- **A mano primero**: papel, calculadora y un borrador. La máquina solo
  para aritmética repetitiva o para verificar (cada nota trae su
  verificador en Python).
- **Terminología formal al frente** (sustitución directa, cociente
  incremental, discontinuidad evitable, matriz jacobiana, ecuaciones
  normales…), con lo informal entre paréntesis como apoyo.
- **Chequeos de cordura siempre**: distancias jamás negativas, resultados
  en ventanas esperadas, verificar sustituyendo.
- Los ejercicios traen la solución plegada (`▸ Solución`): resolvé antes
  de desplegar.

## Lab-lite: verificador de la rampa

Cuando termines las notas, corré desde la raíz del repo:

```bash
python3 clases/mod0-prerrequisitos/matematica/lab/verificar_rampa.py
```

Chequea con asserts los números de referencia de toda la cadena (ritmos,
jacobiano numérico vs analítico, las ecuaciones normales de la tabla de
9 puntos, Gauss-Newton para $p^2=9$ y el error $h^2$ de la
linealización). Si termina en "RAMPA OK", estás en condiciones de entrar
al lab de la 0.2.

## Cheat sheet de la cadena

```text
Definición de derivada     f'(b) = lim_{h→0} [f(b+h) − f(b)] / h   (un 0/0 resuelto)
Las 4 piezas               c→0 · x→1 · c·x→c · x²→2x
Las 2 reglas               multiplicador acompaña · suma = término a término
Parcial (congelar)         sumando congelado muere · multiplicador congelado queda
Cadena (cáscara/peaje)     d/db (relleno)² = 2·(relleno)·(relleno)'
Ecuaciones normales        Σy = mΣx + nb        Σxy = mΣx² + bΣx
La tabla de referencia     Σx=55 Σy=57 Σxy=233 Σx²=473 n=9 → m≈−0,8425 b≈11,48
Linealización              f(p₀+δ) ≈ f(p₀) + J·δ     error ~ h²
Gauss-Newton               (JᵀJ)δ = Jᵀr · actualizar p←p+δ · cortar por ‖δ‖ chico
Fila del PVT (G)           (−ux, −uy, −uz, 1)  ← versor receptor→sat + reloj
Convergencia GN            cuadrática cerca de la solución (dígitos ~se duplican)
```

## Glosario (informal → formal)

| Informal (de sesión) | Formal (UTN) |
|---|---|
| enchufar | **sustitución directa / evaluar** |
| sin huecos | **función continua** |
| el hueco | **discontinuidad evitable** |
| el ratito / pasito | **incremento** ($h$) |
| ritmo promedio | **cociente incremental** |
| ritmo instantáneo | **tasa de variación instantánea** (la derivada) |
| la entrada | **variable independiente / argumento** |
| la salida | **imagen** |
| congelar | **derivación parcial** (las demás variables como constantes) |
| cáscara y relleno / peaje | **regla de la cadena** (función compuesta) |
| la cajita | **binomio / propiedad distributiva** |
| los montones | **términos de las ecuaciones normales** (productos escalares) |
| el tirón | $J^\top \mathbf{r}$ |
| el paso / pasito de GN | **vector corrección** $\boldsymbol\delta$ |

**Tarjeta de símbolos** (recordatorio rápido): $\mathbf{p}_0$ (candidata
inicial) · $\mathbf{s}_i$ (posición del satélite $i$) · $\rho_i$
(pseudodistancia medida, el dato) · $d_i$ (distancia predicha) · $r_i$
(residuo = medido − predicho) · $S$ (función objetivo: suma de
residuos²) · $J$ (matriz jacobiana; filas = observaciones) · $J^\top$
(traspuesta: filas↔columnas) · $M = J^\top J$ · $\mathbf{v} =
J^\top\mathbf{r}$ · $\boldsymbol\delta$ (corrección) · $G$ (matriz de
geometría: el $J$ del PVT).

## Dónde desemboca

El checkpoint del Módulo 0 pide *explicar por qué linealizar el problema
PVT lo convierte en mínimos cuadrados iterativos, y qué rol juega el
jacobiano*. Esta rampa existe para poder responderlo con fundamento:
sin límites no hay derivada, sin derivadas no hay jacobiano, sin
jacobiano no hay Gauss-Newton — y sin Gauss-Newton no hay posición.
