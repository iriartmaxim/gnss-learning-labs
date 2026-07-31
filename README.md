# gnss-learning-labs

Path de aprendizaje GNSS — preparación para el JSNP Master (GNSS Academy,
12ª edición, septiembre 2026 – febrero 2027).

Autor: Maximiliano Iriart (mmiriart)
v5 — el path es ahora el README del repo. Estructura organizada según los
5 bloques de teoría del temario oficial: B1 Basics → B2 Advanced → B3
Signals → B4 System → B5 Future & Trends. Cada ítem del temario es una
sección; debajo, los labs que lo trabajan.

Cada tema es un lab con datos reales, entregable y criterio de validación.
La regla: un concepto no está aprendido hasta que corre en Python.

---

## Índice

- Cómo usar este path
- Estado por bloque
- Prerrequisitos y entorno (transversal)
- **Bloque 1 — Basics**
  - Visión global de la tecnología de la navegación
  - Constelaciones globales / regionales / aumentación
  - Arquitectura de receptores
  - Técnicas de posicionamiento fiable y preciso — Labs 1.1, 1.2, 1.4
  - Observables: código / fase / Doppler / SNR
  - Errores y modelos de caracterización / corrección — Labs 3.1, 3.2, 3.4
  - Órbitas & relojes atómicos — Labs 1.3, 4.1
  - Propagación atmosférica: ionosfera, troposfera — Lab 3.3
  - Cálculo de posición (PVT) y filtros de estimación básicos — Lab 1.5
- **Bloque 2 — Advanced**
  - Fiabilidad e integridad para aplicaciones críticas — Labs 5.1–5.3 + ARAIM
  - Técnicas diferenciales (estaciones de referencia) — Lab 7.3
  - Técnicas de precisión centimétrica — Lab 7.4
  - Resiliencia: sensor fusion — Lab 7.5
  - Modelos avanzados de estimación: KF, EKF — Labs 7.1, 7.2
- **Bloque 3 — Signals**
  - Definición y procesamiento de señales GNSS — Lab 2.1
  - Técnicas de adquisición y tracking — Labs 2.2, 2.3, 2.4
  - Autenticación Galileo OSNMA / SAS — Labs 6.1, 6.2, 6.6
  - Análisis de interferencias y spoofing — Labs 6.3, 6.4, 6.5
  - Simulación de señales (Skydel)
- **Bloque 4 — System**
  - Arquitectura segmento terreno: Galileo y EGNOS
  - Algoritmos de validación y pre-procesado
  - Algoritmos de órbita (POD / OD&TS) — Lab 4.2
  - Sincronización de relojes y escalas de tiempo atómicas — Labs 4.3, 4.4
  - Algoritmos de estimación de la ionosfera
  - Cadena de integridad y detección de ataques del sistema
- **Bloque 5 — Future & Trends**
  - LEO-PNT / Alternative PNT · Navegación lunar (Moonlight) · SatCom
- Workshops del máster — dónde los cubre el path
- Proyecto del máster — preparación para elegir
- Secuencia de cursada sugerida
- Referencias generales

---

## Cómo usar este path

- **Una clase = una carpeta** en `clases/modX-nombre/claseX.Y-tema/`, con
  README (teoría, ejercicios, checkpoints), lab TODO + solución, figuras
  generadas por script y flashcards Anki.
- **La numeración de carpetas (modX/claseX.Y) es estable**: identifica la
  carpeta, no el orden temático. Las clases se importan entre sí (el motor
  PVT de 1.5 se reusa en 3.2, 3.3, 4.1...), así que no se renombra. Este
  documento ordena por bloque del temario; el ID de clase es el puntero.
- **El material de mod0–mod4 ya está construido en el repo** (18 clases
  con README, labs, soluciones y figuras); mod5, mod6 y mod7 se
  construyen al llegar. El checkbox marca **cursada completada y
  validada**, no material existente.
