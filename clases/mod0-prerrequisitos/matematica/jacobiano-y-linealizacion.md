# Jacobiano y linealización (el puente al PVT)

> **Para qué es esta nota** — Último escalón del refresco matemático.
> Toma las derivadas parciales de [derivadas.md](derivadas.md) y las
> organiza en una **matriz** (el jacobiano) para repetir el truco de
> mínimos cuadrados con modelos **no lineales** — que es exactamente lo
> que hace un receptor al resolver su posición. Al cerrarla, el
> Checkpoint del Módulo 0 se responde solo.

## Nivel 0 — El problema nuevo

En la [clase 0.2](../clase0.2-minimos-cuadrados/README.md) el modelo de
partida es una recta: **lineal** en $m$ y $b$. Derivar $S$ e igualar a
cero da un sistema lineal 2×2, y con un solo despeje sale la respuesta.
Una vez.

Pero una pseudodistancia es

$$\rho_i = \sqrt{(x_s - x)^2 + (y_s - y)^2 + (z_s - z)^2} + c\,\delta t$$

**no lineal** en la posición (hay una raíz cuadrada). Derivar e igualar a cero ya no da ecuaciones despejables de una.

**La salida**: cerca de un punto, *cualquier* función suave se parece a una lineal (¡el velocímetro otra vez!). Entonces: aproximo el modelo por uno lineal alrededor de donde estoy, resuelvo ese problema lineal (que ya sé resolver), me muevo a la solución, y **repito**. Para eso necesito dos piezas:

1. El **jacobiano** — el "ritmo" en versión multidimensional.
2. La **linealización** — el "ritmo × pasito" en versión matricial.

## Nivel 1 — Gradiente: las parciales de UNA función, en fila

Si $f$ tiene varias entradas, su **gradiente** es el vector de sus parciales (que ya sabés calcular):

$$\nabla f = \left(\frac{\partial f}{\partial x},\; \frac{\partial f}{\partial y}\right)$$

Ejemplo con sustancia GNSS: la distancia al origen $f(x,y) = \sqrt{x^2 + y^2}$ en el punto $(3, 4)$ (donde $f = 5$):

$$\frac{\partial f}{\partial x} = \frac{x}{\sqrt{x^2+y^2}} = \frac{3}{5} = 0{,}6 \qquad \frac{\partial f}{\partial y} = \frac{y}{\sqrt{x^2+y^2}} = \frac{4}{5} = 0{,}8$$

$$\nabla f = (0{,}6,\; 0{,}8) \quad \leftarrow \text{¡el vector unitario radial!}$$

Interpretación: si me muevo 1 mm en $x$, la distancia crece 0,6 mm; en $y$, 0,8 mm. *Guardá este ejemplo: es literalmente una fila del jacobiano del PVT.*

## Nivel 2 — Jacobiano: una fila por observación, una columna por parámetro

Ahora tengo $n$ observaciones, cada una con su modelo $f_i(p_1, \dots, p_k)$. El **jacobiano** apila los gradientes:

$$J_{ij} = \frac{\partial f_i}{\partial p_j} \qquad \text{fila } i = \text{observación } i, \quad \text{columna } j = \text{parámetro } j$$

**Caso que ya conocés** — la recta $f_i = m x_i + b$, parámetros $(m, b)$:

$$\frac{\partial f_i}{\partial m} = x_i \qquad \frac{\partial f_i}{\partial b} = 1 \qquad\Longrightarrow\qquad \text{fila } i = (x_i,\; 1)$$

$$J = \begin{bmatrix} x_1 & 1 \\ x_2 & 1 \\ \vdots & \vdots \end{bmatrix} = A \;\; \text{(¡la matriz de diseño de mínimos cuadrados!)}$$

> **Importante** — **El jacobiano de un modelo lineal es constante.** No
> depende de $m$ ni de $b$ — por eso en la recta no hace falta iterar:
> la "aproximación lineal" es exacta y una sola pasada basta. En modelos
> no lineales, $J$ cambia según dónde estés parado → hay que recalcularlo
> y repetir.

## Nivel 3 — Linealización: ritmo × pasito, en matricial

La versión 1D la conocés del velocímetro: cerca de $b$,

$$f(b + h) \approx f(b) + f'(b)\cdot h \qquad (\text{salida nueva} \approx \text{salida actual} + \text{ritmo} \times \text{pasito})$$

La versión multidimensional es idéntica, con el jacobiano de ritmo y un vector de pasitos $\boldsymbol\delta$:

$$\mathbf{f}(\mathbf{p}_0 + \boldsymbol\delta) \;\approx\; \mathbf{f}(\mathbf{p}_0) + J\,\boldsymbol\delta$$

Vale para $\boldsymbol\delta$ chico; cuanto más curvado el modelo (o más lejos el punto), peor la aproximación — por eso Gauss-Newton falla si arrancás demasiado lejos.

## Nivel 4 — Gauss-Newton: tus ecuaciones normales, recicladas

Quiero minimizar $\lVert \mathbf{y} - \mathbf{f}(\mathbf{p}) \rVert^2$ con $\mathbf{f}$ no lineal. Sustituyo la linealización y defino el **residuo** $\mathbf{r} = \mathbf{y} - \mathbf{f}(\mathbf{p}_0)$:

$$\min_{\boldsymbol\delta}\; \lVert \mathbf{r} - J\boldsymbol\delta \rVert^2$$

¡Pero esto es un problema **lineal** en $\boldsymbol\delta$ — el mismo de mínimos cuadrados con $A \to J$, $\mathbf{y} \to \mathbf{r}$! Sus ecuaciones normales:

