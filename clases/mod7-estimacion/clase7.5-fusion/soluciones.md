# Soluciones — Clase 7.5 (fusión GNSS+INS)

Referencia: seed 42, corte 50–80 s. Determinista: reproducible exacto.

## Lab

| Métrica | Referencia |
|---|---|
| RMS GNSS solo | 4.41 m |
| RMS INS solo | 117.90 m |
| RMS fusión KF | 3.70 m |
| Máx en corte — INS | 117.82 m |
| Máx en corte — KF | 10.16 m |

**TODO 1 (matrices):** F velocidad constante
`[[1,0,DT,0],[0,1,0,DT],[0,0,1,0],[0,0,0,1]]`; B entrada de aceleración
`[[½DT²,0],[0,½DT²],[DT,0],[0,DT]]`.

**TODO 2 (ciclo):** predicción `x=F@x+B@am; P=F@P@F.T+Q`. Corrección (si hay
GNSS) `S=H@P@H.T+R; K=P@H.T@inv(S); x+=K@(z-H@x); P=(I-K@H)@P`. Durante el
corte, `gnss[k] is None` → solo predicción.

## E1 — deriva por sesgo

$\tfrac12 \cdot 0.02 \cdot 30^2 = 0.5\cdot0.02\cdot900 = 9$ m por
componente **solo** por el sesgo. Sumado a la deriva de velocidad
acumulada previa (el sesgo ya venía integrándose desde t=0, no solo en el
corte) y a las dos componentes, se llega a los ~118 m del lab. La lección:
la deriva no arranca en el corte, se **revela** ahí (el GNSS ya no la tapa).

## E2 — GNSS a 10 Hz

Aun con GNSS a la tasa del IMU, el INS seguiría sirviendo para: (1) los
**cortes** (túneles, jamming) que ninguna tasa evita; (2) suavizar el
ruido entre fixes; (3) dar **actitud** (orientación) que el GNSS de una
antena no mide. La fusión no es solo "más muestras".

## E3 — corte de 5 minutos

La deriva del INS crece con $t^2$: a 5 min (10× el corte del lab) el error
sería ~100× mayor → cientos de metros a km con IMU de consumo. La fusión
loosely-coupled no puede evitarlo: sin GNSS, el KF solo predice y hereda la
deriva. Mitigaciones: IMU de mejor grado, tightly-coupling (aprovecha 1–3
satélites que aún se vean), u otros sensores (odometría, mapa).

## F1 — túnel

2 km a 80 km/h (22.2 m/s) = **90 s**. Un INS de grado automóvil deriva
metros en ese tiempo: sale "en el carril correcto" pero no exacto — por eso
el auto-navegador usa además la velocidad de las ruedas (odometría) para
frenar la deriva.

## F2 — predicciones por corrección

IMU 10 Hz / GNSS 1 Hz = **10 predicciones por cada corrección**. Esas 9
predicciones intermedias son movimiento real que el GNSS no ve: el INS
llena el hueco entre fixes (y todo el hueco, si hay corte).

## Mini-simulacro

1. GNSS: absoluto/acotado/con cortes; INS: continuo/alta tasa/deriva. 2.
solo predice con el IMU. 3. loosely usa la posición GNSS; tightly, las
pseudodistancias (<4 sats). 4. integra dos veces el sesgo/ruido de
aceleración → crece con t². 5. Q grande → cree al GNSS; R grande → cree al
INS.
