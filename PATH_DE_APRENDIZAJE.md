# Path de aprendizaje — Pre-preparación para el JSNP Master (GNSS Academy)

Autor: Maximiliano Iriart (mmiriart)
v2 — reescritura del temario v1 en formato de labs (julio 2026)

Mismo mapeo a los seis módulos del JSNP Master que la v1, pero cada tema se
convierte en un lab con datos reales, entregable y criterio de validación.
La regla: un concepto no está aprendido hasta que corre en Python.

---

## Cómo usar este path

- **Un lab = un script o notebook** en `labs/modX-nombre/`, con un README
  corto (objetivo, datos usados, resultado).
- **Validación siempre cuantitativa**: comparar contra una referencia
  (coordenadas oficiales de una estación, productos precisos, salida de
  RTKLIB/gnss-sdr). Si no hay número, no hay validación.
- **Checkboxes de progreso**: `[x]` marca lo ya hecho en el lab OSNMA y en
  los primeros labs de posicionamiento; ajustar si el estado real difiere.
- Los checkpoints de cada módulo son preguntas de autoevaluación: si no se
  pueden responder sin mirar el código, el módulo no está cerrado.

### Estado de avance

| Módulo | Mapeo JSNP | Estado |
|---|---|---|
| 0 — Setup y prerrequisitos | — | En curso (entorno operativo) |
| 1 — Fundamentos de posicionamiento | Algorithms & Positioning | En curso (labs 1.1–1.3) |
| 2 — Procesamiento de señal y SDR | Signal Processing | Pendiente |
| 3 — Fuentes de error | Ionosphere Impact | Pendiente |
| 4 — Órbitas y tiempo | Orbits Estimation & Clocks Synchro | Pendiente |
| 5 — Integridad | Reliability & Integrity | Pendiente |
| 6 — Seguridad y autenticación | Safety & Authentication | Parcial (criptografía hecha; anti-spoofing aplicado pendiente) |

---

## Módulo 0 — Setup y prerrequisitos *(nuevo en v2)*

Entorno de referencia: WSL2 Ubuntu 24.04 (PCHOME), Python 3.12 en venv.

- [x] **Entorno base.** venv + `numpy scipy matplotlib pandas cryptography`
  (ya operativo por el lab OSNMA). Agregar para este path:
  `georinex hatanaka unlzw3`.
- [x] **Refresco matemático dirigido.** Mínimos cuadrados y su versión
  ponderada, jacobianos y linealización, matrices de rotación 3D.
  Entregable: mini-notebook resolviendo un ajuste no lineal genérico con
  Gauss-Newton escrito a mano (sin `scipy.optimize`).
- [x] **Mecánica orbital mínima.** Elementos keplerianos; anomalía media,
  excéntrica y verdadera; qué perturba una órbita real (J2, presión de
  radiación). Solo lo necesario para leer una efeméride.
- [x] **Pipeline de datos.** Script `tools/fetch_data.py` que descargue y
  descomprima RINEX (nav y obs) y productos SP3/CLK. Fuentes:
  - RINEX y productos: BKG (`igs.bkg.bund.de`), CDDIS (requiere cuenta
    Earthdata de NASA).
  - **Argentina: RAMSAC (IGN)** — red CORS nacional con RINEX descargable;
    ideal para validar contra coordenadas oficiales de estaciones locales.
  - Productos precisos multi-GNSS: MGEX (centros CODE, GFZ, Wuhan).
  - Mensaje de navegación en vivo: **galmon.eu** (ya usado en OSNMA).

**Checkpoint M0:** explicar por qué linealizar el problema PVT lo convierte
en mínimos cuadrados iterativos, y qué rol juega el jacobiano (matriz de
geometría) en cada iteración.

---

## Módulo 1 — Fundamentos de posicionamiento

Mapea a **"Algorithms & Positioning"**.
Objetivo: llegar desde "distancias a puntos conocidos" hasta una solución
PVT completa con observaciones reales.

- [x] **Lab 1.1 — Trilateración.** 2D y 3D con distancias exactas, resuelto
  por mínimos cuadrados. Validación: recuperar una posición conocida con
  error numérico despreciable.
- [x] **Lab 1.2 — Pseudodistancias y sesgo de reloj.** El bias del receptor
  como cuarta incógnita; por eso hacen falta 4 satélites. Gauss-Newton.
  Validación: convergencia en pocas iteraciones incluso arrancando desde el
  centro de la Tierra.
