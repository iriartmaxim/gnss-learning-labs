# Soluciones — Clase 4.2 (broadcast vs SP3, RTN)

Referencia: día 166, 10:00–14:00, dentro del arco de validez. Los produce el lab.

## Lab

| Componente | Galileo | GPS |
|---|---|---|
| Radial | 0.82 m | 1.43 m |
| Along | 0.28 m | 1.27 m |
| Cross | 0.20 m | 0.66 m |
| 3D | 0.89 m | 2.03 m |

**TODO 1 (RTN):** `R=r/|r|`, `Cross=(r×v)/|r×v|`, `Along=Cross×R`; devolvé
`[dpos·R, dpos·Along, dpos·Cross]`.

**TODO 2 (diferencia):** `difs.append(rtn(xb - xp, xb, vb))` con `xb`
broadcast, `xp` SP3 en metros, `vb` velocidad broadcast por diferencia
finita.

## E1 — proyección al rango

En el cénit la línea de vista es casi radial: el error radial de 1 m entra
casi entero (~1 m), el along-track de 3 m casi nada (~0). A baja elevación
la geometría cambia y el along/cross empiezan a proyectarse algo, pero la
radial sigue siendo la que más pesa. Ese es el argumento del SISRE.

## E2 — along-track chico acá

Porque evaluamos **dentro del arco de validez** (±1 h de Toe): la
efeméride está ajustada para ese intervalo. El envejecimiento de 4.1 (569 m
a 12 h) aparece al **extrapolar** fuera del arco, donde el along-track
explota. Acá, en cambio, along-track es de dm.

## E3 — el SP3 como verdad

Es una estimación, pero ~100× mejor que la broadcast (cm vs m) y calculada
con una red global y días de datos. Para juzgar la broadcast (metros), el
SP3 (cm) es "verdad" a efectos prácticos: el error de referencia es
despreciable frente a lo que medimos.

## F1 — aporte de la órbita al PVT

Radial ~0.8 m por satélite, parcialmente promediada por la geometría →
aporta del orden de ~0.5–1 m al error de posición. Consistente con que el
PVT completo (1.5) daba ~1.8 m: la órbita es una parte, el resto es
reloj/tropo/ruido.

## F2 — avance entre épocas SP3

3.7 km/s × 300 s = **1110 km** entre épocas de 5 min. En ese tramo la
órbita curva notablemente → interpolar linealmente daría error de metros a
km. Lagrange de ~10 nodos captura la curvatura a nivel cm.

## Mini-simulacro

1. R=r/|r|, C=(r×v)/|r×v|, A=C×R. 2. la radial (el rango es casi su
proyección). 3. SP3 ~cm/~2 sem; broadcast ~1–2 m/instantáneo. 4. porque el
movimiento entre épocas de 5 min es muy no lineal. 5. Galileo ~0.9 m mejor
que GPS ~2 m.
