# Soluciones — Clase 7.1 (filtro de Kalman)

## Lab

**TODO 1**: las cinco ecuaciones del §3.1, en orden. El único detalle no
obvio: $P$ se corrige DESPUÉS de usar $P^-$ en la ganancia.

**TODO 2**: $F=H=[1]$, $Q=[0]$, $R=[1]$. Con $Q=0$ el filtro sabe que
nada cambia → $K_n = 1/n$ → promedio recursivo: 5.0141 vs 5.0151 (la
diferencia son los 100 de $P_0$ diluyéndose).

**TODO 3**: $F=[[1,dt],[0,1]]$, $H=[[1,0]]$, $Q = \sigma_a^2
[[dt^4/4, dt^3/2],[dt^3/2, dt^2]]$, $R=[[4]]$. Referencia: RMS 1.76 →
0.82 m, v = 0.690.

**TODO 4**: igual que B pero por triplicado (bloques E/N/U) y con la
serie real. Referencia: scatter 0.66/0.69/1.50 → **0.45/0.47/0.65 m**;
RMS vs oficial 0.72/0.75/1.45 → 0.62/0.56/0.69; v = (+7.5, −1.9, −4.8)
mm/s; ρ(1) = −0.16/−0.00/−0.07.

## E1 — tres pasos a mano

$K_1 = 100/101 ≈ 0.990$ → $x_1 = 3.960$, $P_1 ≈ 0.990$.
$K_2 = 0.990/1.990 ≈ 0.497$ → $x_2 = 3.960 + 0.497(6−3.960) = 4.975$, $P_2 ≈ 0.497$.
$K_3 = 0.497/1.497 ≈ 0.332$ → $x_3 = 4.975 + 0.332(5−4.975) ≈ 4.983 ≈ 5$.
(Con $P_0 \to \infty$ daría exactamente 5 = promedio; el 0.017 que falta
es el prior diluyéndose.)

## E2 — Q = 0

Sin ruido de proceso, la incertidumbre solo baja → $K \to 0$ → el filtro
se vuelve sordo. Si la "constante" se mueve, el filtro la sigue con
retardo creciente y las innovaciones se van de blancas (ρ(1) > 0): la
sordera se detecta, no se adivina.

## E3 — F y Q para 30 s

$F = [[1, 30], [0, 1]]$; con $\sigma_a = 10^{-4}$: σ_pos por época
= $\sigma_a dt^2/2 = 0.045$ mm — el modelo deja moverse a la estación
décimas de milímetro por época: quieta, pero no soldada.

## F1 — cuánta blancura falta

Blanco puro: 1.5/√121 ≈ 0.14 m. El KF honesto se planta en 0.65 m: ~80%
de la varianza de U es error con memoria (iono residual, multipath,
tropo), no ruido — exactamente lo que mod3 modela y mide.

## F2 — memoria del error

τ ≈ −30/ln(0.9) ≈ 285 s ≈ 5 min. Promediar más rápido que eso no gana
nada; más lento, empieza a pisar señal.

## C1 — Q y R

$R$ inflado: el filtro ignora datos (lento, liso, atrasado). $Q$
inflado: el filtro persigue cada dato (nervioso, scatter casi crudo).
La sintonía honesta se audita con las innovaciones, no con el gusto.

## C2 — blancura

Si el modelo captura toda la estructura, lo que queda por sorprender es
ruido puro → sin memoria. ρ(1) > 0: el filtro va atrasado (Q chico o
dinámica no modelada). ρ(1) < 0 marcado: sobre-corrección (R chico).

## C3 — pisos distintos

El piso de cada eje es su **sesgo sistemático** (residuo de tropo/iono y
geometría — U siempre peor por ver solo medio cielo, clase 1.4/3.3). El
KF promedia ruido; el sesgo lo explican (y lo bajan) los modelos de
mod3, no la estadística.

## Mini-simulacro

1. §12 del README (las cinco líneas del cheat sheet).
2. Q chico/R grande → modelo; Q grande/R chico → dato.
3. La sorpresa $z - Hx^-$; blanca, media cero, covarianza $HP^-H^\top+R$.
4. Porque converge al promedio de las mediciones — sesgo incluido.
5. ≈ 0 mm/s; si estima velocidad firme en una estación quieta, hay
   dinámica mal modelada o errores correlacionados empujando.

## Entrevista — guión

"Guarda dos cosas: su mejor estimación y cuánto duda de ella. Cada
instante primero PREDICE con la física (y duda un poco más), después
MIDE y corrige: el reparto lo decide la ganancia, que compara su duda
con el ruido del sensor. Si confío en mi física, filtro fino; si confío
en el sensor, lo sigo de cerca. Y las sorpresas que me llevo — las
innovaciones — me auditan: si tienen patrón, mi física estaba mal."

## Mini-caso — el hueco de 10 s

Sin mediciones, solo predicción: $x$ sigue la última velocidad y $P$
crece época a época (la duda se acumula honesta). Al volver GNSS, $K$
sale grande y re-engancha rápido. La IMU (7.5) rellena el hueco con
mediciones propias → $P$ crece mucho más despacio: esa es TODA la idea
de la fusión.
