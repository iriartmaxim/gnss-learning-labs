# Soluciones — Visión global

## Lab (TODO 1–4)

Los patrones: IQ = `data/raw/iq/*.dat` · obs = `data/raw/*/*/[LC]*_MO.rnx`
· nav = `data/raw/*/*/BRDC*_MN.rnx` · precisos = `*ORB.SP3` y `*CLK.CLK`
· productos = `clases/*/*/data/resultados_*.json`. Referencia con 0.4 y
labs corridos: 3 + 3 + 2 + 2 + ~12 archivos, ~150 MB, 5/5 etapas.

## E1 — el arco con las clases

señal (2.1–2.4) → observables (1.2, 1.5, 3.4) → mensaje/órbitas (0.4,
1.3, 4.1, constelaciones) → correcciones (3.1–3.4) → PVT (1.1, 1.2,
1.4, 1.5) — y la verdad precisa (SP3/CLK) calificándolo todo desde
afuera. mod5/6/7 operan SOBRE la solución (confianza, precisión,
seguridad).

## E2 — presupuesto de enlace

14.3 dBW + 13 dB − 182 dB ≈ **−155 dBW** ≈ 3×10⁻¹⁶ W. Con antena
receptora ~0 dB y ancho de banda de C/A, la señal queda ~20 dB bajo el
piso térmico: solo la ganancia de procesamiento de la correlación
(10·log₁₀(1023) ≈ 30 dB) la saca a flote — por eso el arco EMPIEZA en
la correlación.

## E3 — segmentos

(a) control · (b) usuario · (c) espacial · (d) control · (e) **ambos**:
lo emite el segmento espacial, lo captura y compila una red terrestre
(BKG) — el archivo es un producto del suelo sobre datos del cielo (0.4).

## F1 — receptores

~7×10⁹ smartphones + vehículos + IoT/infraestructura → orden **10¹⁰**.
Más receptores que personas.

## F2 — energía

1 J / 10⁻¹⁶ W = 10¹⁶ s ≈ 3×10⁸ años. La información no viaja en
potencia sino en estructura (el código): correlación, no carga.

## C1 — la dependencia del control

Las efemérides caducan (horas) porque la órbita real se aparta del
ajuste (4.1). Si el control no sube frescas: Galileo 2019 (6 días
mudo) y GLONASS 2014 (11 h envenenada) — satélites sanos, sistema
muerto. Por eso B4 mira el sistema desde tierra.

## C2 — por qué 4

El receptor no sabe su hora: su reloj barato mete un sesgo c·δt igual
en TODAS las mediciones. Es la 4ª incógnita — se despeja con la 4ª
medición (1.2). Con 3 satélites y reloj atómico propio: 3 alcanzarían.

## C3 — dos arcos

Broadcast: latencia cero, exactitud ~1 m de órbita, para navegar YA.
Preciso: ~2 semanas, ~2.5 cm, para calificar, calibrar y post-procesar.
El curso navega con el primero y se califica con el segundo — medir el
error propio contra una vara mejor es el método científico del path.

## Mini-simulacro

1. señal (2.2) · observables (1.5) · mensaje (1.3) · correcciones (3.x)
   · solución (1.5); vale cualquier clase correcta por etapa.
2. Control/terreno en ambos.
3. Porque la correlación aporta ~30 dB de ganancia de procesamiento: la
   señal está diseñada para ser encontrada, no oída.
4. x, y, z, c·δt — las despejan ≥4 pseudodistancias vía Gauss-Newton.
5. 1575.42 y 1176.45 MHz; dos frecuencias ⇒ medir y eliminar la iono.

## Entrevista — guión sin fórmulas

"Hay ~30 relojes perfectos dando vueltas a la Tierra, cada uno grita la
hora sin parar. Tu teléfono escucha cuatro gritos, nota que llegan con
retrasos distintos, y de esos retrasos deduce a qué distancia está de
cada reloj — y de ahí, dónde está parado. Todo lo demás — mapas,
correcciones, precisión de centímetros — es ingeniería para que esos
retrasos se midan cada vez mejor."

## Mini-caso — timestamping bancario

Les importa: mensaje (tiempo GNSS), reloj del receptor, integridad.
No les importa: DOP fino, multipath métrico, precisión horizontal.
Riesgo nuevo: **spoofing de tiempo** (correr el reloj sin mover la
"posición") — la defensa es autenticación (OSNMA, 6.x) + holdover con
reloj local. Un solo satélite basta para tiempo si la posición es
conocida: el arco se recorta distinto según el producto.
