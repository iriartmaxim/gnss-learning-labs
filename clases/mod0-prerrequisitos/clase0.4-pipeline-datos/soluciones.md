# Soluciones — Clase 0.4 (pipeline de datos)

Paso a paso **sin código**. Los números de referencia son del día
2026-06-15 (DOY 166) con los archivos `BRDC00IGS_R_20261660000_01D_MN.rnx`
y `COD0MGXFIN_20261660000_01D_05M_ORB.SP3`.

## Lab — TODO 1 (censo del RINEX nav)

Una efeméride ocupa varias líneas, pero **una sola** es la cabecera: la
que arranca con el ID del satélite (`E12 2026 06 15 ...`). El criterio de
detección tiene dos condiciones: el primer carácter es una letra de
constelación conocida, y los dos siguientes son dígitos. Eso descarta las
líneas de parámetros (empiezan con espacios) y las del header del archivo
(p. ej. `GAL` o `GPSA` en las correcciones ionosféricas: tercera letra no
numérica). Contando cabeceras por letra queda:

| Constelación | Efemérides |
|---|---|
| GPS | **450** |
| BeiDou | **901** |
| Galileo | **11 119** |

y el set de Galileo únicos tiene **30** SV (E02…E36; faltan E17, E20,
E22, E24, E35 — huecos reales de la constelación ese día).

## Lab — TODO 2 (header SP3)

Los satélites se declaran en las líneas que empiezan con `+ ` (más
espacio), 17 IDs por línea en las columnas 10–60, rellenando con ceros al
final. La sección siguiente (`++`) son las precisiones — ahí se corta.
Filtrando IDs cuya primera letra sea una constelación real quedan
**116 satélites**: G 32, R 21, E 30, C 30, J 3.

## Lab — TODO 3 (cruce)

Intersección del set Galileo del nav con el del SP3: **30 en común, sin
diferencias**. Qué significa: dos organismos independientes (BKG compila
lo emitido; CODE calcula órbitas con su propia red) coinciden en qué
satélites existían y operaban ese día. Es un chequeo de **consistencia de
constelación** — no dice nada todavía de la exactitud de las órbitas
(eso es la 1.3).

## Lab — TODO 4 (tasa de re-emisión)

- GPS: 450 / 32 ≈ **14 efemérides por satélite y día** → una cada ~102
  min. Nominal: una cada 2 h; el excedente son actualizaciones (uploads)
  y solapes de captura entre estaciones.
- Galileo: 11 119 / 30 ≈ **371 por satélite y día** → una cada ~3.9 min.
  Consistente con re-emisión cada ~10 min por 3 canales (I/NAV en E1 y
  E5b, F/NAV en E5a): 3 mensajes cada 10 min ≈ uno cada 3.3 min.

## E1 — DOY

31 (ene) + 28 (feb) + 31 (mar) + 30 (abr) + 31 (may) = 151; 151 + 15 =
**166** ✓. Para 2026-06-25: 151 + 25 = **176** (el día de la clase 3.4,
elegido a +10 días exactos del 166 por la repetición sideral de Galileo).

## E2 — semana GPS

De 1980-01-06 a 2026-06-15 hay ≈ 46.44 años × 365.25 ≈ 16 963 días;
16 963 / 7 ≈ 2423.3 → semana **2423** ✓ (el conteo exacto da 16 962 días
y 2026-06-15 cae lunes, día 1 de la semana GPS).

## E3 — minutos entre efemérides Galileo

11 119 / 30 ≈ 371 por día → 1440 / 371 ≈ **3.9 min**. Con I/NAV (E1),
I/NAV (E5b) y F/NAV (E5a) re-emitiendo cada ~10 min: 3 copias / 10 min →
una cada ~3.3 min. Mismo orden ✓ — la diferencia son cortes de batch y
deduplicación imperfecta entre estaciones de captura.

## F1 — tamaño del RINEX obs

2880 épocas × 35 sat × 80 bytes ≈ **8 MB**. El archivo real de LPGS del
día 166 anda en ese orden (el tuyo exacto: mirá `ls -lh data/raw/2026/166/`).

