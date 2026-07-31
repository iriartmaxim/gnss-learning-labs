# Repaso por componentes — de Límites al PVT

> **Cómo usar esta nota** — Cada componente tiene: la idea en una frase,
> la fórmula clave, y un **test plegado**. El método: leé el test,
> **respondé en voz alta o en papel**, y recién ahí desplegá. Si sale
> fluido → ✅ y seguís. Si no → volvés a la nota fuente (linkeada). No
> releer de corrido: **recuperar, no reconocer**.

```
A. Límites → B. Álgebra → C. Derivadas → D. Varias variables → E. Mínimos cuadrados → F. Jacobiano/GN
```

---

## Bloque A — Límites ([limites.md](limites.md))

### A1. Qué es un límite

**Idea:** a dónde *se dirige* la salida cuando la entrada se acerca a algo — sin necesidad de llegar (el km 100).
$$\lim_{x\to 3}(2x+1) = 7$$

<details><summary><b>Test:</b> ¿por qué para funciones <b>continuas</b> el límite = <b>evaluar en el punto</b> (sustitución directa)? ¿Cuándo NO alcanza con sustituir?</summary>

Continuidad en $a$ significa exactamente $\lim_{x\to a} f(x) = f(a)$: el valor al que se acerca ES el valor en el punto. No alcanza cuando la sustitución da $\frac{0}{0}$ — típicamente una **discontinuidad evitable** (el "hueco"): el límite puede existir igual, pero hay que *resolverlo* factorizando.
</details>

### A2. El caso 0/0

**Idea:** $\frac{0}{0}$ es **indeterminado** — no es error ni cero ni infinito: depende de *qué funciones* generan esos ceros. Se resuelve con álgebra (factorizar y cancelar).

<details><summary><b>Test:</b> resolvé $\lim_{x\to 4}\frac{x^2-16}{x-4}$</summary>

$x^2-16 = (x-4)(x+4)$ → cancelo $(x-4)$ → queda $x+4$ → **8**.
</details>

---

## Bloque B — Herramientas de álgebra (de apoyo)

### B1. La cajita (binomio)

**Idea:** $(b+h)^2$ = multiplicar TODO con TODO — el exponente no se reparte.
$$(b+h)^2 = b^2 + 2bh + h^2 \qquad (b+h)^3 = b^3 + 3b^2h + 3bh^2 + h^3$$

<details><summary><b>Test:</b> ¿por qué $(b+h)^2 \neq b^2 + h^2$? ¿De dónde sale el $2bh$?</summary>

Porque $(b+h)^2 = (b+h)(b+h)$: 4 productos. El $2bh$ son las DOS casillas cruzadas ($bh$ y $hb$). Chequeo: $3{,}1^2 = 9 + 0{,}6 + 0{,}01 = 9{,}61$.
</details>

### B2. Factor común

**Idea:** sacar afuera **lo que TODOS los términos comparten** (y solo eso). Con restas: el signo viaja pegado a su término.
$$2bh + h^2 = h(2b+h) \qquad 3-x = -(x-3)$$

<details><summary><b>Test:</b> en $\partial S/\partial m$ los términos son $-14(\ldots), -2(\ldots), -20(\ldots)$. ¿Qué se puede sacar de factor común y qué NO?</summary>

Solo el $-2$ (está en todos). Los $x_i$ (7, 1, 10…) son distintos → se quedan adentro, pegados a su paréntesis. Por eso la 2ª ecuación normal tiene $\sum xy$ y $\sum x^2$.
</details>

### B3. Diferencia de cuadrados

$$a^2 - b^2 = (a-b)(a+b) \quad \text{(solo con RESTA)}$$

<details><summary><b>Test:</b> ¿por qué los términos cruzados desaparecen acá y en la cajita se suman?</summary>

$(a-b)(a+b)$: los cruzados son $+ab$ y $-ab$ → se cancelan. En $(b+h)^2$ son ambos positivos → se suman en $2bh$.
</details>

---

## Bloque C — Derivadas ([derivadas.md](derivadas.md))

### C1. Qué es la derivada (el velocímetro)

**Idea:** la derivada es la **tasa de variación instantánea**: el límite del **cociente incremental** (la tasa de variación media sobre un intervalo de ancho $h$) cuando el **incremento** $h \to 0$. La derivada ES un $\frac{0}{0}$ resuelto.
$$f'(b) = \lim_{h\to 0}\frac{f(b+h)-f(b)}{h}$$

<details><summary><b>Test:</b> ¿por qué el cociente es $\frac{0}{0}$ en $h=0$, y qué lo "salva"?</summary>

Numerador y denominador → 0 juntos. El álgebra (cajita + factor común) cancela la $h$ del denominador; después se puede hacer $h\to 0$ tranquilo: **muere lo que lleva $h$, sobrevive lo que no**.
</details>

### C2. El incremento $h$ se aplica a la variable independiente

**Idea:** el incremento afecta al **argumento** de la función: se evalúa $f(m+h)$ (la función en la variable incrementada). Nunca $f(m)+h$ — eso incrementa la **imagen** (la salida), que es otra cosa.