- **El orden del documento sigue al temario, no a la cursada**: algunos
  ítems de un bloque dependen de labs listados en otro (sensor fusion usa
  el KF). La "Secuencia de cursada sugerida" define el orden real de
  estudio.
- **Validación siempre cuantitativa**: comparar contra una referencia
  (coordenadas oficiales de una estación, productos precisos, salida de
  RTKLIB/gnss-sdr). Si no hay número, no hay validación.

## Estado por bloque

| Bloque | Material en el repo | Progreso de cursada |
|---|---|---|
| Prerrequisitos | tools/fetch_data.py + clases mod0 | Pendiente |
| B1 — Basics | mod1, mod3 y 4.1 construidos | Pendiente |
| B2 — Advanced | por construir (mod5, mod7) | Pendiente |
| B3 — Signals | mod2 construido; mod6 por construir | Pendiente |
| B4 — System | 4.2–4.4 por construir | Pendiente |
| B5 — Future & Trends | lectura | Pendiente |

---

## Prerrequisitos y entorno (transversal, fuera del temario)

Entorno de referencia: PCHOME — Ubuntu nativo, Python 3.12 en venv.

- [ ] **Entorno base.** Crear el venv del path e instalar
  `numpy scipy matplotlib pandas cryptography georinex hatanaka unlzw3`.
  Validación: importar todo sin errores y correr una solución de mod1.
- [ ] **Refresco matemático dirigido.** Mínimos cuadrados y su versión
  ponderada, jacobianos y linealización, matrices de rotación 3D.
  Entregable: ajuste no lineal genérico con Gauss-Newton escrito a mano
  (material en `clases/mod0`).
- [ ] **Mecánica orbital mínima.** Elementos keplerianos; anomalía media,
  excéntrica y verdadera; qué perturba una órbita real (J2, presión de
  radiación). Solo lo necesario para leer una efeméride
  (material en `clases/mod0`).
- [ ] **Pipeline de datos.** Dejar operativo `tools/fetch_data.py` (ya en
  el repo): descarga RINEX (nav y obs) y productos SP3/CLK. Validación:
  una descarga de cada tipo. Fuentes:
  - RINEX y productos: BKG (`igs.bkg.bund.de`), CDDIS (cuenta Earthdata).
  - **Argentina: RAMSAC (IGN)** — red CORS nacional con RINEX descargable;
    ideal para validar contra coordenadas oficiales de estaciones locales.
  - Productos precisos multi-GNSS: MGEX (centros CODE, GFZ, Wuhan).
  - Mensaje de navegación en vivo: **galmon.eu**.

**Checkpoint:** explicar por qué linealizar el problema PVT lo convierte
en mínimos cuadrados iterativos, y qué rol juega el jacobiano (matriz de
geometría) en cada iteración.

---

# BLOQUE 1 — BASICS

Los fundamentos para comprender cualquier sistema espacial de navegación.

## Visión global de la tecnología de la navegación

Sin lab propio: es el marco conceptual que el path construye de a
pedazos — el arco señal → observable → errores → órbita → PVT. Lectura
inicial: cap. 1 del ESA Vol. I para el vocabulario de arquitectura
(segmentos espacial / control / usuario).

## Constelaciones globales / regionales / aumentación

Sin lab propio. El path trabaja Galileo como constelación primaria
(F/NAV, E1/E5a, OSNMA) y GPS como contraste (Klobuchar, C/A); esa
exposición comparada es la base real. La aumentación (SBAS/EGNOS) aparece
conceptualmente en el Lab 5.3 y como proyecto del máster. Lectura:
Navipedia (arquitecturas GPS/Galileo/GLONASS/BeiDou, SBAS).

## Arquitectura de receptores

Se cubre con mod2 (Labs 2.1–2.4), listado en el Bloque 3: el pipeline del
receptor recorrido desde adentro — generación de réplicas, adquisición,
tracking y demodulación, receptor de referencia. Lo que el temario
presenta como diagrama de bloques acá corre como código. Ver Bloque 3.

