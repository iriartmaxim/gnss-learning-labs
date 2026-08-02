# Soluciones — Clase 8.1 (Future & Trends)

Física orbital (0.3). El lab termina en "OK".

## Lab

| Métrica | MEO (Galileo) | LEO-PNT |
|---|---|---|
| Período | ~14 h | ~1.6 h |
| Velocidad | 3.67 km/s | 7.59 km/s |
| Doppler máx L1 | ±19 kHz | ±40 kHz |
| Ventaja de potencia LEO | — | +33 dB |

**TODO 1:** `2*np.pi*np.sqrt(a**3/MU)` y `np.sqrt(MU/a)`. **TODO 2:**
`20*np.log10(alt_meo/alt_leo)` (al cénit la distancia usuario→satélite es la altitud).

## E1 — por qué LEO converge más rápido el PPP

La geometría cambia rápido (período 1.6 h vs 14 h): los satélites se
mueven mucho en pocos minutos, así que la matriz de geometría se
"refresca" y las ambigüedades/incógnitas se observan antes. El PPP, que en
MEO tarda decenas de minutos en converger, en LEO puede hacerlo en minutos.

## E2 — el costo del hand-over

Un satélite LEO cruza el cielo en minutos (no horas): el receptor tiene
que adquirir y soltar satélites constantemente (hand-over veloz) y seguir
un Doppler ~2× mayor. Y hacen falta MUCHOS más satélites para cobertura
global continua (cientos vs decenas).

## Mini-simulacro

1. más señal (~30 dB), geometría rápida (converge PPP), anti-jamming. 2.
hand-over veloz, más Doppler, muchos satélites. 3. Moonlight/LunaNet:
navegación alrededor de la Luna. 4. la Luna no tiene GNSS: se lleva la
infraestructura. 5. complemento/respaldo del GNSS (resiliencia PNT).
