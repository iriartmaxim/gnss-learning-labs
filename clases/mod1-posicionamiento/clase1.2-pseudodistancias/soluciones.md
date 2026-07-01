# Clase 1.2 — Soluciones de los ejercicios sin código

> Regla de uso: primero en papel, después acá. Si la respuesta te sorprende,
> volvé a la teoría antes de seguir.

## Blancos (§4 del README)

- **B1.** 1 ms × c = 299 792.458 m ≈ **300 km**.
- **B2.** Vale cero porque el escenario es sintético y las pseudodistancias se
  generaron sin sesgo de satélite; en la clase 1.5 habrá que **corregirlo con
  af0/af1/af2 del mensaje de navegación** (más el término relativista).
- **B3.** Porque su sesgo **se estima como 4ª incógnita en cada época**: el
  hardware barato se compensa con matemática, no con un mejor reloj.
- **B4.** Vale **1**, porque $\partial P/\partial(c\,\delta t_r) = 1$ para
  cualquier satélite (el sesgo entra sumando igual en todas las mediciones).
- **B5.** Casi **singular / mal condicionada**; la solución se vuelve muy
  sensible al ruido — DOP alto (clase 1.4).

## E1 — Una iteración de Gauss-Newton en 2D

**a) Rangos y residuos desde $\mathbf{x}_0=(0,0)$, $b_0=0$:**

$$\rho_1 = \lVert(3,4)\rVert = 5,\quad \rho_2 = \lVert(-4,3)\rVert = 5,\quad \rho_3 = \lVert(0,-5)\rVert = 5$$

$$\delta P_i = P_i - (\rho_i + b_0) = 6 - 5 = 1 \quad \text{para los tres.}$$

**b) Unitarios receptor→satélite y matriz $G$** (filas $[-u_x, -u_y, 1]$):

$$\mathbf{u}_1 = (0.6,\,0.8),\quad \mathbf{u}_2 = (-0.8,\,0.6),\quad \mathbf{u}_3 = (0,\,-1)$$

$$G = \begin{bmatrix} -0.6 & -0.8 & 1 \\ 0.8 & -0.6 & 1 \\ 0 & 1 & 1 \end{bmatrix}$$

**c) Sistema $G\,\Delta = (1,1,1)^\top$, por eliminación:**

- (fila 2 − fila 1): $1.4\,\Delta x + 0.2\,\Delta y = 0 \Rightarrow \Delta y = -7\,\Delta x$
- (fila 3): $\Delta y + \Delta b = 1 \Rightarrow \Delta b = 1 + 7\,\Delta x$
- Sustituyendo en (fila 2): $0.8\,\Delta x + 4.2\,\Delta x + 1 + 7\,\Delta x = 1 \Rightarrow 12\,\Delta x = 0$

$$\boxed{\Delta = (0,\; 0,\; 1)} \quad\Rightarrow\quad \mathbf{x} = (0,0),\; b = 1$$

**d) ¿Por qué exacta en una iteración?** Porque $\mathbf{x}_0$ ya era la
posición verdadera: el único error estaba en $b$, y el modelo es
**exactamente lineal en $b$** — la linealización no aproxima nada, resuelve.
Corolario general: una vez que la posición converge, el reloj se ajusta en un
paso; por eso en la fig. 2 ambas curvas caen juntas.

## E2 — Conversiones de reloj

- **a)** $\delta t_r = 89\,940 / 299\,792\,458 = 3.0001\cdot10^{-4}$ s ≈ **300 µs**.
- **b)** 1 ppm = $10^{-6}$ s/s → $c \times 10^{-6}$ ≈ **300 m/s** de deriva de
  pseudodistancia. En 10 minutos sin re-estimar: 600 s × 300 m/s = **180 km**.
  (Por eso el sesgo se estima *en cada época*.)
- **c)** 1 ns ≈ **30 cm** · 1 µs ≈ **300 m** · 1 ms ≈ **300 km**.

