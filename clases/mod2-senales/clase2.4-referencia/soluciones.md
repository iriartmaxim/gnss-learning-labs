# Soluciones — Clase 2.4

## Ejercicios a mano

**E1.** La grilla Doppler tiene paso de 250 Hz. Tu pico cae en la celda
más cercana al Doppler real: +1750 es la celda de la grilla (…1500, 1750,
2000…) que contiene al valor verdadero. gnss-sdr publica +1680 como su
mejor estimación (con interpolación fina o distinta grilla). La diferencia
de 70 Hz es **menor a una celda** (250 Hz): ambos apuntan al mismo
Doppler físico, sólo con distinta resolución. No es error, es
cuantización de la grilla. Para afinar, se interpola el pico o se integra
más tiempo (más resolución de frecuencia).

**E2.** Sí, son consistentes. El código son 1023 chips ≈ 4000 muestras a
4 Msps. Tu delay 523 y el code phase 2020 de gnss-sdr difieren en 1497
muestras, pero **el desfase de código es relativo al punto de arranque**:
gnss-sdr ancla su adquisición en `sample_stamp=6504` (no en la muestra 0),
así que su fase está corrida. Lo que importa es que ambos identifican el
**mismo satélite** (PRN1) con el **mismo Doppler**. La fase absoluta sólo
tiene sentido comparada módulo el período y con el mismo origen.

**E3.** Bajar el paso a 50 Hz da **5× más resolución de Doppler** (el pico
cae más cerca del valor real, mejor estimación inicial de velocidad), pero
**5× más celdas Doppler** → 5× más cómputo en la adquisición. Es el mismo
trade-off de tu grilla en la 2.2: fino = preciso pero caro. En la práctica
se adquiere grueso (250-500 Hz) y el tracking (2.3) afina el Doppler con
el PLL, así que no hace falta una grilla fina en la adquisición.

## Fermi

**F1.** GNU Radio te da el **framework de flujo de datos en tiempo real**:
manejo de buffers entre bloques, threading, kernels vectorizados (VOLK)
que corren la FFT y las correlaciones a la velocidad de muestreo, drivers
de hardware (RTL-SDR, USRP, bladeRF), y decenas de bloques de DSP
probados. Tu cadena en Python entra en un archivo porque procesa un
archivo *offline* y chico; un receptor real procesa un flujo continuo de
millones de muestras/s de una radio, en tiempo real, con múltiples canales
—eso exige la infraestructura de GNU Radio. Vos hiciste el *algoritmo*;
GNU Radio es la *maquinaria* que lo corre en producción.

**F2.** Capturaste **muestras IQ del aire** (las de gnss-sdr son reales,
de antenas GPS/Galileo), que normalmente requerirían un front-end RF
(antena activa + RTL-SDR o USRP + LNA) y tiempo de captura. Los datasets
públicos te dieron eso gratis. Para un fix en vivo te falta: el hardware
(RTL-SDR + antena activa con vista al cielo), una captura larga (≥30 s
para bajar efemérides), y correr la cadena completa hasta el PVT (que es
la 1.5, ahora con datos que vos capturaste en vez de RINEX de una estación
IGS).

## Conceptuales

**C1.** El Doppler viene del movimiento relativo satélite-receptor: es
físico, cualquier receptor bien hecho mide el mismo (dentro de su
resolución). El desfase de código es *dónde en el código* está el receptor
al empezar a procesar — depende de en qué muestra arranca. Para verificar
dos receptores usás el **Doppler y el PRN**: si coinciden, ambos
encontraron el mismo satélite moviéndose igual. El desfase sólo se compara
con el mismo origen de tiempo.

**C2.** "De referencia" significa que sus resultados están validados
—contra hardware, contra otras implementaciones, contra las verdades
teóricas— y son reproducibles y auditables (open-source). No es circular
porque gnss-sdr es una implementación **independiente**, escrita por otra
gente, con otro código: si tu cadena artesanal y gnss-sdr coinciden, es
muy improbable que ambas tengan el *mismo* error. Es como verificar una
cuenta con una calculadora hecha por otro. La validación final, igual, es
contra el mundo físico (hardware).

**C3.** Hay que repetir la captura porque gnss-sdr necesita suficientes
muestras para correr su máquina de estados (adquirir → confirmar →
trackear), y 2 ms no alcanzan. De la señal repetida **no** podés concluir
nada sobre el **mensaje de navegación**: al hacer loop de 2 ms, los bits
no forman un subframe coherente (un bit dura 20 ms > 2 ms de captura), así
que no hay preámbulo real ni efemérides. Sirve sólo para mostrar
adquisición y enganche de tracking, no demodulación ni PVT.

**C4.** Que las piezas que construiste están **bien**. Si tu generador de
códigos (2.1) tuviera un chip mal, tu réplica no correlacionaría con la
señal real y no encontrarías el satélite —o lo encontrarías en el lugar
equivocado. Si tu PCPS (2.2) tuviera un error de FFT o de grilla, el
Doppler no coincidiría. Que gnss-sdr —independiente— encuentre el mismo
PRN con el mismo Doppler confirma que tu cadena completa, del LFSR a la
correlación, es correcta.

## Mini-simulacro

1. SignalSource (muestras IQ) → Acquisition (PCPS: encontrar PRN, delay,
   Doppler) → Tracking (DLL+PLL: seguir y afinar) → TelemetryDecoder
   (demodular bits) → Observables (pseudorangos) → PVT (posición).
2. **Falso.** Sobre la misma captura, dos receptores pueden dar distinto
   desfase de código si arrancan a procesar en muestras distintas: la fase
   es relativa al punto de arranque. Coinciden módulo el período (1023
   chips). Lo que sí debe coincidir es el Doppler y el PRN.
3. **Ambos, pero con distinto criterio**: el Doppler debe coincidir a ±1
   celda (es físico); el desfase de código sólo módulo el período (por el
   arranque). Para una verificación limpia, el Doppler y el PRN son lo
   robusto.