## Técnicas de posicionamiento fiable y preciso

- [ ] **Lab 1.1 — Trilateración** (`mod1-posicionamiento/clase1.1`).
  2D y 3D con distancias exactas, mínimos cuadrados. Validación:
  recuperar una posición conocida con error numérico despreciable.
- [ ] **Lab 1.2 — Pseudodistancias y sesgo de reloj** (`mod1/clase1.2`).
  El bias del receptor como cuarta incógnita; por eso hacen falta 4
  satélites. Gauss-Newton. Validación: convergencia en pocas iteraciones
  incluso arrancando desde el centro de la Tierra.
- [ ] **Lab 1.4 — DOP y geometría** (`mod1/clase1.4`). Matriz de
  geometría G de una época real, GDOP/PDOP/HDOP/VDOP/TDOP, skyplot.
  Validación: el PDOP empeora al enmascarar satélites bajos o con
  geometría casi coplanar.

Lo "fiable" (integridad) y lo "preciso" (diferencial/PPP) del título se
desarrollan en el Bloque 2.

## Observables: código / fase / Doppler / SNR

Cada observable se trabaja donde más rinde:

- **Código**: pseudodistancias reales C1X/C5X en el Lab 1.5.
- **Fase de portadora**: L1X/L5X (ciclos → metros) en las combinaciones
  código-menos-fase del Lab 3.4; ahí el contraste de ruido código vs.
  fase.
- **Doppler**: como dimensión de búsqueda en la adquisición (Lab 2.2);
  como observable de velocidad, en el EKF del Lab 7.2.
- **SNR / C/N0**: medido y usado en 2.2–2.3; observable centinela
  anti-spoofing (6.4).

## Errores y modelos de caracterización / corrección

- [ ] **Lab 3.1 — Modelos ionosféricos broadcast** (`mod3-errores/
  clase3.1`). Klobuchar (GPS) y NeQuick-G (Galileo). Validación: máximos
  a primeras horas de la tarde local y a baja elevación.
- [ ] **Lab 3.2 — Combinación libre de ionosfera** (`mod3/clase3.2`).
  Observables reales E1/E5a: iono-free, BGD, comparación contra
  monofrecuencia. Validación: mejora en la vertical y trade-off sesgo vs.
  ruido medido.
- [ ] **Lab 3.4 — Multipath y ruido** (`mod3/clase3.4`). MP1/MP5 por
  sub-arcos, firma por elevación y repetición sideral Galileo (ciclo de
  10 días). Validación: correlación > 0.5 en el lag sideral teórico.

La síntesis del módulo de errores: lo grande y predecible se modela
(tropo), lo grande y salvaje se mide (iono), lo local se mitiga y observa
(multipath), lo blanco se promedia (ruido).

## Órbitas & relojes atómicos

- [ ] **Lab 1.3 — De efemérides a posición del satélite** (`mod1/clase1.3`).
  RINEX de navegación Galileo → ecuación de Kepler (iterativa) → plano
  orbital → ECEF con correcciones armónicas (Cuc/Cus, Crc/Crs, Cic/Cis).
  Validación: comparar contra SP3 o contra georinex/RTKLIB; diferencia de
  orden métrico o mejor.
- [ ] **Lab 4.1 — Propagador kepleriano vs. realidad**
  (`mod4-orbitas/clase4.1`). Propagar la misma efeméride apagando
  familias de correcciones del ICD (Δn, armónicos, IDOT) y medir qué
  absorbe cada una; saltos de empalme entre efemérides; divergencia de la
  elipse pura extrapolada. Validación: firma temporal de cada corrección
  (qué se anula en Toe) y empalmes sub-métricos.
