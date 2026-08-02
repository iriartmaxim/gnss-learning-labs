# Soluciones — Clase 3.5 (iono nivel sistema)

Reusa la iono medida de 3.2. Referencia: día 166, 12:00–12:30, LPGS.

## Lab

| Métrica | Referencia |
|---|---|
| Muestras VTEC (sat altos) | ~415 |
| VTEC mediana | ~12 TECU |
| Retardo vertical L1 | ~2.0 m |

**TODO 1:** `stec = I1/(40.3/F1**2)/1e16 ; return stec*oblicuidad(el)`. El
factor 40.3/f² convierte TEC↔retardo; la oblicuidad proyecta el rayo
inclinado a la vertical.

## E1 — por qué solo satélites altos

A baja elevación el rayo atraviesa más ionosfera (más ruido en la
oblicuidad) y sufre más multipath (3.4). Filtrar a >20° da un VTEC más
limpio. Es el mismo criterio de máscara del PVT.

## E2 — de VTEC a mapa TEC

Cada satélite da un VTEC en SU punto ionosférico (IPP, donde el rayo cruza
la capa a ~350 km). Con muchos receptores y satélites, esos VTEC dispersos
se **interpolan** en una grilla (mapa TEC global tipo IGS, o regional tipo
SBAS). Esa es la estimación a nivel sistema; el path te deja en la semilla.

## E3 — por qué SBAS necesita el mapa

SBAS transmite correcciones ionosféricas en una grilla para receptores
**monofrecuencia** (que no pueden medir la iono ellos mismos, 3.1). El mapa
TEC es cómo el sistema "les presta" la medición de doble frecuencia.

## Mini-simulacro

1. STEC=I1/(40.3/f²); VTEC=STEC·oblicuidad. 2. el IPP (~350 km). 3. porque
a baja elevación hay más ruido/multipath. 4. interpolar VTEC de muchos
IPP en una grilla. 5. para corregir a receptores monofrecuencia (SBAS).