$$(J^\top J)\,\boldsymbol\delta = J^\top \mathbf{r}$$

**El loop completo:**

1. Residuo: $\mathbf{r} = \mathbf{y} - \mathbf{f}(\mathbf{p})$
2. Jacobiano $J$ **evaluado en el $\mathbf{p}$ actual** (recalcular en cada vuelta)
3. Resolver $(J^\top J)\boldsymbol\delta = J^\top\mathbf{r}$ → un sistema como el 2×2 de la tabla
4. Actualizar $\mathbf{p} \leftarrow \mathbf{p} + \boldsymbol\delta$; cortar cuando $\lVert\boldsymbol\delta\rVert < \text{tol}$ (criterio sobre $\boldsymbol\delta$, **no** sobre el residuo)

Cada iteración es *"el sistema de la tabla, recalculado donde estás parado ahora"*. Cerca de la solución converge casi cuadráticamente (los dígitos correctos ~se duplican por vuelta).

## Nivel 5 — El puente al PVT (Checkpoint M0)

En el receptor: parámetros $\mathbf{p} = (x, y, z, c\,\delta t)$ y una observación por satélite. La fila $i$ del jacobiano de la pseudodistancia:

$$\text{fila } i = \big(\underbrace{-u_x^{(i)},\; -u_y^{(i)},\; -u_z^{(i)}}_{-\,\text{vector unitario receptor}\to\text{sat}},\; \underbrace{1}_{\text{reloj}}\big)$$

— el mismo vector unitario del Nivel 1 (con signo menos: si me acerco al satélite, la distancia baja). Esa matriz se llama **matriz de geometría** $G$, y su condicionamiento es el **DOP**.

> **Respuesta al Checkpoint M0** — *¿Por qué linealizar el PVT lo
> convierte en mínimos cuadrados iterativos y qué rol juega el jacobiano?*
> Las pseudodistancias son no lineales en la posición (raíz cuadrada).
> Linealizando alrededor de una posición aproximada, cada iteración se
> vuelve un problema lineal de mínimos cuadrados sobre la corrección
> $\boldsymbol\delta$: $(J^\top J)\boldsymbol\delta = J^\top\mathbf{r}$.
> El jacobiano es la matriz de geometría: sus filas (vectores unitarios
> receptor→satélite + un 1 para el reloj) codifican cómo un cambio de
> posición/reloj afecta cada pseudodistancia; su condicionamiento
> determina el DOP.

## Nivel 6 — Verificador en Python

El jacobiano se puede *medir* igual que una derivada: ritmo con pasito chico, columna por columna. Contra eso se chequea el analítico:

```python
import numpy as np

def jac_numerico(f, p, h=1e-6):
    p = np.asarray(p, float)
    f0 = np.asarray(f(p))
    J = np.zeros((f0.size, p.size))
    for j in range(p.size):
        dp = p.copy(); dp[j] += h
        J[:, j] = (np.asarray(f(dp)) - f0) / h   # ritmo en la dirección j
    return J

# modelo exponencial del Lab 0.2: f_i = p0 * exp(p1 * x_i)
x = np.array([0.0, 1.0, 2.0])
f = lambda p: p[0] * np.exp(p[1] * x)
p = np.array([2.0, 0.5])

J_num = jac_numerico(f, p)
J_ana = np.column_stack([np.exp(p[1]*x),            # ∂f/∂p0
                         p[0]*x*np.exp(p[1]*x)])    # ∂f/∂p1 (¡cadena!)
print(np.abs(J_num - J_ana).max())   # ~1e-6 o menor → ✓
```

## Ejercicios (con solución plegada)

**J-a.** Gradiente de $f(x,y)=\sqrt{x^2+y^2}$ en $(3,4)$, y qué representa.

<details><summary>Solución</summary>

$\nabla f = (x/f,\; y/f) = (0{,}6,\; 0{,}8)$ — el vector unitario que apunta del origen al punto. Análogo exacto de una fila de la matriz de geometría del PVT (con signo opuesto).
</details>

**J-b.** ¿Por qué Gauss-Newton resuelve la recta en UNA iteración?

<details><summary>Solución</summary>

Porque el jacobiano de un modelo lineal es constante ($J = A$): la linealización es exacta, la primera $\boldsymbol\delta$ aterriza en el óptimo, y la segunda iteración da $\boldsymbol\delta = 0$ por la ortogonalidad $A^\top\mathbf{r}=0$.
</details>

**J-c.** Gauss-Newton 1D para $x^2 = 9$ desde $x_0 = 2$.

<details><summary>Solución</summary>

Modelo $f(x)=x^2$, "observación" 9, jacobiano $f'(x) = 2x$. Paso: $\delta = \dfrac{9 - x^2}{2x}$.
$x_0=2:\; \delta = 5/4 \Rightarrow x_1 = 3{,}25$
$x_1=3{,}25:\; \delta = -0{,}2404 \Rightarrow x_2 = 3{,}0096$
$x_2:\; \delta = -0{,}00958 \Rightarrow x_3 = 3{,}0000153$
Los dígitos correctos se duplican por vuelta → convergencia cuadrática. ✓
</details>

## Relacionados

- [derivadas.md](derivadas.md) — las parciales que acá se apilan en matriz
- [Clase 0.2](../clase0.2-minimos-cuadrados/README.md) — ecuaciones normales y Gauss-Newton en el lab; esta nota es el porqué
- [repaso-autotests.md](repaso-autotests.md) — toda la cadena en auto-tests
- Siguiente: el lab de la 0.2 (Gauss-Newton sin `scipy.optimize`) y la clase 1.2 (PVT)
