# Derivadas desde cero (lo mínimo para mínimos cuadrados)

> **Para qué es esta nota** — La escalera de prerrequisitos para entender
> la derivación de las ecuaciones normales de la
> [clase 0.2](../clase0.2-minimos-cuadrados/README.md). Son 4 ideas:
> **qué es una derivada → las 4 derivadas básicas → derivada parcial
> (congelar) → regla de la cadena**. Cada una con números antes que símbolos.

## La tabla de referencia (9 puntos)

Los ejemplos "reales" de esta nota usan este juego de datos y sus montones:

| | X | Y | X·Y | X² |
|---|---|---|---|---|
| | 7 | 2 | 14 | 49 |
| | 1 | 9 | 9 | 1 |
| | 10 | 2 | 20 | 100 |
| | 5 | 5 | 25 | 25 |
| | 4 | 7 | 28 | 16 |
| | 3 | 11 | 33 | 9 |
| | 13 | 2 | 26 | 169 |
| | 10 | 5 | 50 | 100 |
| | 2 | 14 | 28 | 4 |
| $\Sigma$ | **55** | **57** | **233** | **473** |

($n = 9$; el ajuste que sale al final: $m \approx -0{,}8425$, $b \approx 11{,}48$.)

## Nivel 0 — Qué ES una derivada (sin fórmulas)

La derivada responde una sola pregunta:

> **"Si muevo la entrada un poquito, ¿cuánto se mueve la salida?"**

- Auto: la **velocidad** es la derivada de la posición (cuánto se mueve el auto por cada segundo que pasa).
- Terreno: si $f(x)$ es la altura de una loma en el punto $x$, la derivada es la **pendiente** en ese punto: positiva = subiendo, negativa = bajando, **cero = punto plano (¡fondo del valle!)**.

Por eso "derivar e igualar a cero" encuentra mínimos: en el fondo del valle la pendiente es 0.

## Nivel 1 — Medir el ritmo con tablas (los 3 casos)

**Derivada = a qué ritmo cambia la salida cuando muevo la entrada.** El ritmo se puede *medir* con una tabla — las reglas son solo el resumen del patrón.

### Caso 1: constante, $f(b) = 9$

| $b$ | 1 | 2 | 5 | 100 |
|---|---|---|---|---|
| $f$ | 9 | 9 | 9 | 9 |

La salida no se mueve nunca → ritmo $= 0$. *"La derivada de una constante es 0"* = línea horizontal, pendiente cero.

### Caso 2: rampa, $f(b) = -6b$

| $b$ | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| $f$ | 0 | −6 | −12 | −18 |
| cambio por paso | — | **−6** | **−6** | **−6** |

Cada paso $+1$ de entrada, la salida baja 6 — **siempre igual**. Ritmo $= -6$. En general $c\cdot b$ cambia $c$ por paso → derivada $= c$.

### Caso 3: curva, $f(b) = b^2$ — el ritmo *cambia*

| $b$ | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| $f$ | 1 | 4 | 9 | 16 |
| cambio por paso | — | **+3** | **+5** | **+7** |

⚠️ El ritmo ya no es constante → la derivada no puede ser un número: **depende de dónde estés parado**. Se mide con un paso chiquito ($0{,}01$):

- en $b=3$: $\frac{9{,}0601 - 9}{0{,}01} = 6{,}01 \approx 6 = 2\cdot 3$
- en $b=5$: $\frac{25{,}1001 - 25}{0{,}01} = 10{,}01 \approx 10 = 2\cdot 5$

Patrón: parado en $b$, el ritmo es $2b$. *"La derivada de $b^2$ es $2b$"* = una **fórmula** que da la pendiente en cada punto.

## Nivel 2 — La tabla resumen + el verificador universal

| $f$ | $f'$ | Por qué (Nivel 1) |
|---|---|---|
| $7$ (constante) | $0$ | no cambia nunca |
| $b$ | $1$ | copia la entrada: 1 por paso |
| $c\cdot b$ (ej. $-6b$) | $c$ | cambia $c$ por paso |
| $b^2$ | $2b$ | ritmo que crece: $2b$ en el punto $b$ |

