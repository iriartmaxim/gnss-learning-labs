# Soluciones — Clase 6.4 (detectores)

Series sintéticas deterministas. El lab termina en "DETECTORES OK".

## Lab

| Métrica | Referencia |
|---|---|
| Falsa alarma (datos limpios) | 0.5 % |
| Detección (durante el ataque) | 100 % |
| Latencia | 0 s |

**TODO 1:** `return m > base + k`. **TODO 2:** `return np.abs(dgps_gal) > umbral`.

**Hallazgo honesto:** en este escenario el ataque es **gradual**; los
detectores de *tasa* (2ª diferencia del reloj, salto de velocidad) NO
disparan (una rampa tiene aceleración ~0). Los que lo cazan son el **salto
de C/N0** y el **cruce GPS/Galileo**. Moraleja: ningún detector solo
alcanza; se combinan varios + criptografía (6.1). Un spoofer sofisticado
que iguale potencia y sea coherente entre constelaciones evade a los
físicos — por eso OSNMA.

## E1 — por qué el C/N0 delata

Para "ganar" el correlador auténtico, el spoofer debe llegar más fuerte →
sube el C/N0. Un salto de varios dB simultáneo en muchos satélites es
antinatural (la geometría real cambia lento). Un spoofer que iguale
potencia exactamente evade este detector, pero es mucho más caro.

## E2 — por qué el cruce funciona

Falsificar coherentemente DOS constelaciones (con sus relojes, efemérides y
señales distintas) es mucho más difícil que una. Si GPS dice una posición y
Galileo otra, algo anda mal. Es barato de chequear y caro de burlar.

## Mini-simulacro

1. sube la potencia (C/N0) para ganar el correlador. 2. porque un spoofer
barato falsifica una constelación, no ambas coherentes. 3. detectores de
tasa (gradual los evade) vs de nivel/cruce (los cazan). 4. combinar varios +
cripto. 5. OSNMA autentica datos; los detectores cubren el rango/consistencia.