## E3 — El error de 13.7 µs

- **a)** $13.7\cdot10^{-6} \times 299\,792\,458 = 4\,107$ m ≈ **4.1 km**.
- **b)** **Un solo satélite:** el error *no* es común → no lo absorbe
  $c\,\delta t_r$; sesga la posición (con la geometría del lab: ~3.5 km,
  experimento 4) y ensucia los residuos. **Todos por igual:** es un error de
  modo común → lo absorbe íntegro la incógnita $c\,\delta t_r$; la posición
  queda intacta pero el **tiempo estimado** queda corrido 13.7 µs. Esa
  asimetría es exactamente la moraleja del caso 2016 (§8 del README).

## Fermi

- **F1.** Altura MEO ~20 200 km → cenit: $2\cdot10^7 / 3\cdot10^8 \approx$
  **67 ms**; al horizonte la oblicua sube a ~25 800 km → **~86 ms**. Orden:
  décimas de décima de segundo (70–90 ms).
- **F2.** $10^{-12} \times 86\,400$ s ≈ 86 ns/día → × 0.3 m/ns ≈ **~26 m/día**.
  Por eso los relojes de los satélites se monitorean y corrigen desde tierra
  en forma continua.
- **F3.** Velocidad radial máxima de un MEO visto desde tierra ~0.9 km/s →
  $f_D = f\,v/c = 1575.42\,\text{MHz} \times 900/(3\cdot10^8) \approx$
  **±4.7 kHz**. De ahí la grilla de búsqueda de **±5 kHz** del Lab 2.2 (para
  receptor estático; con dinámica del receptor y deriva del oscilador se
  amplía).

## Mini-simulacro

1. $P = \rho + c(\delta t_r - \delta t^s) + I + T + \varepsilon$: distancia
   geométrica, sesgo de reloj del receptor (se estima), sesgo de reloj del
   satélite (se corrige del mensaje), retardo ionosférico, retardo
   troposférico, multipath + ruido. **[2 pts]**
2. $47\,\mu s \times \sim300$ m/µs ≈ **14.1 km** (exacto: 14 090 m). **[1 pt]**
3. **Falso.** Un error común a todos entra idéntico en cada ecuación → lo
   absorbe la incógnita $c\,\delta t_r$. Sesga el *tiempo* estimado, no la
   posición. **[1 pt]**
4. Porque $\partial P_i/\partial(c\,\delta t_r) = 1$ para todo $i$: el sesgo
   del receptor suma igual en todas las pseudodistancias. **[1 pt]**

## Caso 26-ene-2016 — respuestas razonadas

1. **Posicionamiento vs. timing.** El parámetro erróneo era la corrección
   GPS→UTC del mensaje. La solución PVT trabaja en *tiempo GPS*, coherente
   entre satélites → las pseudodistancias no se tocaron y la posición
   sobrevivió. Quien necesitaba **UTC** (telecom, broadcast, energía) aplicó
   la corrección envenenada y se corrió 13.7 µs. Errores de modo común y
   conversiones de escala de tiempo: dos lugares distintos donde te podés
   romper.
2. **¿RAIM?** No: RAIM mira la *consistencia entre pseudodistancias*, y acá
   eran consistentes. Lo detectó (en la práctica) la comparación contra
   fuentes independientes: alarmas de equipos con holdover, NTP/PTP contra
   otras referencias, y receptores multiconstelación comparando UTC(GPS)
   contra UTC(Galileo/otros). Moraleja de ingeniería de detección: la
   redundancia tiene que ser *de fuente*, no solo de sensor.
3. **Lectura SIEM.** El tiempo GNSS es una dependencia crítica más: merece
   reglas de detección propias (salto/deriva de offset contra NTP interno,
   correlación de alarmas de sincronismo entre sitios — un salto simultáneo
   multi-sitio huele a segmento espacial o spoofing regional, no a falla
   local) y figurar en el threat model como superficie de ataque (puente
   directo a la clase 6.4).