**Verificador universal** (para no creerle a nadie):
$$\text{ritmo en } x \;\approx\; \frac{f(x + 0{,}01) - f(x)}{0{,}01}$$

```python
def ritmo(f, x, h=0.001):
    return (f(x + h) - f(x)) / h

print(ritmo(lambda b: 9,     5))    # → 0.0    constante
print(ritmo(lambda b: -6*b,  5))    # → -6.0   rampa
print(ritmo(lambda b: b**2,  5))    # → ~10.0  = 2·5 ✓
print(ritmo(lambda b: b**2, 10))    # → ~20.0  = 2·10 ✓
```

> **Hábito del path** — cualquier derivada que te digan, verificala con
> `ritmo()` en dos o tres puntos.

## Nivel 2½ — Por qué es EXACTAMENTE 2b (justificación analítica)

Medir con $h = 0{,}01$ es **evidencia**, no **prueba**. La prueba: dejo el pasito como símbolo $h$, hago álgebra, y lo achico a cero. Se llama *definición de derivada*:

$$f'(b) = \lim_{h\to 0}\frac{f(b+h) - f(b)}{h}$$

Para $f(b) = b^2$, usando el **binomio** $(b+h)^2 = b^2 + 2bh + h^2$:

$$\frac{(b+h)^2 - b^2}{h} = \frac{b^2 + 2bh + h^2 - b^2}{h} = \frac{2bh + h^2}{h} = 2b + h \;\xrightarrow[h\to 0]{}\; \boxed{2b}$$

**El "ruido" del 6,01 era el $h$.** El ritmo medido es $2b + h$; en $b=3$, $h=0{,}01$: $\;2(3)+0{,}01 = 6{,}01$. Al achicar $h$, se pega al 6 exacto:

| $h$ | $2(3)+h$ |
|:---:|:---:|
| $0{,}1$ | $6{,}1$ |
| $0{,}01$ | $6{,}01$ |
| $0{,}001$ | $6{,}001$ |
| $\to 0$ | $\mathbf{6}$ |

**Por qué las rectas no tienen ruido** (mismo método):
$$\frac{5(b+h)-5b}{h} = \frac{5h}{h} = 5 \quad (\text{no queda } h) \qquad\qquad \frac{7-7}{h} = 0$$

La recta y la constante dan exacto con cualquier paso; la parábola deja un $h$ → por eso su medición tiene "ruido". Se demuestra **una vez** por pieza; después se usan las reglas sin re-derivar.

## Nivel 3 — Derivar una suma: por pedazos

La derivada de una suma es la suma de las derivadas. Cada término se deriva solo:

$$x^2 + 5x + 7 \;\;\xrightarrow{\ \text{derivo}\ }\;\; \underbrace{2x}_{x^2} + \underbrace{5}_{5x} + \underbrace{0}_{7}$$

Esto es lo que nos deja "meter la derivada adentro de la $\Sigma$": una sumatoria es solo una suma larga.

> **No confundir $b^2$ con $2b$**
>
> | escribo | qué es | derivada |
> |:---:|:---|:---:|
> | $b^2 = b\times b$ | parábola | $2b$ |
> | $2b = 2\times b$ | recta | $2$ |
>
> La derivada **de** $b^2$ *es* $2b$; la derivada **de** $2b$ es $2$. Son piezas distintas.

### Las 2 reglas para combinar piezas

**Regla 1 — un número multiplicador va de acompañante:** derivo la parte con $b$, el número queda adelante.
$$3b^2 \to 3\cdot 2b = 6b \qquad 5b \to 5\cdot 1 = 5$$

**Regla 2 — una suma se deriva pedazo por pedazo:**
$$b^2 + 5b + 7 \to \underbrace{2b}_{b^2} + \underbrace{5}_{5b} + \underbrace{0}_{7} = 2b+5$$

## Banco de práctica (escalones 2–3, sin cadena)