- El **reloj del satélite** (af0/af1/af2 + término relativista de
  excentricidad) se implementa dentro del motor PVT del Lab 1.5. La
  comparación contra relojes precisos y los tipos de reloj (RAFS vs. PHM)
  van en el Bloque 4 (Lab 4.3).

## Propagación atmosférica: ionosfera, troposfera

- [ ] **Lab 3.3 — Troposfera** (`mod3/clase3.3`). Saastamoinen (ZHD+ZWD)
  + función de mapeo; retardo cenital (~2.3 m) y amplificación a baja
  elevación; PVT con tres troposferas. La física de la propagación iono
  está en 3.1–3.2: dispersiva en L, retrasa código y adelanta fase.

## Cálculo de posición (PVT) y filtros de estimación básicos

- [ ] **Lab 1.5 — Solución PVT completa** (`mod1/clase1.5`). RINEX real
  (estación IGS LPGS) + nav: reloj del satélite, Sagnac, iono/tropo
  simples. Validación: error < ~5–10 m contra coordenadas oficiales de la
  estación. Es el motor que reusan 3.2, 3.3, 4.1 y todo lo que sigue.
- Extensión natural de estimación básica: pesos por elevación (WLS) — se
  retoma al armar el KF (7.1). Los filtros más allá de LSQ (KF/EKF) son
  Bloque 2.

**Checkpoints B1:**
- ¿Qué mide una pseudodistancia y por qué no es una distancia?
- ¿Por qué hay que rotar la posición del satélite por el tiempo de vuelo?
- ¿Qué le pasa a la solución (y al GDOP) con satélites casi coplanares?
- ¿Por qué la ionosfera es dispersiva en banda L y la troposfera no?
- ¿Qué signo tiene el efecto ionosférico en código vs. fase?
- ¿Por qué la efeméride broadcast tiene 16 parámetros y no 6?

**Referencias B1:** ESA *GNSS Data Processing Vol. I*; Navipedia; Galileo
OS SIS ICD.

---

# BLOQUE 2 — ADVANCED

Técnicas avanzadas usadas hoy en el sector. Las clases viven en
`mod5-integridad/` y `mod7-estimacion/` (por construir).

## Técnicas de fiabilidad e integridad para aplicaciones críticas

Objetivo: pasar de "la solución da bien" a "puedo acotar y garantizar el
error". Reusa el motor PVT de 1.5.

- [ ] **Lab 5.1 — RAIM por residuos.** Test chi-cuadrado sobre los
  residuos. Inyectar un fallo (bias de 50–100 m en una pseudodistancia) y
  detectarlo. Validación: el estadístico supera el umbral con fallo y no
  sin fallo (calibrar falsa alarma).
- [ ] **Lab 5.2 — Identificación y exclusión.** Con ≥6 satélites:
  soluciones por subconjuntos para identificar el satélite fallado y
  excluirlo. Validación: la solución post-exclusión vuelve al error
  nominal.
- [ ] **Lab 5.3 — Protection levels.** HPL/VPL simplificado contra alert
  limits de una operación tipo aproximación; disponibilidad de integridad
  (PL < AL). Base conceptual de SBAS/EGNOS.
- [ ] **Lectura dirigida — ARAIM.** ISM, hipótesis de fallo múltiple.
  Resumen de una página.

## Técnicas diferenciales (estaciones de referencia)

- [ ] **Lab 7.3 — Posicionamiento diferencial (DGNSS).** LPGS como base
  (coordenadas oficiales) y CORD como rover (`fetch_data.py` baja ambas):
  correcciones de pseudodistancia por satélite. El baseline La
  Plata–Córdoba es largo a propósito: medir qué se cancela (reloj del
  satélite, efeméride) y qué decorrelaciona (iono, tropo) con la
  distancia. Validación: mejora parcial + explicación cuantitativa de por
  qué DGNSS operativo usa baselines cortos. Opcional: repetir con una
  estación RAMSAC cercana.

## Técnicas de precisión centimétrica