- [ ] **Lab 1.3 — De efemérides a posición del satélite.** RINEX de
  navegación Galileo → ecuación de Kepler (iterativa) → plano orbital →
  ECEF con correcciones armónicas (Cuc/Cus, Crc/Crs, Cic/Cis).
  Validación: comparar contra SP3 o contra la salida de georinex/RTKLIB;
  diferencia de orden métrico o mejor.
- [x] **Lab 1.4 — DOP y geometría.** Construir la matriz de geometría G de
  una época real y calcular GDOP/PDOP/HDOP/VDOP/TDOP. Graficar un skyplot.
  Validación: el PDOP empeora al enmascarar satélites de baja elevación o
  al quedarse con satélites casi coplanares.
- [x] **Lab 1.5 — Solución PVT completa.** RINEX de observación real
  (estación RAMSAC o IGS) + nav. Incluir: corrección de reloj del satélite
  (af0/af1/af2 + término relativista de excentricidad), rotación terrestre
  durante el tiempo de vuelo (efecto Sagnac), correcciones simples de
  ionosfera y troposfera (se refinan en M3). Validación: error < ~5–10 m
  contra las coordenadas oficiales de la estación.

**Checkpoints M1:**
- ¿Qué mide realmente una pseudodistancia y por qué no es una distancia?
- ¿Por qué hay que rotar la posición del satélite por el tiempo de vuelo?
- ¿Qué le pasa a la solución (y al GDOP) si los satélites usados están casi
  en un mismo plano?

**Referencias:** ESA *GNSS Data Processing Vol. I* (caps. de modelado y
posicionamiento); Navipedia; Galileo OS SIS ICD (algoritmo de efemérides).

---

## Módulo 2 — Procesamiento de señal y SDR

Mapea a **"Signal Processing"**.
Objetivo: entender la señal desde las muestras IQ crudas hasta los bits del
mensaje. Prerrequisito de los labs anti-spoofing del Módulo 6.

Conceptos: estructura código + portadora + datos; GPS C/A (códigos Gold,
1023 chips a 1.023 Mcps); Galileo E1 (códigos de memoria, modulación CBOC,
canal piloto E1-C); relación C/N0.

- [x] **Lab 2.1 — Generación de códigos.** Implementar los códigos C/A con
  los registros LFSR G1/G2 y verificar autocorrelación y correlación
  cruzada. Validación: pico de autocorrelación en 1023 y lóbulos laterales
  acotados según la familia Gold.
- [x] **Lab 2.2 — Adquisición.** Sobre un dataset IQ público (los de
  gnss-sdr sirven): búsqueda paralela en fase de código vía FFT
  (correlación circular) × grilla Doppler (~±5 kHz para receptor estático).
  Validación: detectar los PRN presentes en el dataset con su Doppler y
  fase de código.
- [ ] **Lab 2.3 — Tracking y bits.** DLL early–prompt–late para código y
  PLL/Costas para portadora; demodular bits de navegación.
  Validación: encontrar el preámbulo del mensaje (GPS LNAV: `10001011`).
- [ ] **Lab 2.4 — Receptor de referencia.** Correr gnss-sdr sobre el mismo
  dataset y comparar contra los resultados propios de 2.2/2.3. Opcional con
  hardware: RTL-SDR + antena GPS activa en PCHOME.

**Checkpoints M2:**
- ¿Por qué la búsqueda por FFT equivale a la correlación circular en fase
  de código?
- ¿Qué representa el C/N0, y qué rango es normal a cielo abierto
  (~35–50 dB-Hz)? ¿Por qué es un observable clave para detectar spoofing?

**Referencias:** Borre & Akos, *A Software-Defined GPS and Galileo
Receiver*; Kaplan & Hegarty; documentación de gnss-sdr.

---

## Módulo 3 — Fuentes de error

Mapea a **"Ionosphere Impact"**.
Objetivo: cuantificar cada error del Lab 1.5 y reducirlo.

- [ ] **Lab 3.1 — Modelos ionosféricos broadcast.** Implementar Klobuchar
  (GPS) y usar la implementación de referencia de NeQuick-G (Galileo, ESA
  publica el código) o un port a Python. Graficar retardo vs. elevación y
  hora local. Validación: máximos a primeras horas de la tarde local y a
  baja elevación.
