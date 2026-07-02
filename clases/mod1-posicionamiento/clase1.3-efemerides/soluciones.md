# Soluciones — Clase 1.3

## Ejercicios a mano

**E1.** a = 5440.631² = 29 600 128 m ≈ 29 600 km.
T = 2π√(a³/μ) = 2π√(2.593e22 / 3.986e14) = 2π·8066 s = **50 680 s = 14 h 04 m**
(coincide con la clase 0.3). v ≈ 2πa/T ≈ 3.67 km/s.

**E2.** Con E₀ = M = 0.5: ΔE = e·sin(0.5)/(1−e·cos 0.5) ≈ 3.4e-4·0.479 ≈
**1.6e-4 rad**. La corrección es de orden *e*; cada iteración la reduce otro
factor ~e, así que con e ~ 1e-4 llegás a 1e-13 en ~3 pasos. Por eso Kepler
es "gratis" para GNSS (e < 0.02 en toda la constelación, fig. 2 de la 0.3).

**E3.** La longitud del nodo en ECEF es la inercial menos lo que rotó la
Tierra desde el origen de la semana: Ω_ECEF = Ω0 + Ω̇·tk − ω⊕·(tk + Toe) =
Ω0 + (Ω̇−ω⊕)·tk − ω⊕·Toe. Si omitís −ω⊕·Toe con Toe = 129 600 s, girás la
órbita ω⊕·Toe ≈ 9.45 rad (≈ 3.17 rad módulo 2π ≈ 181°): el satélite queda
**del otro lado de la Tierra**, error de decenas de miles de km. No es un
error sutil: es el clásico "mi satélite está en el océano equivocado".

## Fermi

**F1.** err ≈ v·Δt: 3.7 km/s × 1 ms = **3.7 m**; × 1 µs = **3.7 mm**.
Moraleja: el reloj de la efeméride importa tanto como la órbita (clase 1.5).

**F2.** Δn ≈ err/(r·tk) = 569 / (2.96e7 · 43 200) ≈ **4.4e-10 rad/s** —
mismo orden que el ΔN transmitido (2.7e-9): el envejecimiento es,
literalmente, el movimiento medio descalibrándose.

**F3.** Renovación ~3 h → ~8 ajustes/día/SV; medimos 2821/30 ≈ 94
registros/SV → ~12×: el mismo IODnav se re-emite continuamente y la red
IGS lo recolecta desde muchas estaciones. Registros ≠ ajustes distintos.

## Conceptuales

**C1.** 16 parámetros + dinámica dan posición *continua* en todo el
intervalo con precisión métrica; una tabla XYZ equivalente necesitaría
órdenes de magnitud más de bits y un interpolador en el receptor. La física
es el mejor compresor.

**C2.** El ajuste absorbe localmente las perturbaciones no keplerianas
(J2, Sol/Luna, presión de radiación). Fuera de la ventana esas fuerzas no
modeladas se acumulan — sobre todo along-track, que crece ~cuadrático con
el error de movimiento medio. La órbita no cambió: el *modelo local* caducó.

**C3.** OSNMA viaja en bits reservados de I/NAV en **E1-B** (con datos
duplicados en E5b). F/NAV (E5a) no lo lleva. Un receptor E5a-only puede
posicionar pero **no autenticar**: necesita al menos E1.

**C4.** El IODnav referenciado por la autenticación en curso. OSNMA liga
cada firma a datos concretos (IODnav incluido): mezclar un registro de otra
versión rompe la verificación aunque la órbita sea casi igual.

**C5.** (a) SP3 = centro de masa, broadcast = centro de fase de antena:
~1–2 m sistemáticos; (b) los relojes son productos distintos (CLK preciso
vs polinomio broadcast + BGD por mensaje). Además el SP3 tiene su propio
error (~2.5 cm), despreciable acá.

## Mini-simulacro

1. Ver cheat sheet / Parte B del lab.
2. 516 = 512+4 → **I/NAV E5b** con reloj I/NAV. Es contenido I/NAV válido,
   pero para *recibir* OSNMA hace falta E1-B (nuestro filtro didáctico usa
   el combinado 517).
3. ~**406 m**; domina **along-track** (el error de n·tk empuja al satélite
   "adelante/atrás" en su órbita; radial y cross quedan un orden abajo).
4. **FALSO.** GST y GPST son continuos (sin leap seconds); difieren < 50 ns
   y el offset (GGTO) se transmite en el propio mensaje.
