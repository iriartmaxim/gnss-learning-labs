# Soluciones — Clase 2.3

## Ejercicios a mano

**E1.** Doppler de código = Doppler de portadora / 1540 = 1200 / 1540 ≈
**0.78 Hz** (sobre 1.023 MHz de chip rate). Es minúsculo: el código se
corre menos de 1 chip cada ~1.3 s. Por eso el DLL puede tener BW muy bajo
(1–2 Hz) — casi no hay dinámica de código —, y en la práctica se lo
**asiste con la portadora** (carrier-aided): el PLL, que sí ve 1200 Hz,
le pasa la estimación de velocidad al DLL dividida por 1540.

**E2.** Integrar 20 ms coherente vs 1 ms = factor 20 en tiempo →
10·log₁₀(20) ≈ **+13 dB** de ganancia de proceso extra. Lo que lo impide
pasar de 20 ms es el **bit de datos**: cada 20 ms puede invertir el signo
y cancelar la integración. El piloto E1-C de Galileo (sin datos) o el
tracking asistido por bits conocidos permiten integrar más.

**E3.** 8 bits: la probabilidad de que 8 bits aleatorios coincidan
exactamente con el patrón (o su inverso) es 2·(1/2)⁸ = 2/256 ≈ **0.8%**
por posición. En 300 bits de un subframe eso da varios falsos positivos:
por eso el receptor exige además **paridad correcta** de las palabras y
**dos preámbulos consecutivos separados exactamente 6 s** (300 bits) antes
de declarar sincronización.

## Fermi

**F1.** 12 SV × 3 correladores × 4000 muestras × 1000 ms/s ≈ **1.4·10⁸
multiplicaciones complejas por segundo**, y eso sólo el correlador prompt
básico (con E/P/L y varios más por SV, sube). Es flujo constante y
paralelo → ideal para **FPGA/ASIC**: cada canal es un correlador en
hardware corriendo a la tasa de muestreo. En SDR se hace en CPU/GPU con
FFT, pero el consumo es la razón de que los chips GNSS de teléfono lo
metan en silicio dedicado.

**F2.** ½ chip = ~150 m; 1% de chip = ~3 m de error de código. Con
suavizado de portadora baja aún más. Comparado con la 1.5 (donde el error
de pseudorango dominaba junto con órbitas/reloj y quedaba ~1–2 m de RMS
tras iono-free): el tracking fino es lo que hace *posible* ese nivel — sin
él, el pseudorango tendría cientos de metros de ruido y ningún PVT
cerraría a metros.

**F3.** 900 km/h = 250 m/s. En aproximación, la velocidad radial hacia un
satélite bajo puede acercarse a eso; Doppler = v·f/c = 250 × 1.57542e9 /
3e8 ≈ **1310 Hz** de la dinámica del avión (sumado al ±4 kHz orbital). Un
PLL de 18 Hz de BW sigue la **frecuencia** sin problema (el BW limita el
ruido, no el rango), pero la **aceleración** en maniobras bruscas puede
exceder un lazo de 2º orden → por eso los receptores de aviación/inercial
usan lazos asistidos por la IMU (ultra-tight coupling).

## Conceptuales

**C1.** Porque el bit de datos invierte la fase 180° cada 20 ms; un PLL
común interpretaría eso como un salto de fase y se desengancharía. El
Costas usa `atan(Q/I)` (o Q·I), que da el mismo error para 0° y 180° → es
insensible al signo del símbolo. El precio es una **ambigüedad de 180°**:
no sabés si tus bits son los reales o los invertidos. Se resuelve con el
preámbulo: si correla +8 son directos, si correla −8 hay que invertir todo.

**C2.** Se normaliza por (E+L) para que el error quede en **unidades de
chip independientes de la amplitud**. Si no, cuando el C/N0 sube (señal más
fuerte), |E|−|L| crece en valor absoluto y la ganancia efectiva del lazo se
dispara → el DLL se vuelve inestable o sobre-corrige; cuando baja, se hace
lento. Normalizar mantiene el ancho de banda del lazo constante ante
cambios de potencia.

**C3.** Porque el error de código es un error de **fase** (posición), no de
frecuencia. Si corregís la frecuencia del NCO de código sin que haya
Doppler de código real, introducís una deriva que va corriendo el prompt
ms a ms — la amplitud del prompt cae aunque el preámbulo todavía salga (el
prompt sigue siendo el mayor un rato). Síntoma: |Prompt| decreciente y
dll_err con sesgo. Corrigiendo la **fase** directamente, el prompt se
mantiene centrado y su amplitud estable.

**C4.** Cuando el PLL engancha, el NCO de portadora está en fase con la
señal recibida, así que al multiplicar por `exp(−j·fase)` la componente de
señal queda **real**: toda su energía cae en I y Q≈ruido. Como el bit sólo
cambia el signo de I (no mete nada en Q), integrando I sobre 20 ms y
mirando el signo recuperás el bit. Q sirve de chequeo: si crece, el PLL se
está desenganchando.

**C5.** Durante el arrastre, el receptor ve primero **dos correlaciones
casi superpuestas** (la real y la del atacante) que luego se separan a
medida que el spoofer mueve su código; el pico de correlación se
**distorsiona** (|E| y |L| dejan de ser simétricos, el prompt se ensancha o
se parte) y suele haber un **salto de C/N0** cuando el atacante sube
potencia. Un monitor de calidad de señal (SQM) que vigile la simetría
early-late y el C/N0, o la comparación con la inercial, lo delata. La
autenticación criptográfica (OSNMA) lo corta de raíz al firmar el mensaje.

## Mini-simulacro

1. señal → (× NCO portadora) → base → correladores E/P/L con réplica de
   código → Costas `atan(Q/I)` y early-late `(|E|−|L|)/(|E|+|L|)` →
   filtros de lazo → NCO portadora (freq) y NCO código (fase) → Prompt
   integrado 20 ms → signo → bits → preámbulo.
2. **Matiz**: el Costas no distingue 0 de 1 *por su fase* (ambos dan el
   mismo error de lazo, esa es la gracia), pero el **signo del Prompt I**
   sí lleva el bit — lo que no sabés es la polaridad global hasta ver el
   preámbulo.
3. 1200 / 1540 ≈ 0.78 Hz.
4. Porque un bit LNAV dura exactamente 20 ms (50 bps) = 20 códigos C/A;
   integrar 15 o 25 mezcla energía de dos bits distintos y el signo se
   ensucia.