- [ ] **Lab 3.2 — Combinación libre de ionosfera.** Con observables de
  doble frecuencia (E1/E5a o L1/L5): formar la combinación iono-free y
  comparar la solución contra monofrecuencia; estimar el retardo oblicuo
  eliminado. Validación: mejora clara en la componente vertical.
- [ ] **Lab 3.3 — Troposfera.** Modelo de Saastamoinen + función de mapeo
  simple. Cuantificar el retardo cenital (~2.3 m) y su amplificación a baja
  elevación; efecto en la vertical de la solución.
- [ ] **Lab 3.4 — Multipath y ruido.** Con una estación real: combinaciones
  de multipath código-menos-fase (MP1/MP2) y análisis por elevación.
  Validación: el multipath crece a baja elevación y se repite con la
  geometría sideral día a día.

**Checkpoints M3:**
- ¿Por qué la ionosfera es dispersiva en banda L y la troposfera no, y qué
  habilita eso (doble frecuencia)?
- ¿Qué signo tiene el efecto ionosférico en código vs. fase de portadora?

**Referencias:** ESA *GNSS Data Processing Vol. I* (caps. de errores);
Navipedia (Klobuchar, NeQuick-G, Saastamoinen).

---

## Módulo 4 — Órbitas y tiempo

Mapea a **"Orbits Estimation & Clocks Synchro"**.

- [ ] **Lab 4.1 — Propagador kepleriano vs. realidad.** Propagar una órbita
  ideal de dos cuerpos y compararla contra la efeméride broadcast en un
  arco de horas: el residuo son las perturbaciones que la efeméride absorbe
  con sus correcciones.
- [ ] **Lab 4.2 — Broadcast vs. órbitas precisas.** Descargar SP3 (MGEX),
  interpolar (Lagrange de orden alto entre épocas de 5–15 min) y comparar
  contra broadcast por constelación. Validación: diferencias de orden
  sub-métrico a métrico; Galileo típicamente entre las mejores.
- [ ] **Lab 4.3 — Relojes.** Comparar la corrección broadcast (af0/af1/af2)
  contra archivos CLK precisos; graficar estabilidad por tipo de reloj
  (RAFS vs. máser pasivo de hidrógeno en Galileo). Validación: el PHM
  muestra menor deriva.
- [ ] **Lab 4.4 — Escalas de tiempo y marcos.** GPST, GST, UTC, TAI y leap
  seconds; el GGTO del mensaje de navegación para mezclar GPS+Galileo;
  ECEF vs. ECI; ITRF vs. WGS84/GTRF. Entregable: módulo
  `timescales.py` de conversión, con tests.

**Checkpoints M4:**
- ¿Por qué GPST no tiene leap seconds y UTC sí?
- ¿Qué es el GGTO y qué alternativa existe si no se usa (estimar el sesgo
  inter-sistema como incógnita extra)?
- ¿Qué significa "POD" y qué observables/estaciones lo hacen posible?

**Referencias:** ESA *GNSS Data Processing Vol. I* (tiempo y marcos de
referencia); Navipedia (Time References, Reference Frames); formatos SP3 y
CLK del IGS.

---

## Módulo 5 — Integridad

Mapea a **"Reliability & Integrity"**.
Objetivo: pasar de "la solución da bien" a "puedo acotar y garantizar el
error". Reusa la solución PVT del Lab 1.5.

- [ ] **Lab 5.1 — RAIM por residuos.** Test chi-cuadrado sobre los residuos
  de la solución. Inyectar un fallo (bias de 50–100 m en una
  pseudodistancia) y detectarlo. Validación: el estadístico supera el
  umbral con fallo y no lo supera sin fallo (calibrar falsa alarma).
- [ ] **Lab 5.2 — Identificación y exclusión.** Con ≥6 satélites: soluciones
  por subconjuntos para identificar el satélite fallado y excluirlo.
  Validación: la solución post-exclusión vuelve al error nominal.
- [ ] **Lab 5.3 — Protection levels.** Calcular un HPL/VPL simplificado y
  compararlo contra alert limits de una operación tipo aproximación.
  Concepto de disponibilidad de integridad (PL < AL).
- [ ] **Lectura dirigida — ARAIM.** Evolución multiconstelación del RAIM:
  ISM, hipótesis de fallo múltiple. Sin lab; resumen de una página.

**Checkpoints M5:**
- Definir y distinguir: exactitud, integridad, continuidad, disponibilidad.
- ¿Por qué RAIM necesita redundancia (≥5 satélites para detectar, ≥6 para
  excluir)?
