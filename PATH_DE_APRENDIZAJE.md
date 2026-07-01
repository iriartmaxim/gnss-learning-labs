# Path de aprendizaje — Pre-preparación para el JSNP Master (GNSS Academy)
Autor: Maximiliano Iriart (mmiriart)

Objetivo: llegar preparado al JSNP Master (máster industrial online de 6 meses,
Python/Linux/Git/ML, para ingenieros que transicionan desde otros campos).
Estrategia: el máster ENSEÑA estos temas; esta pre-preparación construye la base
para no ahogarse, y consolida la fortaleza propia (seguridad de señal).

## Dos órdenes posibles (y por qué este documento usa el lógico)
- Orden CRONOLÓGICO (como se hizo en la práctica): se empezó por seguridad/OSNMA,
  por venir de la ciberseguridad. Se entró a GNSS por esa puerta.
- Orden LÓGICO / pedagógico (este documento): de los cimientos al techo. La
  autenticación de señal es un tema AVANZADO que se apoya sobre todo lo demás, así
  que va al final, como culminación.
Nota clave: que la seguridad figure al final NO significa rehacerla. Ya está
dominada. El pendiente real de estudio son los fundamentos (Módulos 1-5).
En una frase: la seguridad es el destino; ya se llegó, ahora se construye el camino.

Ventaja de partida: el stack del máster (Python, Linux/WSL, Git) ya es fluido, y la
seguridad de señal (OSNMA) ya está dominada — el tema más nuevo y demandado del sector.
Hueco principal: los fundamentos "clásicos" de GNSS (posicionamiento, señal, órbitas).

Metodología: pasos chiquitos ejecutados en WSL, salida transcripta, repaso por paso
(qué es / dónde encaja / por qué importa / conexión con lo ya hecho). Cada módulo deja
scripts numerados + REGISTRO.md. Conceptual en chat; implementación en Claude Code.

================================================================
## MÓDULO 1 — Fundamentos de posicionamiento   [EN CURSO ~80%]
================================================================
La base absoluta. Mapea a "Algorithms & Positioning". Mayor hueco a cerrar.

Hecho:
- Trilateración 2D (intuición de los círculos) + solver linealizado.
- 3D con error de reloj: 4 incógnitas (X,Y,Z,bias) -> 4 satélites. Gauss-Newton.
- Lectura de RINEX de navegación real (georinex). Parámetros keplerianos.
- Cálculo de la posición XYZ real de un satélite Galileo (E12) desde efemérides:
  ecuación de Kepler -> orientación ECEF -> correcciones armónicas.
- DOP (GDOP/PDOP/TDOP): cómo la geometría amplifica el error.

Pendiente:
- Escalón 4: posicionamiento completo de punta a punta. RINEX de OBSERVACIÓN real
  (pseudodistancias), parsearlo, alinear tiempos con las efemérides, y correr el
  Gauss-Newton ya programado para recuperar la posición de un receptor REAL.

================================================================
## MÓDULO 2 — Procesamiento de señal y SDR   [PENDIENTE]
================================================================
Cómo nace la medición que usa el Módulo 1. Mapea a "Signal Processing".
Enfatizado en ambas charlas (receptores, sensibilidad dB-Hz, tracking).

Plan:
- Estructura de la señal GNSS: código C/A, portadora, mensaje de navegación.
- Adquisición: cómo el receptor "encuentra" un satélite (correlación con el código).
- Tracking: cómo lo sigue (lazos de seguimiento).
- Lab: GNSS-SDR con muestras crudas IQ, o adquisición de código C/A en Python.

================================================================
## MÓDULO 3 — Fuentes de error   [PENDIENTE]
================================================================
Por qué la posición no es perfecta. Mapea a "Ionosphere Impact" (+ tropo, relojes).

Plan:
- Ionosfera (la principal fuente de error) y su corrección.
- Troposfera, multipath, errores de reloj.
- Lab: cuantificar/modelar errores sobre RINEX; corrección ionosférica con doble
  frecuencia (L1/L5, E1/E5).

