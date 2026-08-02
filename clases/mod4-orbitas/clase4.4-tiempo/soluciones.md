# Soluciones — Clase 4.4 (escalas de tiempo)

## Lab (timescales.py)

| Chequeo | Referencia |
|---|---|
| ΔAT 2026 | 37 s |
| GPST − UTC | 18 s |
| GPST = TAI − | 19 s |
| 2026-06-15 12:00 UTC | semana 2423, sow 129618 |
| Tests | 8/8 |

**TODO 1:** recorrer `LEAP_TABLE` y quedarse con el último `val` cuya fecha
≤ utc. **TODO 2:** `utc + timedelta(seconds=leap_seconds(utc) - 19)`.
**TODO 3:** `semana = dt.days // 7`, `sow = (dt.days % 7)*86400 + dt.seconds`.

## E1 — conversión

UTC 12:00:00. GPST = UTC + 18 s = **12:00:18**. TAI = UTC + ΔAT = UTC + 37 s
= **12:00:37**. (GPST = TAI − 19 = 12:00:18 ✓.)

## E2 — ignorar el GGTO

Si el receptor asume GST=GPST (GGTO=0) cuando en realidad hay un offset de
ns, inyecta un sesgo común a todas las mediciones Galileo → pequeño error
sistemático. La alternativa correcta: tratar el **sesgo inter-sistema como
una incógnita más** en el PVT (un reloj por constelación). Cuesta un grado
de libertad, lo elimina el error.

## E3 — nuevo leap second

Si ΔAT pasa a 38: **GPST no cambia** (es fija, TAI−19). **UTC** sí (salta 1
s para mantenerse cerca del día solar). **GPST − UTC** pasa de 18 a 19 s. La
escala de trabajo (GPST) es inmune; solo cambia la conversión a UTC.

## F1 — salto de 1 s

1 s × c = **299 792 km** de error de rango. Catastrófico: por eso GPST es
continua. Ninguna escala de posicionamiento puede tener saltos.

## F2 — GGTO en cm

few ns × c: 3 ns ≈ 0.9 m; sub-ns ≈ cm. Para un receptor de código puede ser
despreciable, pero en precisión (PPP/RTK multi-GNSS) conviene estimarlo para
no meter un sesgo sistemático entre constelaciones.

## Mini-simulacro

1. TAI atómica; UTC=TAI−ΔAT con leaps; GPST=TAI−19 fija; GST≈GPST±GGTO. 2.
18 s (ΔAT−19). 3. ajuste de 1 s por la rotación; último 2017. 4. offset ns
GPS↔Galileo; se lee o se estima. 5. ECI dinámica, ECEF usuario.
