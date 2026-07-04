# Soluciones — Clase 2.2

## Ejercicios a mano

**E1.** ±5 kHz cada 500 Hz = 21 celdas Doppler (de −5000 a +5000). Por
1023 fases de código = **21 483 celdas por satélite**. Por 32 PRN ≈
**687 000 hipótesis** en un cold-start puro — de ahí que el arranque en
frío tarde y que A-GPS (que recorta la grilla) sea tan valioso.

**E2.** El pico coherente cae como sinc(f_res·T_coh). Con T_coh = 1 ms y
residuo máximo 250 Hz (media celda de 500 Hz): sinc(0.25) → factor
≈ 0.90 en amplitud → **~0.9 dB** de pérdida. Por eso 500 Hz es un paso
razonable a 1 ms; si integrás más, el paso tiene que achicarse.

**E3.** 524 muestras / 4 Msps = 131 µs → × 1.023 Mcps = **134 chips** →
× 293.1 m = **~39.3 km** (módulo la ambigüedad de 300 km del período de
1 ms). Es grueso porque el pico tiene base de ±1 chip (~300 m) y la
grilla lo ubica a ~½ chip; el discriminador early-late del tracking
(2.3) interpola el vértice a ~1% de chip → metros.

## Fermi

**F1.** 32 PRN × 41 celdas (±5 kHz/250 Hz) × FFT de 4000 pts (~4000·log₂
4000 ≈ 5·10⁴ ops) ≈ **~7·10⁷ operaciones** por 1 ms de datos, ×N para
integrar. Es mucho para arrancar de cero cada vez: A-GPS manda los ~8
SVs visibles y su Doppler ±, así el receptor confirma decenas de celdas
en vez de cientos de miles → TTFF de segundos, no minutos.

**F2.** Los satélites MEO orbitan a ~3.9 km/s; su **velocidad radial**
respecto de un usuario quieto va de 0 (cenit) a ±~800 m/s (horizonte),
que a 1.5 GHz da hasta ~±4 kHz. Sumá deriva del oscilador local del
receptor (ppm × 1.5 GHz = kHz) y llegás a la ventana de ±5 kHz.

**F3.** Gp coherente de 1 ms = 30 dB saca −19 dB a +11 dB de SNR pico:
alcanza para umbral 2.5 sin integrar más, en cielo abierto. Con señal
débil (indoor, −25 dB o peor) sumás integración no coherente (M
periodos: +5·log₁₀M dB pero con pérdida de squaring) hasta cruzar el
umbral. Coherente rinde más por dB pero topa en la longitud del dato
(1 bit = 20 ms en GPS; el piloto E1-C de Galileo levanta ese techo).

## Conceptuales

**C1.** Porque la réplica es un período completo del código periódico:
la correlación circular equivale a deslizarlo cíclicamente, que es
justo lo que hace la señal (se repite cada 1 ms). Si la captura fuera
más corta que un período, no habría un período completo que alinear: el
pico se degrada y el remuestreo circular deja de ser válido — hay que
zero-pad o usar al menos 1 ms.

**C2.** Coherente suma la amplitud **compleja** (preserva fase): gana
señal linealmente y ruido como √N → +3 dB por duplicar tiempo, pero
exige fase estable y ningún cambio de bit en la ventana. No coherente
suma **módulos** (|corr|²): tolera bits y deriva de fase, pero pierde
por el "squaring loss". No se puede coherente sin fin porque un bit de
datos (cada 20 ms en GPS) invierte el signo y cancela la suma.

**C3.** El BOC(1,1) de E1 mete una subportadora cuadrada: la
autocorrelación resultante tiene un pico central más angosto (mejor
precisión) pero **dos lóbulos laterales** a ±½ chip. GPS C/A (BPSK) es
un solo triángulo. Riesgo: la adquisición puede engancharse a un lóbulo
lateral y quedar ½ chip corrida (~150 m de sesgo) — hay que validar que
es el central (técnicas bump-jumping / doble estimación).

**C4.** El pico coherente ∝ A²·T² y el piso ∝ ruido; su cociente,
normalizado por el ancho de banda de integración, da C/N0 = 10·log₁₀
(pico/piso / T) aprox. Es útil contra spoofing porque el ataque suele
llegar más fuerte que lo real (C/N0 anómalamente alto y parejo entre
SVs) o crea un pico extra: un C/N0 fuera de lo físico es una bandera.

**C5.** El CAF muestra **dos picos** en la misma fila de código (o filas
vecinas): el auténtico y el del atacante, típicamente más alto y a un τ
levemente menor (más "cerca"). Un detector que mira el plano completo
—no sólo el máximo— ve la multiplicidad, la incoherencia de C/N0 entre
SVs, o el salto de posición del pico, y levanta alarma (SQM, monitoreo
de distorsión del pico — módulo 6).

## Mini-simulacro

1. `para cada f_D en grilla: x = seg·e^{-j2πf_D t}; corr = IFFT(FFT(x)·
   conj(FFT(rep))); guardar |corr|²`. Máximo del plano → (τ*, f_D*);
   adquirido si pico/media > umbral.
2. **V.** El ancho Doppler del pico ~1/T_coh: más integración coherente
   → lóbulo más angosto (mejor resolución de frecuencia), a costa de
   cómputo y de sensibilidad a cambios de bit.
3. 524/4e6 = 131 µs × 1.023e6 = 134 chips × 293.1 m ≈ 39.3 km (mod 300).
4. Porque el código E1-B no es una m-secuencia de LFSR: fue **elegido
   por búsqueda** (4092 chips optimizados), así que sólo puede
   almacenarse en tabla. El C/A sí sale de dos LFSR (2.1).