<details><summary><b>Test:</b> ¿por qué $\frac{(mx+h)-mx}{h} = 1$ está mal para derivar $mx$ respecto de $m$?</summary>

Incrementó la **imagen** en vez del argumento. Correcto: $\frac{(m+h)x - mx}{h} = \frac{hx}{h} = x$. El incremento acompaña a la variable independiente: $(m+h)x$.
</details>

### C3. Las 4 piezas + 2 reglas

| $f$ | $f'$ |
|---|---|
| constante | $0$ |
| $x$ | $1$ |
| $c\cdot x$ | $c$ |
| $x^2$ | $2x$ |

**Regla 1:** el multiplicador acompaña ($3x^2 \to 6x$). **Regla 2:** suma = término a término.

<details><summary><b>Test</b> (la escalera clásica): derivá $7x$, $4x^2$, $x^2+3x$, $x^3$</summary>

$7$ · $8x$ · $2x+3$ · $3x^2$. (El cubo: $(b+h)^3$ → sobreviven $3b^2$; coeficientes 1,3,3,1.)
</details>

---

## Bloque D — Varias variables ([derivadas.md](derivadas.md) N4–N5)

### D1. Derivada parcial (congelar)

**Idea:** $\partial/\partial b$ = derivo respecto de $b$ tratando **toda otra letra como número congelado**. La parcial DERIVA, no selecciona.

| el congelado está… | qué le pasa |
|---|---|
| **sumando** ($b$ en $7m+b$, resp. de $m$) | muere → 0 |
| **multiplicando** ($y$ en $2xy$, resp. de $x$) | queda de acompañante → $2y$ |

<details><summary><b>Test:</b> $g = x^2 + 3xy + y^2$: las dos parciales</summary>

$\partial g/\partial x = 2x + 3y$ · $\partial g/\partial y = 3x + 2y$. Detector: en $\partial/\partial x$ sobrevive el $2x$ (la viva); el congelado que multiplica queda ($3y$); el $y^2$ muere.
</details>

### D2. Regla de la cadena (el apodo $u$)

**Idea:** para $(\text{algo})^2$: variable intermedia $u$ = el algo. Derivo la externa ($u^2 \to 2u$), multiplico por la derivada de la interna, y AL FINAL sustituyo el apodo.
$$\frac{dT}{db} = \frac{dT}{du}\cdot\frac{du}{db}$$

**⚠️ Los dos roles:** $u$ = la expresión (viaja entera, vuelve como paréntesis) · $u'$ = el multiplicador (entra UNA vez).

<details><summary><b>Test:</b> $\dfrac{\partial}{\partial m}(2-7m-b)^2$, pasos completos</summary>

$u = 2-7m-b$ · $\partial u/\partial m = -7$ · externa: $2u$ · producto: $2u\cdot(-7) = -14u = -14(2-7m-b) = -28+98m+14b$. ✓
</details>

---

## Bloque E — Mínimos cuadrados ([clase 0.2](../clase0.2-minimos-cuadrados/README.md))

### E1. El problema y la S

**Idea:** más ecuaciones que incógnitas + ruido → no hay solución exacta → busco la que minimiza la suma de residuos al cuadrado. Mínimo = fondo del valle = **pendiente cero en las dos direcciones**.
$$S(m,b) = \sum_i (y_i - mx_i - b)^2 \qquad \frac{\partial S}{\partial b} = 0, \;\; \frac{\partial S}{\partial m} = 0$$

### E2. Las ecuaciones normales (los montones)

**Idea:** derivo cada término (cadena), sumo los 9, saco el $-2$, distribuyo, y agrupo por especie: montón de $y$, montón de $m$, montón de $b$.
$$\sum y = m\sum x + nb \qquad\qquad \sum xy = m\sum x^2 + b\sum x$$

<details><summary><b>Test:</b> ¿por qué la 2ª ecuación tiene $\sum xy$ y $\sum x^2$ y la 1ª no?</summary>

Porque $\partial u/\partial m = -x_i$ (acompañante congelado): cada término trae SU $x_i$ pegado, que no sale de factor común y se distribuye adentro → los montones quedan multiplicados por $x_i$. Las columnas X·Y y X² de la tabla SON esos montones.
</details>

### E3. Resolver el sistema (sustitución)

**Idea:** despejo $b$ de la 1ª → lo **sustituyo** entero en la 2ª → una ecuación con una incógnita → $m$ → vuelvo por $b$.

<details><summary><b>Test:</b> con $\sum x=55, \sum y=57, \sum xy=233, \sum x^2=473, n=9$: ¿qué da?</summary>

$m = -1038/1232 \approx -0{,}8425$, $b \approx 11{,}48$. Recta: $\hat y = 11{,}48 - 0{,}84x$. Verificación: $473m + 55b \approx 233$ ✓
</details>

---

## Bloque F — Jacobiano y Gauss-Newton ([jacobiano-y-linealizacion.md](jacobiano-y-linealizacion.md))

### F1. Gradiente

**Idea:** las parciales de UNA función, empaquetadas en un vector. Un velocímetro por dirección.
$$\nabla g = \left(\tfrac{\partial g}{\partial x},\, \tfrac{\partial g}{\partial y}\right) \qquad \text{ej: } \nabla(3x^2+2xy) = (6x+2y,\; 2x)$$