Tapá las soluciones, resolvé, comparás. Solo usan la tabla de 4 piezas + las 2 reglas.

**Serie A — una pieza:** A1) $6$ · A2) $b$ · A3) $9b$ · A4) $b^2$ · A5) $-4b$ · A6) $-b$ · A7) $100$

**Serie B — recta vs parábola** (decí cuál es y derivá): B1) $b^2$ · B2) $2b$ · B3) $7b$ · B4) $10$

**Serie C — sumas:** C1) $3b+4$ · C2) $b^2+5b$ · C3) $b^2-8b$ · C4) $b^2+10b+25$ · C5) $b^2-4b+4$ · C6) $5b-7$

**Serie D — acompañante en $b^2$:** D1) $3b^2$ · D2) $2b^2+4b$ · D3) $5b^2-3b+2$

<details><summary>Soluciones</summary>

**A:** $0$ · $1$ · $9$ · $2b$ · $-4$ · $-1$ · $0$
**B:** parábola $2b$ · recta $2$ · recta $7$ · constante $0$
**C:** $3$ · $2b+5$ · $2b-8$ · $2b+10$ · $2b-4$ · $5$
**D:** $6b$ · $4b+4$ · $10b-3$
</details>

> **Verificá cualquiera con Python (Nivel 2)** — Ej. C5 en $b=3$: la
> derivada $2b-4$ da $2$. Comprobá: `ritmo(lambda b: b**2 - 4*b + 4, 3)` → $\approx 2$ ✓

## Nivel 4 — Derivada parcial: congelar la otra variable

$S(m, b)$ tiene **dos** entradas. La derivada **parcial** $\dfrac{\partial}{\partial b}$ significa: *derivo respecto de $b$, y todo lo que no sea $b$ lo trato como un número congelado* (como el 7 de la tabla).

Ejemplo: $g(m, b) = 3m + 2b$. Para $\partial g/\partial b$, congelá $m$ (imaginá $m = 10$):

$$g = \underbrace{30}_{\text{constante} \to 0} + 2b \;\;\xrightarrow{\ \partial/\partial b\ }\;\; 0 + 2 = 2$$

Tabla de práctica (todo respecto de $b$):

| expresión | $\partial/\partial b$ | por qué |
|---|---|---|
| $y_i$ | $0$ | es un dato (número), no contiene $b$ |
| $m \cdot x_i$ | $0$ | ¡tampoco contiene $b$! ($m$ y $x_i$ están congelados) |
| $b$ | $1$ | es la variable |
| $-b$ | $-1$ | constante $(-1)$ por la variable |

## Nivel 5 — La regla de la cadena (la única difícil)

Para derivar $(\text{algo})^2$ cuando el "algo" no es simplemente $x$. La receta:

> **cáscara y relleno**: derivá la cáscara $(\square)^2 \to 2(\square)$
> dejando el relleno intacto, y después **multiplicá por la derivada del
> relleno**.

