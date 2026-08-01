# Constelaciones globales, regionales y aumentación

> Bloque del máster: B1 — Basics · Constelaciones globales / regionales / aumentación

**Objetivo en una frase**: conocer los cuatro GNSS globales
(GPS/GLONASS/Galileo/BeiDou), los regionales (QZSS/NavIC) y la
aumentación (SBAS/EGNOS), y por qué **este path usa Galileo como
constelación primaria y GPS como contraste**.

**Tiempo estimado**: 1–1.5 h (teoría 30' · lab 25' · ejercicios y cierre 30').

## 1. Objetivos

- [ ] Nombrar los 4 sistemas globales, su país/bloque y su banda abierta.
- [ ] Distinguir global vs regional vs aumentación.
- [ ] Contar los SVs reales de cada sistema en tu propio BRDC.
- [ ] Justificar por qué el path prioriza Galileo (E1/E5a, OSNMA) y usa GPS de contraste.

## 2. Dónde estás en el mapa

```mermaid
flowchart TB
    subgraph GLOB[Globales]
      GPS[GPS · EE.UU.] · GLO[GLONASS · Rusia] · GAL[Galileo · UE] · BDS[BeiDou · China]
    end
    subgraph REG[Regionales]
      QZSS[QZSS · Japón] · NAVIC[NavIC · India]
    end
    subgraph AUG[Aumentación]
      SBAS[SBAS/EGNOS/WAAS]
    end
    GLOB --> RX[tu receptor multi-GNSS]
    REG --> RX
    AUG --> RX
```

Es una clase de panorama: el detalle de cada sistema aparece en su lugar
(Galileo en mod2/mod6, GPS en 3.1, SBAS en 5.3). Acá se fija el mapa.

## 3. Teoría

### 1. Los cuatro globales

| Sistema | País/bloque | Satélites (nominal) | Órbita | Banda abierta | Rasgo del path |
|---|---|---|---|---|---|
| **GPS** | EE.UU. | ~31 | MEO ~20 200 km | L1 C/A | contraste (Klobuchar 3.1, C/A 2.1) |
| **GLONASS** | Rusia | ~24 | MEO ~19 100 km | L1OF (FDMA) | el "raro": FDMA, no CDMA |
| **Galileo** | UE | ~28 | MEO ~23 200 km | E1 (+OSNMA) | **primaria** (mod2, 1.3, mod6) |
| **BeiDou** | China | ~35 | MEO+IGSO+GEO | B1I/B1C | el más grande y heterogéneo |

Todas son **MEO** (órbita media, ~20 000 km) salvo la parte IGSO/GEO de
BeiDou. Distinta altura → distinto período y ground track (clase 0.3).

### 2. Regionales y aumentación

- **Regionales**: **QZSS** (Japón, órbitas IGSO que "cuelgan" sobre Asia-Pacífico) y **NavIC** (India, GEO+IGSO). No dan cobertura global: refuerzan una zona.
- **Aumentación (SBAS)**: no son un GNSS propio; son satélites GEO (EGNOS en Europa, WAAS en EE.UU., etc.) que **corrigen y monitorean** a los GNSS y transmiten integridad. Es la base conceptual de la clase 5.3 y de la aviación.

### 3. CDMA vs FDMA

Casi todos usan **CDMA** (todos en la misma frecuencia, se separan por
código — la clase 2.1). GLONASS legado usa **FDMA** (cada satélite en su
propia frecuencia): más difícil de procesar, por eso el path lo menciona
pero no lo trabaja en profundidad.

### 4. Por qué Galileo primaria

El path elige Galileo como hilo conductor porque: transmite en **E1/E5a**
abiertas y bien documentadas (OS SIS ICD), tiene **F/NAV** limpio para
efemérides (1.3), y es el único con **autenticación OSNMA** (mod6) — el
diferencial de perfil. GPS entra como **contraste** donde conviene:
Klobuchar (3.1) y el código C/A clásico (2.1).

## 4. Lab: censo comparado sobre tu BRDC

```bash
python3 clases/mod0-prerrequisitos/constelaciones/lab/lab_constelaciones_TODO.py
```

Contás los SVs únicos de cada sistema en el RINEX nav mixto del día 166 y
los contrastás con la capacidad nominal. La solución de referencia está
en `lab/soluciones/`.

### Tabla de validación (día 166, BRDC real)

| Sistema | SVs únicos en el BRDC |
|---|---|
| GPS | **32** |
| GLONASS | **27** |
| Galileo | **30** |
| BeiDou | **37** |
| **Globales (G+R+E+C)** | **126** |

(El BRDC cuenta todo satélite que **emitió** ese día —incluidos los
marginales—, por eso los números superan la constelación "nominal" y
difieren del SP3 preciso, que solo lista los de órbita calculada.
Discrepancia esperada, no error: la comentás en el lab.)

## 5. Ejercicios a mano

**E1.** De los cuatro globales, ¿cuál orbita más alto y cuál más bajo
(tabla §3.1)? Con la 3ª ley de Kepler (clase 0.3), ¿cuál tiene el período
más largo?

**E2.** Un receptor "GPS-only" ve 8 satélites; uno multi-GNSS ve 30.
¿Qué gana el multi-GNSS además de "más satélites" (pensá geometría/DOP,
clase 1.4, e integridad, mod5)?

**E3.** ¿Por qué SBAS **no** cuenta como un quinto GNSS global aunque
transmita desde el espacio?

## 6. Estimaciones Fermi

**F1.** Con ~120 satélites globales operativos repartidos en el cielo,
¿cuántos esperás sobre el horizonte en un instante desde un punto abierto?
(Regla: aprox. la mitad de cada constelación está del lado visible.)

**F2.** Galileo a 23 200 km vs GPS a 20 200 km: ¿cuánto más tarda la
señal de Galileo en llegar? (Δaltura / c.)

## 7. Preguntas conceptuales

Respuestas en `soluciones.md`.

**C1.** ¿Por qué "más constelaciones" mejora la posición aun con el mismo
receptor y el mismo ruido de medición?

**C2.** ¿Qué hace distinto a GLONASS que complica un receptor CDMA común?

**C3.** ¿Por qué al path le conviene Galileo y no GPS como sistema
primario, si GPS es el más conocido?

## 8. Pregunta de entrevista

> "Un cliente te pide un receptor 'multi-constelación'. ¿Qué sistemas
> incluirías, qué ganás con cada uno y qué complejidad agrega cada uno?"

## 9. Mini-simulacro (8 min, aprobás con 4/5)

1. Nombrá los 4 globales con su país.
2. ¿Cuál usa FDMA y qué implica?
3. Global vs regional vs aumentación: un ejemplo de cada uno.
4. ¿Qué banda abierta de Galileo trae autenticación?
5. ¿Por qué el BRDC lista más SVs que la constelación nominal?

## 10. Caso real — BeiDou y el salto a global (2020)

BeiDou completó su constelación global (BDS-3) en 2020, pasando de un
sistema regional a uno con **más satélites que cualquier otro GNSS** y una
arquitectura mixta MEO+IGSO+GEO única. En tu censo del día 166 eso se ve
directo: BeiDou aporta **37 SVs**, más que GPS (32) o Galileo (30). El
dato ilustra tres cosas del path: (1) el mundo GNSS es multipolar, no
"GPS y otros"; (2) la heterogeneidad orbital de BeiDou complica el
procesamiento uniforme; (3) un receptor moderno **tiene** que ser
multi-constelación para aprovechar la geometría disponible (mejor DOP,
clase 1.4; más redundancia para integridad, mod5).

## 11. Glosario ES/EN

| ES | EN | Nota |
|---|---|---|
| constelación | constellation | conjunto de satélites de un sistema |
| global / regional | global / regional | cobertura mundial vs zona |
| aumentación | augmentation (SBAS) | corrige/monitorea GNSS desde GEO |
| MEO / IGSO / GEO | MEO / IGSO / GEO | órbitas media / inclinada geosíncrona / geoestacionaria |
| CDMA / FDMA | CDMA / FDMA | separación por código vs por frecuencia |
| multi-GNSS | multi-GNSS | receptor que combina varios sistemas |

## 12. Cheat sheet

```text
Globales   GPS(EE.UU.,L1C/A) · GLONASS(Rusia,FDMA) · Galileo(UE,E1+OSNMA) · BeiDou(China,B1)
Regionales QZSS(Japón,IGSO) · NavIC(India,GEO+IGSO)
Aumentación SBAS: EGNOS(UE) · WAAS(EE.UU.) — GEO, corrigen e integridad → clase 5.3
Órbitas    todas MEO ~19-23 mil km (salvo IGSO/GEO de BeiDou)
Path       Galileo primaria (E1/E5a, F/NAV, OSNMA) · GPS contraste (Klobuchar, C/A)
Censo 166  G32 · R27 · E30 · C37 · globales 126 (BRDC cuenta todo el que emitió)
```

## 13. Errores comunes

1. Decir "GPS" para referirse a GNSS en general: GPS es **uno** de cuatro globales.
2. Contar SBAS como un GNSS: es aumentación, no navegación autónoma.
3. Esperar que el BRDC coincida con la constelación "nominal": lista todo el que emitió (incluye marginales).
4. Asumir que todos son CDMA: GLONASS legado es FDMA.
5. Creer que "más satélites" es solo cantidad: lo que importa es la **geometría** (DOP) y la **redundancia** (integridad).

## 14. Referencias

- Navipedia — "GNSS constellations", "GPS/GLONASS/Galileo/BeiDou", "SBAS".
- Galileo OS SIS ICD — bandas y estructura de Galileo (se usa en 1.3, 2.x).
- El censo del BRDC: clase 0.4 (`inspeccionar_datos.py`) y este lab.

### Para ver (en español)

- [¿Qué es y cómo funciona GNSS? — GPS Total](https://gpstotal.org/es/gps/gnss) — panorama de las constelaciones globales, regionales y SBAS.
- [Metodología GNSS — N. Garrido-Villén (UPV)](https://nagarvil.webs.upv.es/metodos-de-posicionamiento-gnss-gps/metodologia/) — sistemas, órbitas y observación.

## 15. Autoevaluación

- ⭐ Nombro los 4 globales, los regionales y qué es SBAS.
- ⭐⭐ Corro el censo sobre mi BRDC y explico por qué difiere del nominal y del SP3.
- ⭐⭐⭐ Justifico una arquitectura multi-GNSS para un caso concreto (geometría + integridad + complejidad).

## 16. Para tu bitácora

Copiá [`bitacora.md`](bitacora.md): tus números del censo vs la tabla, y
una frase sobre por qué el path eligió Galileo.