### F2. Jacobiano

**Idea:** **gradientes apilados** — fila = observación, columna = parámetro. (No al revés: gradiente = un renglón; jacobiano = el edificio.)
$$J_{\text{recta}} = \begin{bmatrix} 7 & 1 \\ 1 & 1 \\ 10 & 1 \end{bmatrix} = A \;\;\text{(¡la matriz de diseño!)}$$

<details><summary><b>Test:</b> ¿cuál es la "firma" de un modelo lineal en su jacobiano, y qué implica?</summary>

$J$ contiene solo datos (ni $m$ ni $b$ adentro) → vale en TODOS lados → un solo despeje basta. No lineal: las parciales contienen los parámetros → $J$ es foto local → iterar. (Rampa vs parábola, un piso arriba.)
</details>

### F3. Linealización (ritmo × pasito)

$$f(p_0+\delta) \approx f(p_0) + J\delta \qquad \text{error} \approx h^2 \text{ (el cuadradito descartado de la cajita)}$$

<details><summary><b>Test:</b> $f(p)=p^2$ en $p_0=3$, paso $0{,}5$: predicción, realidad, error</summary>

Predicción: $9 + 6\cdot 0{,}5 = 12$. Realidad: $3{,}5^2 = 12{,}25$. Error: $0{,}25 = h^2$ ✓. Comparado con $h=0{,}1$ (error $0{,}01$): paso 5× más grande → error 25× — por eso GN falla si arrancás lejos.
</details>

### F4. Gauss-Newton (el juego del GPS)

**Idea:** *¿cuánto falta? ÷ ¿a qué ritmo voy? → paso → repetir desde donde caí.* El "÷ ritmo" en matricial son las ecuaciones normales recicladas:
$$(J^\top J)\,\delta = J^\top r \qquad r = \text{medido} - \text{predicho}$$

**⚠️ $\delta$ mueve la ENTRADA** ($p \leftarrow p + \delta$), nunca se mezcla con la salida (el objetivo 9 vive en otro mundo).

<details><summary><b>Test:</b> $p^2=9$ desde $p_0=2$: hacé 2 vueltas de memoria</summary>

V1: $r=5$, $J=4$, $\delta=1{,}25$ → $p_1 = 3{,}25$. V2: $r=-1{,}5625$, $J=6{,}5$, $\delta=-0{,}2404$ → $p_2 = 3{,}0096$. Dígitos correctos se duplican por vuelta (cuadrática).
</details>

### F5. El PVT y la matriz de geometría G

**Idea:** 4 incógnitas $(x,y,z,c\delta t)$, una fila de $G$ por satélite:
$$\text{fila}_i = (\underbrace{-u_x, -u_y, -u_z}_{\text{vector unitario hacia el sat}},\; \underbrace{1}_{\text{reloj}})$$

$G$ = el **traductor** entre "metros que faltan" (mediciones) y "paso a dar" (incógnitas). El 1 del reloj = columna de unos = "la ordenada al origen del GNSS". Satélites agrupados → filas parecidas → mal condicionamiento → **DOP**.

<details><summary><b>Test:</b> ¿por qué la parcial respecto de $c\delta t$ es exactamente 1, y por qué hacen falta ≥4 satélites?</summary>

$\rho = \text{raíz} + \tau$: la raíz no tiene $\tau$ (→0) y $\tau$ solo → 1. El error de reloj afecta TODAS las mediciones por igual. 4 columnas = 4 incógnitas → mínimo 4 filas (satélites).
</details>

### F6. Checkpoint M0 (el jefe final)

<details><summary><b>Test:</b> ¿por qué linealizar el PVT lo convierte en mínimos cuadrados iterativos, y qué rol juega el jacobiano en cada iteración?</summary>

La pseudodistancia tiene raíz → no lineal → $J$ foto local, no hay despeje único. Linealizando, cada vuelta es un LS **lineal** en $\delta$: $(G^\top G)\delta = G^\top r$ (las ecuaciones normales de siempre). El ritmo no es exacto lejos ($\sim h^2$) → recalcular $G$ y repetir hasta $\delta$ diminuto. $G$ = matriz de geometría: vectores unitarios a los satélites + 1 del reloj; traduce residuos→paso; su condicionamiento es el DOP.
</details>

---

## Cierre del repaso

- Si todos los tests salen sin mirar → el bloque teórico del Módulo 0 está **consolidado**: seguir con el lab de la [clase 0.2](../clase0.2-minimos-cuadrados/README.md) (Gauss-Newton sin `scipy.optimize`).
- Si alguno traba → ir a la nota fuente del bloque y rehacer solo ese ejercicio.

## Relacionados

- [README.md](README.md) — el mapa general de la rampa
- [limites.md](limites.md) · [derivadas.md](derivadas.md) · [jacobiano-y-linealizacion.md](jacobiano-y-linealizacion.md) — las notas fuente
- [Clase 0.2](../clase0.2-minimos-cuadrados/README.md) — lo que se destraba al cerrar esto