## F2 — efemérides GPS esperadas

32 sat × 12 por día (una cada 2 h) = **384**. El archivo trae 450: el
~17% extra son uploads no programados y efemérides duplicadas con
distinto tiempo de captura. Si te dio 384 exacto, tu modelo es el
nominal — el archivo es la realidad.

## F3 — líneas del SP3

116 sat × 288 épocas ≈ **33 400 líneas de posición** (+ header y líneas
de época) → unos 2–3 MB de texto. Por eso el SP3 va cada 5 min y no cada
30 s: para relojes finos existe el CLK.

## C1 — ¿por qué el BRDC sale de un servidor?

Nadie tiene una antena que vea toda la constelación todo el día: el BRDC
es un **agregado terrestre** de lo capturado por cientos de estaciones.
Consecuencias: puede haber duplicados (misma efeméride vista por varias
estaciones, a veces con tiempos de captura distintos) y huecos (satélite
sin estación a la vista que lo capture en algún intervalo). El archivo
"mixto" (`_MN`) junta todas las constelaciones en un solo RINEX.

## C2 — ¿el SP3 corrige el pasado?

No: tu fix de hace dos semanas ya se calculó con la broadcast que había.
El SP3 final sirve como **verdad de referencia post-facto**: restás
órbita broadcast − órbita precisa y medís el error que sufriste (SISRE
orbital, lo cuantificás en 1.3 y 4.1). También alimenta el post-proceso
(PPP): recalcular posiciones con los productos buenos.

## C3 — qué validó el cruce 30/30

Validaste **consistencia de catálogo**: ambas fuentes ven los mismos
satélites operativos. NO validaste: que las órbitas broadcast sean
exactas (1.3), que los relojes broadcast sean sanos (1.5/3.2), ni que los
observables de tu estación sean limpios (1.5/3.4). El pipeline te da los
insumos; la evidencia la construís clase por clase.

## Mini-simulacro — respuestas

1. Pseudodistancias → RINEX **obs** (por eso lo baja `--que obs` por
   estación); efemérides → RINEX **nav** (BRDC, global).
2. Porque los **finales MGEX** (única órbita precisa multi-GNSS del
   curso) tardan ~2 semanas; con un día a ~3 semanas está todo publicado
   y el resultado es reproducible.
3. georinex agrega `_N` cuando el mismo SV tiene varios mensajes en la
   misma época (I/NAV vs F/NAV, capturas duplicadas). En 1.3 hay que
   quedarse con **un** tipo de mensaje antes de propagar.
4. Rápido IGS: ~1 día, **solo GPS**. Final MGEX (CODE): ~2 semanas,
   GPS+GLONASS+Galileo+BeiDou+QZSS.
5. GPS re-emite cada 2 h; Galileo cada ~10 min y por 3 canales, y el
   BRDC mixto guarda todo → ~25× más registros con constelaciones de
   tamaño similar.

## Pregunta de entrevista — guión de 90 s

- Broadcast: la genera el **segmento terreno** de cada constelación y la
  transmite el propio satélite; latencia cero, error de órbita ~1 m —
  es lo que usa cualquier receptor en tiempo real.
- Precisos: los generan **centros de análisis** (CODE, JPL…) combinando
  una red global; rapid ~1 día (GPS), final ~2 semanas (multi-GNSS),
  error ~2–3 cm.
- Uso: tiempo real → broadcast, sí o sí. Post-proceso, calibración,
  investigación, o medir el error de la broadcast → precisos.
- Cierre: "en el curso los uso a la vez: propago la broadcast con el ICD
  y la califico contra el SP3 final".

## Mini-caso — respuesta esperable

Insumos: obs RINEX de la estación del cliente (o RAMSAC/red propia),
órbitas+relojes finales MGEX de CODE (por el requisito Galileo), modelo
de antena/mareas según exigencia. Latencia prometible: **~2 semanas**
(la manda el final MGEX); si el cliente tolera solo GPS, rapid ~1 día.
El trade-off latencia/constelaciones/precisión es la decisión de diseño.
