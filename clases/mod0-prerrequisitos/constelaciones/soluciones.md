# Soluciones — Constelaciones

## Lab (TODO 1–4)

**TODO 1**: mismo criterio de cabecera que la 0.4 (letra + 2 dígitos),
pero acumulando SV en un set por letra. Referencia día 166:
G 32 · E 30 · R 27 · C 37 · J 5 · I 3 · S 17.

**TODO 2**: `sqrtA` es el 4º campo de la línea 3 (19 chars desde la
col. 4, exponente `D`→`E`). a = sqrtA² → medianas: GPS 26 561 km,
Galileo 29 600, BeiDou 27 906 (la mediana cae en los MEO: los GEO/IGSO
de ~42 164 km quedan arriba).

**TODO 3**: GLONASS trae x, y, z (km) como primer campo de las líneas
1–3 del registro. |r| mediana ≈ 25 502 km — no hay sqrtA que leer: el
formato mismo te dice que acá se integra, no se propaga Kepler.

**TODO 4**: T = 2π√(a³/μ) → 11.97 / 14.08 / 11.26 / 12.89 h. Alturas =
a − 6371 km.

## E1 — tercera ley

a = 29 600 km → T = 2π√(a³/μ) = 50 690 s ≈ 14.08 h ✓. Para T = 12 h:
a = (μ(T/2π)²)^(1/3) ≈ 26 610 km — casi GPS (11.97 h es medio día
**sidéreo**, no solar: por eso GPS no usa 12 h exactas).

## E2 — registros esperados

GPS: 32 × 14 ≈ 450 ✓ exacto. Galileo: 30 × 370 ≈ 11 100 ≈ 11 119 ✓.
El censo de la 0.4 y el de hoy cierran entre sí.

## E3 — BeiDou GEO

T = 23 h 56 m → a ≈ 42 164 km → altura ≈ 35 786 km. Un GEO sobre Asia
(~80°–160° E) queda bajo o debajo del horizonte visto desde Argentina:
cobertura regional por diseño.

## F1 — total activos

32+30+27+37+5+3 ≈ 134 emisores de navegación (+17 SBAS retransmisores).
Orden: ~130.

## F2 — por qué 24–30

Con MEO de ~20 000 km, la Tierra se cubre con ≥4 visibles usando ~24
satélites bien repartidos (6×4 GPS clásico); los extras son margen de
mantenimiento y geometría (DOP), no capacidad de lanzamiento.

## C1 — 37 vs 30

CODE ajusta con una red **global**: los MEO (y algo de IGSO) se observan
desde todo el mundo; los GEO de BeiDou se ven siempre desde la misma
región con geometría pobre (satélite quieto en el cielo) → órbitas
difíciles de ajustar → afuera del SP3. El BRDC en cambio guarda todo lo
que se emite.

## C2 — FDMA

Cada sat GLONASS legado emite el MISMO código en frecuencia distinta
(L1 = 1602 + k·0.5625 MHz). El receptor necesita front-end más ancho y
réplicas por canal de frecuencia (no solo por código) — más hardware,
y sesgos inter-frecuencia propios. El CDMA moderno (L3OC) converge al
esquema de los demás.

## C3 — la incógnita extra

Cada sistema tiene su escala de tiempo: mezclar GPS+Galileo agrega el
sesgo GGTO (o se estima como incógnita extra → hace falta 1 satélite
más). Robustez sí, pero no gratis: 4+1 incógnitas con dos sistemas.

## Mini-simulacro

1. GLONASS (19 130) < GPS (20 190) < BDS MEO (21 535) < Galileo (23 230).
2. GLONASS: vectores de estado → el receptor integra numéricamente; el
   propagador kepleriano de la 1.3 no aplica.
3. Órbita geosíncrona inclinada (traza en ∞ sobre una región): BeiDou y
   QZSS/NavIC.
4. Corrige e informa integridad; sus datos salen de redes TERRESTRES de
   monitoreo, subidos a GEOs que retransmiten.
5. Para no resonar con la rotación terrestre: 17 rev/10 días reparte las
   perturbaciones y el multipath no se repite cada día (3.4).

## Entrevista — guión

Órbita: Galileo más alto (23 230 vs 20 190) → menos perturbación
relativa, repeat de 10 días. Señal: CBOC en E1 (mejor multipath que C/A)
y E5 AltBOC ancha. Tiempo: GST sin leaps, GGTO emitido. Mensaje:
I/NAV+F/NAV con re-emisión densa (0.4: 370/día vs 14) y OSNMA de
autenticación (mod6). Cierre: "llegó después y diseñó contra los
problemas medidos de GPS".

## Mini-caso — tractor en Argentina

GPS+Galileo (cobertura global y densidad de señal, iono-free E1/E5a) +
GLONASS como tercera si el receptor lo trae. QZSS no aporta acá (órbitas
sobre Asia-Pacífico... sus GEO/HEO no cubren Sudamérica). SBAS: WAAS no
da servicio garantizado en Argentina — para precisión agrícola real:
corrección local (RTK/red propia o PPP, B2).