- [ ] **Lab 7.4 — PPP-lite (solo código).** Iono-free + órbitas SP3 +
  relojes CLK precisos + Saastamoinen con ZWD estimado como incógnita
  (la extensión ⭐⭐⭐ del 3.3). Sin ambigüedades de fase la precisión
  queda en dm–m con convergencia lenta: documentar por qué el PPP real
  necesita la fase de portadora (y RTK, la resolución de ambigüedades).
  Validación: mejora neta contra broadcast en las mismas épocas.

## Técnicas de resiliencia: sensor fusion

- [ ] **Lab 7.5 — Fusión GNSS+INS.** Filtro de Kalman loosely-coupled en
  2D con IMU sintética: el INS puentea cortes de GNSS y el GNSS frena la
  deriva del INS. Puerta de entrada al proyecto de fusión del máster.
  Depende de 7.1.

## Modelos avanzados de estimación: KF, EKF

- [ ] **Lab 7.1 — Filtro de Kalman desde cero.** Primero 1D didáctico;
  después filtrar la serie de soluciones época a época del 1.5 con modelo
  de velocidad constante (estados: posición, velocidad, sesgo y deriva de
  reloj). Validación: el KF reduce el scatter del LSQ suelto y la
  secuencia de innovaciones es blanca (si no, el modelo de ruido está
  mal).
- [ ] **Lab 7.2 — EKF sobre pseudodistancias y Doppler.** EKF directo
  sobre los observables (medición no lineal; el jacobiano es la matriz de
  geometría de 1.4), incorporando Doppler como observable de velocidad.
  Validación: equivalencia con LSQ+KF en estático, y ventaja con pocos
  satélites (sigue dando solución con 3 SVs por el modelo de dinámica —
  y ahí se ve el riesgo de confiar en el modelo).

**Checkpoints B2:**
- Definir y distinguir: exactitud, integridad, continuidad,
  disponibilidad.
- ¿Por qué RAIM necesita redundancia (≥5 para detectar, ≥6 para excluir)?
- ¿Qué relación hay entre protection level y alert limit?
- ¿Qué agrega un KF sobre LSQ época a época, y qué rompe si el modelo de
  dinámica o de ruido está mal?
- ¿Por qué el diferencial cancela unos errores y otros no? ¿Qué decide la
  longitud útil del baseline?
- ¿Por qué PPP necesita productos precisos y fase para llegar a cm?

**Referencias B2:** ESA Vol. I (estimación y PPP); Navipedia (RAIM,
Kalman Filter, DGNSS, PPP); material ARAIM (WG-C); RTKLIB.

---

# BLOQUE 3 — SIGNALS

Procesamiento de señales en receptores, de las muestras IQ a los bits, y
la seguridad de la señal. Las clases de seguridad viven en
`mod6-seguridad/` (por construir).

## Definición y procesamiento de señales GNSS

- [ ] **Lab 2.1 — Generación de códigos** (`mod2-senales/clase2.1`).
  Códigos C/A con LFSR G1/G2; autocorrelación y correlación cruzada.
  Validación: pico en 1023 y lóbulos acotados según la familia Gold.

## Técnicas de adquisición y tracking

- [ ] **Lab 2.2 — Adquisición** (`mod2/clase2.2`). Sobre capturas IQ
  reales (gnss-sdr): búsqueda paralela en fase de código vía FFT ×
  grilla Doppler. Validación: PRN presentes detectados con su Doppler y
  fase de código.
- [ ] **Lab 2.3 — Tracking y bits** (`mod2/clase2.3`). DLL
  early–prompt–late + PLL/Costas; demodulación de bits sobre señal
  sintética. Validación: BER 0% y preámbulo del mensaje detectado.
- [ ] **Lab 2.4 — Receptor de referencia** (`mod2/clase2.4`). gnss-sdr
  sobre el mismo dataset, comparado contra los resultados propios de
  2.2/2.3.