$$\frac{d}{db}\Big[(\text{relleno})^2\Big] = 2 \cdot (\text{relleno}) \cdot \underbrace{(\text{relleno})'}_{\text{¡el peaje!}}$$

**Red de seguridad** — verifiquemos que da lo mismo que el camino largo, con $(3-b)^2$:

*Camino largo (expandir, sin cadena):*
$$(3-b)^2 = 9 - 6b + b^2 \;\;\xrightarrow{\ \text{Niveles 2 y 3}\ }\;\; 0 - 6 + 2b = \boxed{2b - 6}$$

*Camino corto (cadena):*
$$(3-b)^2 \;\;\xrightarrow[\text{relleno intacto}]{\ \text{cáscara: } 2(\square)\ }\;\; 2(3-b) \;\;\xrightarrow{\ \times\ (3-b)' = -1\ }\;\; -2(3-b) = \boxed{2b - 6}$$

✅ **Idénticos.** La cadena es solo un atajo para no expandir. Con los 9 términos de la tabla de referencia, expandir todo sería un infierno — por eso existe la cadena.

## Nivel 6 — Un término REAL de la tabla

Punto 1 de la tabla: $(x_1, y_1) = (7, 2)$. Su término en $S$ es $(2 - 7m - b)^2$.

**Respecto de $b$:**
$$(2 - 7m - b)^2 \;\xrightarrow{\ \text{cáscara}\ }\; 2\,(2 - 7m - b) \;\xrightarrow{\ \times\ (0 - 0 - 1)\ }\; -2\,(2 - 7m - b)$$

**Respecto de $m$** (misma cáscara, cambia el peaje):
$$(2 - 7m - b)^2 \;\xrightarrow{\ \text{cáscara}\ }\; 2\,(2 - 7m - b) \;\xrightarrow{\ \times\ (0 - 7 - 0)\ }\; -14\,(2 - 7m - b)$$

El peaje respecto de $m$ es $-x_i$ (acá $-7$): por eso en la segunda ecuación normal aparece una $x_i$ multiplicando.

## Nivel 7 — S entera: sumar los 9 términos

$$S = (2-7m-b)^2 + (9-1m-b)^2 + \dots + (14-2m-b)^2$$

Nivel 3: derivo término a término. Cada uno aporta $-2(y_i - mx_i - b)$:

$$\frac{\partial S}{\partial b} = -2(2-7m-b) -2(9-m-b) - \dots = -2\sum_i (y_i - mx_i - b)$$

Igualo a $0$ y divido ambos lados por $-2$ (por eso "se cancela"):

$$\sum_i (y_i - mx_i - b) = 0$$

Reparto la $\Sigma$ con cuidado — **acá vive el error clásico**:

$$\underbrace{\sum y_i}_{57} - m\underbrace{\sum x_i}_{55} - \underbrace{(b + b + \dots + b)}_{9 \text{ veces} \;=\; 9b} = 0 \;\Longrightarrow\; \boxed{\sum y = m \sum x + n\,b}$$

Y respecto de $m$, cada término trae su peaje $-x_i$:

$$\sum_i x_i (y_i - mx_i - b) = 0 \;\Longrightarrow\; \boxed{\sum xy = m \sum x^2 + b \sum x}$$

Estas dos cajas son las **ecuaciones normales** → el despeje, la versión
matricial y todo lo que sigue vive en la
[clase 0.2](../clase0.2-minimos-cuadrados/README.md). Con la tabla de
referencia el sistema da $m \approx -0{,}8425$, $b \approx 11{,}48$.

## Ejercicios (con solución plegada)

**E-a.** $\dfrac{d}{db}(4-b)^2$

<details><summary>Solución</summary>

Cáscara: $2(4-b)$. Peaje: $(4-b)' = -1$. Total: $-2(4-b) = 2b - 8$.
Verificación expandiendo: $(4-b)^2 = 16 - 8b + b^2 \to -8 + 2b$ ✓
</details>

**E-b.** $\dfrac{\partial}{\partial m}(5-2m)^2$

<details><summary>Solución</summary>

Cáscara: $2(5-2m)$. Peaje: $(5-2m)' = -2$. Total: $-4(5-2m) = 8m - 20$.
</details>

**E-c.** $\dfrac{\partial}{\partial b}\,(y_3 - m x_3 - b)^2$ con $(x_3, y_3) = (10, 2)$

<details><summary>Solución</summary>

Cáscara: $2(2 - 10m - b)$. Peaje respecto de $b$: $-1$. Total: $-2(2 - 10m - b)$.
¿Y respecto de $m$? Peaje $-10$: total $-20(2 - 10m - b)$.
</details>

## Relacionados

- [limites.md](limites.md) — el escalón previo: la derivada es un límite $0/0$ resuelto (Nivel 2½)
- [Clase 0.2](../clase0.2-minimos-cuadrados/README.md) — donde se usa todo esto
- [jacobiano-y-linealizacion.md](jacobiano-y-linealizacion.md) — el siguiente escalón: estas mismas parciales, organizadas en una matriz (una por parámetro y por observación)
- [README.md](README.md) — mapa de la rampa y orden de estudio