- ¿Qué relación hay entre protection level y alert limit?

**Referencias:** Navipedia (RAIM, Integrity); material público de ARAIM
(working group WG-C).

---

## Módulo 6 — Seguridad y autenticación de señal

Mapea a **"Safety & Authentication"**. El módulo que conecta el perfil de
ciberseguridad con GNSS; la parte criptográfica ya está implementada y
validada en vivo.

### Hecho (lab OSNMA)

- [x] **TESLA**: cadena de claves con revelación diferida; verificación de
  cada clave hacia el KROOT.
- [x] **Merkle**: prueba de inclusión de la clave pública contra la raíz
  embebida en el receptor.
- [x] **ECDSA P-256**: verificación de la firma del DSM-KROOT.
- [x] **Cadena de confianza completa**: raíz de Merkle → clave pública →
  KROOT → claves TESLA → tags → datos de navegación autenticados, corriendo
  en vivo contra el feed de galmon.eu.
- [x] **Operativa**: análisis de logs de autenticación; relevo entre
  cadenas (Chain ID).

### Pendiente (labs aplicados — requieren Módulo 2)

- [ ] **Lab 6.1 — Anatomía de un spoofing con TEXBAT.** Correr la
  adquisición del Lab 2.2 sobre los escenarios TEXBAT (UT Austin, dataset
  público de spoofing grabado): observar la aparición del pico falso junto
  al auténtico, los saltos de C/N0 y la deriva de reloj inducida.
- [ ] **Lab 6.2 — Detectores de consistencia.** Implementar 2–3 chequeos
  clásicos: monitoreo de C/N0, deriva anómala del reloj del receptor, salto
  de posición/velocidad, consistencia cruzada entre constelaciones.
  Validación: disparan en los escenarios TEXBAT y no en datos limpios.
- [ ] **Lab 6.3 — Jamming.** Sobre IQ con interferencia (real o sumada
  sintéticamente): espectrograma, detección por energía/AGC, degradación de
  C/N0 y pérdida de tracking. Relación con la resiliencia del receptor.
- [ ] **Lab 6.4 — Threat model de OSNMA.** Documento corto (estilo ADR):
  qué ataque mitiga cada primitiva y qué queda afuera. Clave: OSNMA
  autentica los **datos** de navegación, no el rango — replay/meaconing
  dentro de la ventana temporal sigue siendo un vector; la autenticación a
  nivel de señal (p. ej. ACAS sobre E6-C) es la línea complementaria.

**Checkpoints M6:**
- ¿Por qué la seguridad de TESLA depende de que el receptor tenga una
  sincronización de tiempo "suficientemente buena" (loose time sync)?
- ¿Qué NO protege OSNMA y cómo se complementa?
- ¿Qué observables delatan un spoofing barato vs. uno sofisticado?

**Referencias:** Galileo OSNMA SIS ICD y OSNMA Receiver Guidelines (GSC);
dataset TEXBAT y papers del Radionavigation Lab de UT Austin (Humphreys).

---

## Temas de frontera

Sin labs obligatorios; lectura y, si dan las ganas, un lab opcional.

- **LEO-PNT**: señales desde órbita baja (demostraciones de ESA,
  constelaciones comerciales tipo Xona): geometría que cambia rápido, más
  potencia recibida, implicancias para resiliencia anti-jamming.
- **Navegación lunar**: Moonlight (ESA), LunaNet (NASA/ESA) y el problema
  de POD en órbita lunar.
- **Fusión de sensores**: lab opcional — filtro de Kalman loosely-coupled
  GNSS+IMU en 1D/2D, como puente hacia navegación integrada.

---

## Secuencia sugerida

Dado lo ya hecho (criptografía de M6 completa, M1 avanzado), el orden que
minimiza bloqueos es:

1. Cerrar **M1** (labs 1.4–1.5) — 1–2 semanas.
2. **M2** completo — 3–4 semanas (el más denso; habilita M6 aplicado).
3. **M3** — 2 semanas (refina el Lab 1.5).
4. **M4** — 2 semanas.
5. **M5** — 1–2 semanas (reusa Lab 1.5).
6. **M6 aplicado** (6.1–6.4) — 2–3 semanas.

Total orientativo a ritmo part-time: **3–4 meses**, compatible como rampa
de entrada al JSNP.

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
