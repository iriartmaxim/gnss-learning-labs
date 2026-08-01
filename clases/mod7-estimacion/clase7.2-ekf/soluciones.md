# Soluciones — Clase 7.2 (EKF sobre observables)

## Lab

**TODO 1**: derivada centrada del propagador de la 1.3 con ±0.5 s.
`kepler_a_ecef` ya devuelve ECEF (la rotación terrestre vive en el
término −ω⊕ de Ω), así que la derivada numérica ES la velocidad ECEF:
|v| Galileo ≈ 3670 m/s (clase 0.3).

**TODO 2**: las dos filas del §3.2. El único detalle con historia: el
signo del rango-rate, ρ̇ = −λ₁·D (Doppler positivo = se acerca = rango
bajando). Diagnóstico que lo prueba: en POS_OFICIAL el residuo
Doppler-vs-modelo es modo común −195.99 m/s con spread 0.012 m/s — si tu
signo estuviera al revés, el "modo común" sería ±700 m/s y sin sentido.

**TODO 3**: la misma maquinaria de la 7.1 con h(x) no lineal y H
recalculada por época. F: identidad + dt en (pos→vel) y (cδt→cδṫ). Q:
aceleración blanca σa=1e-3 por eje + RW de deriva σd=0.03. R:
diag(1², 0.05²) por satélite.

**TODO 4**: mediana de las innovaciones de código; si ronda k·299 792.458
(k entero ≠ 0), sumar k·c·1ms a cδt ANTES de corregir. En la hora de
datos hay ~2 saltos (deriva −196 m/s ⇒ 1 ms cada ~25 min).

Referencia completa: GN inicial 8.6 m → EKF 1.5 m (época 2) → medio
1.21 m, final 1.56 m · |v| 20 mm/s · deriva −196.126 m/s · [B] 73/395 km
con σ 2→135 m.

## E1 — la fila con u = (0.6, 0.8, 0)

Código: (−0.6, −0.8, 0, 0, 0, 0, 1, 0) · Doppler: (0, 0, 0, −0.6, −0.8, 0, 0, 1).

## E2 — el ms

1 ms / (196 m/s ÷ c) = c·1ms / 196 ≈ 299 792 / 196 ≈ **1530 s ≈ 25.5
min**. La deriva es negativa (el reloj atrasa): el reset SUMA +1 ms →
la pseudodistancia salta +299 792.458 m (y tu detector debe leer el
signo del salto en la mediana, no asumirlo).

## E3 — Doppler máximo

f_D = 1575.42e6 × 900 / 3e8 ≈ **±4.7 kHz** → en rango-rate: ±900 m/s.
Coincide con la grilla ±5 kHz de la 2.2 — el mismo número visto desde
la adquisición y desde la navegación.

## F1 — precisión de velocidad

0.012/√8 ≈ 4 mm/s instantáneo; promediando épocas, mm/s y menos. Por
eso el Doppler es el observable de velocidad (y el EKF lo hereda gratis).

## F2 — 240 vs 196

No es casualidad: la dirección inobservable con 3 SVs mezcla posición y
reloj (la columna de unos de G contra las u). El error "corre" a una
velocidad del orden de la deriva no separada — reloj y posición son la
misma sombra con 3 luces.

## C1 — H local

Porque h es no lineal: su jacobiano depende de dónde estás (foto local,
0.2). En la 7.1 H era literalmente la identidad sobre ENU — constante.

## C2 — el salto al reloj

Porque físicamente NADA más puede moverse 300 km entre épocas. Si lo
come la posición: fix a 300 km, velocidad gigante un instante, y el
filtro tarda decenas de épocas en perdonarse. Al reloj: un estado que
YA sabe que deriva, corrección instantánea, nadie más se entera.

## C3 — por qué P queda ciega

P se propaga con Q y R **asumidos** (ruido blanco, modelo correcto,
observabilidad). Con 3 SVs la dirección nula no recibe información y el
error real lo empujan sesgos correlacionados que "no existen" en el
modelo de ruido → P chica, error enorme. P mide la incertidumbre DEL
MODELO, no la del mundo: la brecha es exactamente lo que mod5 vigila.

## Mini-simulacro

1. §12 del cheat sheet, filas código y Doppler.
2. Derivada centrada del propagador broadcast; error ~cm/s (sobra: el
   ruido Doppler es mayor).
3. Lo detectan los códigos (saltan); el Doppler lo atraviesa porque
   deriva de la fase, continua a través del reset.
4. GN converge global desde cualquier lado (itera hasta plantarse); el
   EKF linealiza UNA vez por época — cerca es óptimo, lejos es ciego.
5. Una combinación posición-reloj (y velocidad-deriva): la rellena el
   modelo de dinámica con lo que tenga — y P no se entera.

## Entrevista — guión

Gana: estados físicos (velocidad, deriva) estimados directo de los
observables, huecos puenteados por el modelo, ruido de medición usado
como es (por observable, no por solución), y funciona donde el LSQ ni
arranca (3 SVs). Riesgo: todo eso descansa en el modelo — si la
dinámica o el ruido mienten, el filtro fabrica una realidad coherente
y su covarianza la firma. La pareja completa es EKF + integridad.

## Mini-caso — el dron con 3 satélites

Seguís navegando — el EKF está para eso — pero la confianza del fix ya
no sale de P: reportás "navegación degradada, error creciendo ~X m/min"
(lo sabés del análisis [B], no de P). Agregás: IMU (7.5) para achicar
la deriva real, y un monitor de integridad (mod5) que compare
soluciones/residuos y grite cuando la dirección ciega se lleve el fix.