## Autenticación Galileo OSNMA / SAS

- [ ] **Lab 6.1 — Primitivas OSNMA.** Implementar y verificar las tres
  piezas criptográficas: cadena TESLA (revelación diferida, verificación
  hacia el KROOT), prueba de inclusión de Merkle contra la raíz embebida,
  y firma ECDSA P-256 del DSM-KROOT. Validación: cada primitiva verifica
  contra vectores/datos reales.
- [ ] **Lab 6.2 — Cadena de confianza en vivo.** Raíz de Merkle → clave
  pública → KROOT → claves TESLA → tags → datos de navegación
  autenticados, corriendo contra el feed de galmon.eu. Operativa: logs de
  autenticación y relevo entre cadenas (Chain ID). Validación:
  autenticación sostenida en vivo.
- [ ] **Lab 6.6 — Threat model de OSNMA/SAS.** Documento corto (estilo
  ADR): qué ataque mitiga cada primitiva y qué queda afuera. Clave: OSNMA
  autentica los **datos** de navegación, no el rango — replay/meaconing
  dentro de la ventana temporal sigue siendo un vector; la autenticación
  a nivel de señal (SAS/ACAS sobre E6-C) es la línea complementaria.
  Incluir la capa de plausibilidad física de efemérides del Lab 4.1
  (semieje MEO, salto de empalme, consistencia orbital) como defensa
  ortogonal: cripto + física.

## Análisis de interferencias y spoofing

- [ ] **Lab 6.3 — Anatomía de un spoofing con TEXBAT.** La adquisición
  del 2.2 sobre los escenarios TEXBAT (UT Austin): pico falso junto al
  auténtico, saltos de C/N0, deriva de reloj inducida.
- [ ] **Lab 6.4 — Detectores de consistencia.** 2–3 chequeos clásicos:
  C/N0, deriva anómala del reloj, salto de posición/velocidad,
  consistencia cruzada entre constelaciones. Validación: disparan en
  TEXBAT y no en datos limpios.
- [ ] **Lab 6.5 — Jamming.** IQ con interferencia (real o sintética):
  espectrograma, detección por energía/AGC, degradación de C/N0 y pérdida
  de tracking.

## Simulación de señales (Skydel)

Se hace en el máster (licencia comercial). El generador sintético del Lab
2.3 (señal con código, portadora, datos y ruido calibrado) es el
sustituto casero y la base conceptual para entender qué simula Skydel.

**Checkpoints B3:**
- ¿Por qué la búsqueda por FFT equivale a la correlación circular?
- ¿Qué representa el C/N0 y por qué es un observable centinela
  anti-spoofing?
- ¿Por qué la seguridad de TESLA depende de sincronización de tiempo
  "suficientemente buena" (loose time sync)?
- ¿Qué NO protege OSNMA y cómo se complementa (SAS/ACAS, consistencia,
  sanidad física de efemérides)?
- ¿Qué observables delatan un spoofing barato vs. uno sofisticado?

**Referencias B3:** Borre & Akos; Kaplan & Hegarty; gnss-sdr; Galileo
OSNMA SIS ICD + Receiver Guidelines (GSC); TEXBAT / Radionavigation Lab
UT Austin (Humphreys).

---

# BLOQUE 4 — SYSTEM

Inmersión en los sistemas espaciales europeos: la vista desde el segmento
terreno. Las clases viven en `mod4-orbitas/`.

## Arquitectura segmento terreno: Galileo y EGNOS

Sin lab propio; lectura dirigida (GSC, Navipedia: Galileo Ground Segment,
EGNOS architecture). Conexiones del path: **galmon.eu** es telemetría en
vivo de lo que emite la constelación (Lab 6.2); los **saltos de empalme
del Lab 4.1** son la huella observable del segmento de control
re-ajustando efemérides — monitorearlos es QC del segmento visto desde el
usuario.

## Algoritmos de validación y pre-procesado

