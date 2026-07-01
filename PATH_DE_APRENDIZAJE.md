# Path de aprendizaje — Pre-preparación para el JSNP Master (GNSS Academy)
Autor: Maximiliano Iriart (mmiriart)

Temario de pre-preparación para el JSNP Master, ordenado de los fundamentos
a la seguridad de señal.

## Módulo 1 — Fundamentos de posicionamiento
Mapea a "Algorithms & Positioning".
- Trilateración: distancias a puntos conocidos determinan una posición.
- Pseudodistancias y error de reloj: por qué se necesitan 4 satélites.
- Resolución del sistema (Gauss-Newton).
- Lectura de RINEX de navegación. Parámetros keplerianos.
- Cálculo de la posición de un satélite desde efemérides:
  ecuación de Kepler -> orientación ECEF -> correcciones armónicas.
- DOP (GDOP/PDOP/TDOP): efecto de la geometría en la precisión.
- Posicionamiento completo con RINEX de observación (pseudodistancias reales).

## Módulo 2 — Procesamiento de señal y SDR
Mapea a "Signal Processing".
- Estructura de la señal GNSS: código C/A, portadora, mensaje de navegación.
- Adquisición: correlación con el código para encontrar un satélite.
- Tracking: lazos de seguimiento.
- SDR: procesamiento de muestras crudas IQ.

## Módulo 3 — Fuentes de error
Mapea a "Ionosphere Impact".
- Ionosfera y su corrección.
- Troposfera, multipath, errores de reloj.
- Corrección ionosférica con doble frecuencia (L1/L5, E1/E5).

## Módulo 4 — Órbitas y tiempo
Mapea a "Orbits Estimation & Clocks Synchro".
- Cálculo y propagación de órbita.
- Determinación precisa de órbita (POD).
- Sincronización de relojes.
- Sistemas de tiempo (GST, UTC, GPS time) y de referencia (ECEF, marcos).

## Módulo 5 — Integridad
Mapea a "Reliability & Integrity".
- RAIM / ARAIM.
- Protection levels, alert limits.
- Detección de fallos por consistencia.

## Módulo 6 — Seguridad y autenticación de señal
Mapea a "Safety & Authentication".
- OSNMA: autenticación del mensaje de navegación de Galileo.
- Primitivas criptográficas: TESLA (cadena de claves con revelación temporal),
  Merkle (prueba de inclusión), ECDSA (firma del KROOT).
- Cadena de confianza: raíz de Merkle -> clave pública -> KROOT -> claves TESLA
  -> tags -> efemérides autenticadas.
- Relevo entre cadenas (Chain ID).
- Análisis de logs de autenticación.
- Amenazas: spoofing y jamming.

## Temas de frontera
- LEO-PNT, navegación lunar (Moonlight, LunaNet), POD lunar.
- Fusión de sensores (GNSS + IMU + altímetro).
