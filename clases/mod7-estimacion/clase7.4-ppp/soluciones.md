# Soluciones — Clase 7.4 (PPP-lite)

Referencia: día 166, 12:00–13:00, LPGS, iono-free. Los produce el lab.

## Lab

| Métrica | Referencia |
|---|---|
| Épocas | 121 |
| RMS 3D ZWD=0 | 1.88 m |
| ZWD óptimo (batch) | 14 cm |
| RMS 3D ZWD óptimo | 1.83 m |
| Broadcast (1.5) | ~1.95 m |

**TODO 1 (reloj preciso):** `clk_interp(*clk[s], t_tx) + dt_relativista(sp3, s, t_tx)`.
El segundo término es −2(r·v)/c², que los CLK no incluyen. Sin él el RMS
salta a ~11 m (lo verificás quitándolo).

**TODO 2 (PVT):** `pred = rho + x[3] − C*dt_sat + zhd + zwd*m_wet`; fila del
jacobiano `[(x−xyz)/rho , 1]` (los tres cosenos directores + el 1 del
reloj). El ZWD entra como término conocido (no incógnita en esta versión).

## E1 — ZWD mapeado

ZWD=14 cm cenital. A 30°: 0.14/sin(30°)=0.14/0.5=**28 cm**. A 10°:
0.14/sin(10°)=0.14/0.1736≈**81 cm**. La baja elevación amplifica: por eso
el ZWD se ve mejor con satélites bajos (pero ahí también pega el
multipath, 3.4 — trade-off).

## E2 — por qué no baja de 1.8 m

Porque con órbita/reloj ya perfectos, el error dominante pasa a ser el
**ruido y multipath del código** (~0.3 m por medición, amplificado por
geometría). Mejorar la órbita de 1.5 m a 3 cm saca un término que ya no
era el cuello de botella. El código tiene techo en el metro.

## E3 — relatividad GPS vs Galileo

La amplitud es $2\sqrt{\mu a}\,e/c^2$. Galileo tiene e≈3.4e-4 → ~8 cm. GPS
tiene e≈0.01 (30× mayor) → ~metros. Misma física, distinta excentricidad
(clase 0.3): por eso en GPS la relatividad es un término de primer orden.

## F1 — RMS por ruido solo

0.3 m × factor geométrico (~PDOP 2–3) ≈ **0.6–0.9 m** por ruido. El resto
hasta 1.83 m es multipath y residuos de tropo/modelo. Consistente con que
el código no baja del metro.

## F2 — la fase

2 mm vs 300 mm → **~150× menos ruido**. No es gratis porque la fase mide
ciclos con una **ambigüedad entera** desconocida por satélite: hay que
resolverla (RTK) o dejar que converja (PPP), y eso lleva tiempo y cuidado
con los saltos de ciclo.

## Mini-simulacro

1. SP3 órbita ~cm cada 5 min; CLK reloj ~0.1 ns cada 30 s. 2. la
relativista periódica −2(r·v)/c², con la velocidad del SP3. 3. por época
es inobservable (correlado con reloj/vertical) → batch. 4. porque domina
el ruido/multipath del código, no la órbita/reloj. 5. PPP: global sin
base, lento; DGNSS: base cercana, código; RTK: fase+ambigüedades, cm.