================================================================
## MÓDULO 4 — Órbitas y tiempo   [PENDIENTE]
================================================================
De dónde salen las posiciones de los satélites y el tiempo. Mapea a "Orbits
Estimation & Clocks Synchro". Fuerte en la charla lunar (POD, filtros de Kalman).

Plan:
- Profundizar el cálculo de órbita (ya iniciado en Módulo 1 con la posición de E12).
- Determinación precisa de órbita (POD); sincronización de relojes.
- Sistemas de tiempo (GST, UTC, GPS time) y de referencia (ECEF, marcos).
- Lab: propagar la posición de un satélite en el tiempo y graficar su órbita.

================================================================
## MÓDULO 5 — Integridad   [BASE YA HECHA]
================================================================
Cómo detectar cuándo NO confiar en la posición. Mapea a "Reliability & Integrity".

Plan:
- RAIM/ARAIM, protection levels, alert limits (formalizar lo visto en teoría).
- Conectar con el DOP del Módulo 1.
- Lab: detección de fallos por consistencia (RAIM) sobre observaciones reales.
- Progresión natural hacia el Módulo 6: integridad = ¿el dato está corrupto por
  causas naturales? -> autenticación = ¿el dato fue falsificado por un atacante?

================================================================
## MÓDULO 6 — Seguridad y autenticación de señal   [COMPLETADO]  <-- CULMINACIÓN
================================================================
La capa que protege todo lo anterior contra un adversario. Es un tema AVANZADO:
requiere entender efemérides, posicionamiento y errores para captar por qué importa.
Mapea a "Safety & Authentication" (el tema más nuevo y demandado). YA DOMINADO.

Hecho (fue lo primero cronológicamente, por venir de ciberseguridad):
- Interpretación del tablero OSNMA en vivo (osnmalib.eu) + cheatsheet.
- OSNMAlib sobre grabaciones SBF: autenticación de efemérides reales de Galileo.
- Experimento clave correcta (PKID2) vs incorrecta (PKID1): la cadena se rompe.
- Proyecto 1: galmon-osnma compilado, OSNMA en vivo desde el feed de Galmon.
- Las TRES primitivas criptográficas construidas desde cero:
    * lab-tesla  : hash, cadena, revelación temporal, ataque, relevo de cadenas.
    * lab-merkle : árbol, prueba de inclusión, verificación.
    * lab-ecdsa  : par de claves, firma y verificación del KROOT.
- Proyecto 2: analizador de logs en Python (conteo, TTFAF, bits/satélite, gráficos, CLI).

El hilo conductor: las EFEMÉRIDES. Se autenticaron aquí (Módulo 6), se usan para
posicionar (Módulo 1) y reaparecen en órbitas (Módulo 4). Ese enrosque entre
seguridad y posicionamiento es el ángulo diferencial del perfil.

================================================================
## TEMAS DE FRONTERA (lectura transversal)   [TRANSVERSAL]
================================================================
Para el vocabulario del sector y conectar con el entorno de Eduardo:
- LEO-PNT, navegación lunar (Moonlight, LunaNet), POD lunar.
- Sensor Fusion (tema del máster): GNSS + IMU + altímetro. Encararlo tras el Módulo 4.

================================================================
## ORDEN DE ESTUDIO Y SIGUIENTE PASO
================================================================
El Módulo 6 (seguridad) ya está hecho. El estudio pendiente va de los cimientos
hacia arriba:
1. Cerrar Módulo 1 (Escalón 4)   <- siguiente paso inmediato
2. Módulo 2 (SDR / procesamiento de señal)
3. Módulo 3 (fuentes de error)
4. Módulo 4 (órbitas y tiempo)
5. Módulo 5 (integridad)
(Módulo 6 ya completado; frontera en paralelo, labs tras el Módulo 4.)