Se ejercita de forma transversal: partición por sub-arcos y saltos (3.4),
detección de empalmes (4.1), filtrado de satélites/observables en el
motor 1.5. Sin clase propia; al llegar al máster, mapear estos chequeos a
la cadena formal de pre-procesado.

## Algoritmos de órbita (POD / OD&TS)

- [ ] **Lab 4.2 — Broadcast vs. órbitas precisas** (`mod4/clase4.2`).
  Descargar SP3 (MGEX), interpolar (Lagrange de orden alto entre épocas
  de 5–15 min) y comparar contra broadcast por constelación, con
  descomposición RTN. Validación: diferencias sub-métricas a métricas; la
  radial es la que pesa en el rango; Galileo típicamente entre las
  mejores. El POD propio (estimar la órbita desde observaciones) es el
  proyecto LEO-OD del máster.

## Sincronización de relojes y escalas de tiempo atómicas

- [ ] **Lab 4.3 — Relojes** (`mod4/clase4.3`). Corrección broadcast
  (af0/af1/af2) contra CLK precisos; estabilidad por tipo de reloj (RAFS
  vs. máser pasivo de hidrógeno). Validación: el PHM muestra menor
  deriva.
- [ ] **Lab 4.4 — Escalas de tiempo y marcos** (`mod4/clase4.4`). GPST,
  GST, UTC, TAI, leap seconds; GGTO para mezclar GPS+Galileo; ECEF vs.
  ECI; ITRF vs. WGS84/GTRF. Entregable: `timescales.py` con tests.

## Algoritmos de estimación de la ionosfera

La base es 3.1 (modelos broadcast) y 3.2 (medición del retardo con doble
frecuencia — la semilla de toda estimación iono). La estimación a nivel
sistema (grillas TEC tipo SBAS, mapas globales) es teoría del máster;
llegar con 3.1–3.2 sólidas es la preparación correcta.

## Cadena de integridad y detección de ataques del sistema

Se arma con piezas de otros bloques: RAIM e identificación de fallos
(5.1–5.2), detectores de consistencia (6.4), threat model y plausibilidad
física de efemérides (6.6 + 4.1). La vista "de sistema" del máster
integra esas capas de usuario con el monitoreo de tierra.

**Checkpoints B4:**
- ¿Por qué GPST no tiene leap seconds y UTC sí?
- ¿Qué es el GGTO y qué alternativa existe (sesgo inter-sistema como
  incógnita)?
- ¿Qué significa POD y qué observables/estaciones lo hacen posible?
- ¿Qué revela el salto de empalme entre efemérides sobre la calidad del
  segmento de control?

**Referencias B4:** ESA Vol. I (tiempo y marcos); Navipedia (Time
References, Reference Frames, Ground Segment); formatos SP3/CLK del IGS.

---

# BLOQUE 5 — FUTURE & TRENDS

Lectura para llegar con contexto; sin labs obligatorios.

- **LEO-PNT / Alternative PNT**: señales desde órbita baja
  (demostraciones de ESA, constelaciones comerciales tipo Xona):
  geometría que cambia rápido, más potencia recibida, implicancias
  anti-jamming.
- **Navegación lunar (Moonlight)**: Moonlight (ESA), LunaNet (NASA/ESA) y
  el problema de POD en órbita lunar.
- **Comunicaciones satelitales (SatCom)**: panorama general; el máster lo
  toca como tendencia.

---

## Workshops del máster — dónde los cubre el path

**En el path:** Python con buenas prácticas y Git (todo el repo),
estadística/ruido/covarianzas (prerrequisitos, 1.4), dinámica orbital con
RINEX/SP3 (mod4), fundamentos de señales (2.1), LSE (prerrequisitos, 1.2)
y EKF (7.2), acquisition/tracking (2.2–2.3), autenticación OSNMA/SAS
(6.1–6.2), sistemas de referencia y escalas de tiempo (4.4), herramientas
de técnicas precisas (7.3–7.4).

