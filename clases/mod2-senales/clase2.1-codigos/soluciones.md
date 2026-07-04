# Soluciones — Clase 2.1

## Ejercicios a mano

**E1.** Un LFSR de n etapas tiene 2ⁿ estados posibles, pero el estado
todos-ceros es absorbente (XOR de ceros da cero: se queda clavado para
siempre). Un polinomio primitivo recorre **todos** los demás →
2¹⁰ − 1 = 1023. Por eso la semilla es todos-unos (cualquier no-cero
sirve; el estándar fija esa).

**E2.** Aislación = 20·log₁₀(65/1023) = **−23.9 dB**. Si un transmisor
llega ~24 dB más fuerte (×250 en potencia, ~×16 más cerca a igual EIRP),
su *cruzada* empata tu *pico* y el receptor puede engancharse al PRN
equivocado. Ese es el problema **near-far**: la garantía Gold es
relativa a potencias parecidas — y es exactamente el margen que un
jammer o spoofer barato explota transmitiendo desde cerca.

**E3.** chip = c/1.023 MHz = **293.1 m**. El receptor no "cuenta chips":
el pico de correlación es un triángulo de ±1 chip de base, y un
discriminador early–late (clase 2.3) ubica el vértice interpolando a
~1% del chip → metros. La regla es gruesa; la puntería sobre la regla
es fina.

## Fermi

**F1.** 1.023 Mcps / 50 bps = **20 460 chips por bit** = **20 códigos
completos** por bit. Por eso podés integrar coherente 1 ms sin mirar los
datos, y por eso el bit se detecta como un cambio de signo entre códigos.

**F2.** SNR pre-correlación ≈ −130 − (−111) = **−19 dB** (la señal está
enterrada). Ganancia de procesamiento +30.1 dB → SNR post ≈ **+11 dB**:
alcanza, con ~10 dB de margen para pérdidas de implementación. GNSS
funciona *debajo* del ruido — todo el mérito es de la correlación.

**F3.** Eligiendo (búsqueda computacional, como Galileo) ganás
propiedades a medida: mejores cruzadas para el largo elegido (4092),
balance exacto, comportamiento con Doppler. Perdés la generación
on-the-fly: el receptor debe **almacenar** ~50 × 4092 chips por
componente (trivial hoy, carísimo en los 70 — por eso GPS eligió LFSR).

## Conceptuales

**C1.** Porque la cruzada de dos m-secuencias preferidas desfasadas se
reduce a evaluar una suma sobre estructura algebraica cerrada (trazas en
GF(2¹⁰)): solo puede caer en {−t, −1, t−2} con t = 65. No es ruido — es
álgebra con uniforme de ruido.

**C2.** La semilla fija el desfase inicial de la secuencia (qué "vuelta"
del ciclo ves). Todos-unos es una convención del estándar para que todos
los receptores generen la misma fase; cualquier estado no nulo genera la
misma secuencia rotada.

**C3.** El código es periódico (se repite cada 1 ms), así que el desfase
es circular por naturaleza. Y la correlación circular es diagonal en
Fourier: `IFFT(FFT(a)·conj(FFT(b)))` calcula los 1023 desfases en
O(N log N). En la 2.2 esa identidad *es* el algoritmo de adquisición.

**C4.** Sin bits que puedan cambiar de signo, el piloto E1-C permite
integración coherente larga (decenas de ms) → detectar señales mucho más
débiles y mantener tracking robusto. El precio: gastar la mitad de la
potencia en un canal "mudo" (con código secundario de 25 chips).

**C5.** OSNMA autentica el **contenido** del mensaje (efemérides, reloj)
con TESLA: te garantiza que los *datos* los firmó el sistema. No
autentica el **rango**: un meaconer que retransmite señal auténtica con
retardo controlado pasa OSNMA. Por eso existe la línea complementaria a
nivel señal (ACAS/E6-C) y los detectores de consistencia del módulo 6.

## Mini-simulacro

1. G1 desde [1,1,1,1,1,1,1,1,1,1]: salida = etapa 10 = **1**;
   realimentación = e3⊕e10 = 1⊕1 = 0 → entra 0. Segunda salida: **1**
   (el 1 que estaba en la etapa 9), realim 1⊕1=0. Tercera: **1**.
   (La salida C/A completa arranca 1100100000 = 1440₈ porque se XORea
   con G2; la salida de G1 sola arranca 111...)
2. **F.** El set es {−65, −1, 63}: el 0 no está. Dos C/A nunca son
   perfectamente ortogonales — son "suficientemente" ortogonales.
3. 20·log₁₀(65/1023) = **−23.9 dB**.
4. Sin transiciones de datos, el receptor integra coherente mucho más de
   1 ms sin riesgo de que un bit le dé vuelta el signo a mitad de suma →
   más sensibilidad y un lazo de portadora más limpio.
