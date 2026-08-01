# Soluciones — Visión global

## Lab-lite — mapeo del arco

Con los datos de la clase 0.4 en disco, la clasificación correcta:

| Archivo | Eslabón | Clase |
|---|---|---|
| `*.dat` (IQ) | señal | mod2 |
| `*_MO.rnx` | observable | 1.5, mod3 |
| `*_MN.rnx` | órbita (broadcast) | 1.3, 4.1 |
| `*ORB.SP3` | órbita (precisa) | 1.3, 4.1, 4.2 |
| `*CLK.CLK` | error/reloj | 1.5, 4.3 |

Censo esperado con lo bajado: 3 señal, 3 observable, 2 broadcast, 1 SP3, 1 CLK.

## E1 — ordenar en el arco

código C/A (**señal**, mod2) → Klobuchar (**error** iono, 3.1) → ecuación
de Kepler (**órbita**, 1.3) → Gauss-Newton (**PVT**, 1.5) → DOP (calidad
del PVT, 1.4). El orden causal: primero existe la señal, de ella salen
observables, se les quitan errores, se ubica el satélite por su órbita, y
recién ahí se resuelve el PVT; el DOP juzga qué tan bien quedó.

## E2 — redundancia

6 satélites = 6 ecuaciones, 4 incógnitas ($x,y,z,c\,\delta t$) → **2
grados de redundancia**. Sirven para *chequear* la solución: detectar un
satélite fallado (RAIM, 5.1) y hasta excluirlo (5.2). Sin redundancia la
solución es única pero **no verificable**.

## E3 — qué segmento falla

(a) tormenta solar en el trayecto → ninguno de los tres *falla*: es el
**medio de propagación** (error ionosférico, mod3). (b) efeméride vieja →
**segmento de control** (no renovó/subió a tiempo; caso Galileo 2019).
(c) cold start lento → **segmento usuario** (tu receptor buscando en
frío; lo mitiga A-GPS).

## F1 — tiempo de vuelo

$20\,200\,\text{km} / c \approx 67\,\text{ms}$. Un error de reloj de
1 µs → $c \times 10^{-6} \approx 300\,\text{m}$ de error de rango. Por eso
el reloj es la 4ª incógnita: 1 µs arruina la posición.

## F2 — uploads diarios

30 satélites × (24 h / 2 h) = 30 × 12 = **360 subidas de efeméride al
día** — trabajo continuo del segmento de control (en la práctica el ritmo
real es aún mayor; ver el censo del BRDC en 0.4).

## C1 — "pseudo"distancia

Porque no es una distancia geométrica: es una **medición de tiempo**
(× c) hecha con dos relojes imperfectos (satélite y receptor), más
propagación y ruido. El sesgo del reloj del receptor la corre a todas por
igual; por eso se estima como incógnita.

## C2 — control vs fetch_data.py

Ambos son la **tubería de órbitas y relojes**: el segmento de control los
*calcula y sube* a los satélites; `fetch_data.py` los *baja* (broadcast,
SP3, CLK) para que tus labs trabajen con lo mismo que usó el sistema. La
0.4 es tu segmento de control en miniatura.

## C3 — GNSS en una frase

"Satélites con relojes atómicos emiten una señal; tu receptor mide el
tiempo de vuelo a cuatro de ellos y resuelve a la vez dónde está y qué
hora es." (Cualquier variante que respete el arco y las 4 incógnitas es
válida.)

## Mini-simulacro

1. Espacial (emite señal), control (calcula/sube efeméride), usuario
   (resuelve PVT). 2. señal→observable→error→órbita→PVT. 3. la fase de
   portadora. 4. porque el sesgo de reloj del receptor es una 4ª
   incógnita. 5. Time: el receptor da tiempo sincronizado; la banca lo
   usa para *timestamps* legales y la red eléctrica para sincronizar fase.