**Cubiertos por el perfil profesional:** automatización Bash/Linux,
virtualización (Docker/Kubernetes), Machine Learning, programación y
validación con asistentes de código (el workshop Codex del temario).

**Se hacen en el máster (no invertir antes):** C/C++ y simulación de
señales con Skydel. TLE/YUMA como formatos: lectura corta al pasar por
4.2 alcanza.

---

## Proyecto del máster — preparación para elegir

| Proyecto | Base en este path | Salto a cubrir en el máster |
|---|---|---|
| LEO-OD (determinación de órbita en LEO) | mod4, prerreq. orbital | dinámica LEO (arrastre), estimación orbital |
| SBAS (posicionamiento fiable p/ aviación) | 5.1–5.3, 3.1–3.2 | mensajes SBAS, grillas iono, PL certificables |
| PPP (motor centimétrico) | 7.4, 4.2–4.3, mod3 | fase de portadora, ambigüedades, convergencia |
| Fusión GNSS/INS resiliente | 7.1–7.2, 7.5 | mecanización INS, tightly-coupled |
| Simulación de señales y amenazas | mod2, mod6 | Skydel, escenarios de ataque end-to-end |

Los dos calces naturales del perfil: **simulación de señales y amenazas**
(capitaliza el diferencial de ciberseguridad + mod2 + mod6) o **LEO-OD**
(credencial de ingeniero GNSS de núcleo duro, sobre mod4). Decisión final
en el máster, con más información de cada work-package.

---

## Secuencia de cursada sugerida

El documento ordena por temario; la cursada óptima va por dependencias
(cada clase reusa la anterior). Tiempos orientativos a ritmo part-time;
el path puede seguir en paralelo al máster, fase a fase con el bloque
correspondiente.

1. **Fase 0 — Prerrequisitos y entorno** (~1 semana). Venv, refrescos de
   mod0, fetch_data operativo.
2. **Fase 1 — Posicionamiento** (B1: labs 1.1 → 1.2 → 1.4 → 1.5,
   ~2–3 semanas). Termina con el motor PVT andando contra LPGS.
3. **Fase 2 — Señal** (B3: 2.1 → 2.4, ~3–4 semanas). El tramo más denso;
   habilita todo lo anti-spoofing.
4. **Fase 3 — Errores** (B1: 3.1 → 3.4, ~2 semanas). Refina el PVT.
5. **Fase 4 — Órbitas y tiempo** (B1/B4: 4.1 → 4.4, ~2–3 semanas).
6. **Fase 5 — Integridad** (B2: 5.1 → ARAIM, ~1.5–2 semanas).
7. **Fase 6 — Estimación y precisas** (B2: 7.1 → 7.2 → 7.3 → 7.4,
   ~2–3 semanas). KF/EKF antes que todo lo que los usa.
8. **Fase 7 — Seguridad de señal** (B3: 6.1 → 6.6, ~3 semanas). El
   diferencial del perfil.
9. **Fase 8 — Fusión y frontera** (7.5 + lecturas B5).

---

## Referencias generales

- Sanz Subirana, Juan Zornoza & Hernández-Pajares — *GNSS Data Processing,
  Vol. I (Fundamentals) & Vol. II (Laboratory Exercises)*, ESA TM-23. PDF
  gratuito; el Vol. II es en sí mismo un set de labs complementario.
- Navipedia (ESA) — referencia rápida por tema.
- Galileo OS SIS ICD; Galileo OSNMA SIS ICD + OSNMA Receiver Guidelines
  (European GNSS Service Centre).
- Kaplan & Hegarty — *Understanding GPS/GNSS: Principles and Applications*.
- Borre, Akos et al. — *A Software-Defined GPS and Galileo Receiver*.
- Herramientas de referencia cruzada: RTKLIB, gnss-sdr, georinex.
