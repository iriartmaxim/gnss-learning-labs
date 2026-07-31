# Límites (lo mínimo para derivadas)

> **Para qué es esta nota** — Es el cimiento que aparece al fondo de
> [derivadas.md](derivadas.md): el "achicar el pasito a cero" ($h \to 0$).
> Un límite responde **"¿a qué valor se acerca la salida cuando la
> entrada se acerca a algo?"** — la herramienta que convierte una
> medición aproximada en un valor exacto. Enfoque: solo lo que hace
> falta para entender la derivada.

## Nivel 0 — La idea: acercarse sin necesidad de llegar

Un límite pregunta a dónde **se dirige** una función, no cuánto vale justo en el punto.

Analogía: vas manejando hacia el km 100. A medida que avanzás pasás por el 98, 99, 99,9, 99,99… El límite es **100** (hacia donde vas), aunque todavía no hayas llegado. La pregunta del límite es *"¿hacia qué número apunta esto?"*.

Notación: $\displaystyle \lim_{x \to 3} f(x)$ se lee *"el valor al que se acerca $f(x)$ cuando $x$ se acerca a 3"*.

## Nivel 1 — Con números: el caso fácil

$f(x) = 2x + 1$. ¿A qué se acerca cuando $x \to 3$? Me acerco con una tabla:

| $x$ | 2,9 | 2,99 | 2,999 | → | 3,001 | 3,01 |
|---|---|---|---|---|---|---|
| $f(x)$ | 6,8 | 6,98 | 6,998 | → | 7,002 | 7,02 |

Desde los dos lados, la salida apunta a **7**. Y acá no hay truco: como puedo *sustituir* $x = 3$ directamente ($2\cdot 3 + 1 = 7$), el límite es simplemente $f(3) = 7$.

$$\lim_{x\to 3} (2x+1) = 7$$

> **Nota** — Para funciones **continuas** en el punto, el límite = evaluar
> la función ahí (**sustitución directa**). De hecho esa es la definición
> de continuidad en $a$: $\lim_{x\to a} f(x) = f(a)$. El límite se pone
> interesante justo cuando la sustitución directa falla…

## Nivel 2 — El caso interesante: 0/0

Mirá esta función:

$$g(x) = \frac{x^2 - 9}{x - 3}$$

Si sustituyo $x = 3$: numerador $= 9 - 9 = 0$, denominador $= 3 - 3 = 0$. Queda $\frac{0}{0}$ → **indefinido**, la calculadora se queja. Pero, ¿a qué se *acerca*? Tabla:

| $x$ | 2,9 | 2,99 | 2,999 | → | 3,001 | 3,01 |
|---|---|---|---|---|---|---|
| $g(x)$ | 5,9 | 5,99 | 5,999 | → | 6,001 | 6,01 |

¡Apunta clarísimo a **6**! En $x=3$ la función tiene una **discontinuidad evitable** (un "hueco" en la gráfica: ese único punto no está definido), pero el límite existe y vale 6.

**Y se puede probar con álgebra** (sin tabla): el numerador se factorea $x^2 - 9 = (x-3)(x+3)$, así que

$$g(x) = \frac{(x-3)(x+3)}{x-3} = x + 3 \quad (\text{para } x \neq 3)$$

Simplificando el $(x-3)$ que causaba el $0/0$, queda $x+3$, que en $x=3$ da $\boxed{6}$.

$$\lim_{x\to 3} \frac{x^2-9}{x-3} = 6$$

## Nivel 3 — Por qué 0/0 no es cero, ni infinito, ni prohibido

$\frac{0}{0}$ se llama **indeterminado**: su valor *depende de qué funciones* generan esos ceros, y hay que investigarlo (factorizando o con una tabla). No es un error — es el corazón de todo el cálculo.

| forma | resultado |
|---|---|
| $\frac{5}{0}$ | explota (∞), no existe |
| $\frac{0}{5}$ | es $0$, sin drama |
| $\frac{0}{0}$ | **indeterminado**: puede dar cualquier cosa; hay que resolver el límite |

> **Importante** — **La derivada ES un 0/0 resuelto.** Toda derivada tiene
> esta pinta $\frac{0}{0}$ y el límite es lo que la vuelve un número
> concreto. Justo lo que sigue.

## Nivel 4 — Conexión con la derivada ($h \to 0$)

En [derivadas.md](derivadas.md) el "ritmo" sobre un pasito $h$ es:

$$\text{ritmo} = \frac{f(b+h) - f(b)}{h}$$

Cuando $h \to 0$: el numerador $\to 0$ (dos valores casi iguales se restan) **y** el denominador $\to 0$. Es un $\frac{0}{0}$. La **derivada** es ese límite:

$$f'(b) = \lim_{h\to 0}\frac{f(b+h) - f(b)}{h}$$

Con $f(b) = b^2$: el álgebra simplifica la $h$ problemática, igual que el $(x-3)$ de arriba:

$$\frac{(b+h)^2 - b^2}{h} = \frac{2bh + h^2}{h} = 2b + h \;\xrightarrow[h\to 0]{}\; 2b$$

En $h=0$ sería $\frac{0}{0}$; el límite lo resuelve y da exactamente $2b$. **Derivar = resolver este límite 0/0.**

## Nivel 5 — Verificador en Python

Un límite se "mide" acercándose; recordá que nunca se evalúa en el punto prohibido, solo se ronda:

```python
def limite(f, punto, desde=0.1):
    # me acerco desde ambos lados y miro a dónde apunta
    for h in [desde, desde/10, desde/100, desde/1000]:
        print(f"  x={punto-h:.4f} -> {f(punto-h):.5f}    x={punto+h:.4f} -> {f(punto+h):.5f}")

# el caso 0/0 del Nivel 2: apunta a 6 desde los dos lados
limite(lambda x: (x**2 - 9)/(x - 3), 3)

# la derivada de b^2 en b=3: el cociente apunta a 6 = 2*3
limite(lambda h: ((3+h)**2 - 3**2)/h, 0)
```

> **Hábito del path** — "No está aprendido hasta que corre en Python":
> cuando dudes de un límite, acercate con la tabla numérica y confirmá
> el valor al que apunta.

## Ejercicios (con solución plegada)

**L-a.** $\lim_{x\to 2}(3x - 1)$

<details><summary>Solución</summary>

Caso fácil (Nivel 1): se puede evaluar por sustitución directa. $3\cdot 2 - 1 = 5$.
</details>

**L-b.** $\lim_{x\to 4}\dfrac{x^2 - 16}{x - 4}$

<details><summary>Solución</summary>

Es $0/0$. Factoreo: $x^2-16 = (x-4)(x+4)$, simplifico el $(x-4)$ → queda $x+4$ → en $x=4$ da $\boxed{8}$.
</details>

**L-c.** El cociente de la derivada de $5b$: $\lim_{h\to 0}\dfrac{5(b+h) - 5b}{h}$

<details><summary>Solución</summary>

Numerador $= 5b + 5h - 5b = 5h$. Divido: $\frac{5h}{h} = 5$. No queda $h$ → límite $= 5$. (Por eso la derivada de una recta es constante.)
</details>

## Relacionados

- [derivadas.md](derivadas.md) — el siguiente escalón: la derivada es un límite $0/0$ resuelto
- [Clase 0.2](../clase0.2-minimos-cuadrados/README.md) — destino: donde se derivan y usan las ecuaciones normales
- [README.md](README.md) — mapa de la rampa y orden de estudio
