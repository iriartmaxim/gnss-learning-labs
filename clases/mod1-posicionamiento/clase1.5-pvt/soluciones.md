# Soluciones — Clase 1.5

## Ejercicios a mano

**E1.** −64 251.5 / 299 792 458 = **−214.32 µs**. No contamina la posición
porque es la **cuarta incógnita**: en el jacobiano su columna es de unos
(afecta igual a todos los pseudorangos), así que Gauss-Newton separa
limpiamente el sesgo común (→ reloj) de la parte geométrica (→ posición).
Todo error *común a todos los satélites* cae en ese sumidero.

**E2.** v·τ = 380 m/s × 0.086 s ≈ **32.7 m** — clava con los 32.5 m
medidos. Sagnac es, literalmente, cuánto se movió tu marco de referencia
mientras la señal viajaba.

**E3.** Amplitud máxima = 2√(μA)·e/c.
Galileo (A=2.96e7, e=3.4e-4): 2·1.086e11·3.4e-4/c ≈ **0.25 m**.
GPS (A=2.656e7, e=0.02): 2·1.029e11·0.02/c ≈ **13.7 m**.
Un receptor Galileo-only "podría" ignorarla a nivel 10 m; uno GPS jamás.
(Excepción Galileo: E14/E18 con e≈0.16 → ~120 m — nunca la ignores.)

## Fermi

**F1.** c·1 ms ≈ **300 km/ms**. Con af0(E19) ≈ 3.03 ms → ~908 km del
mismo orden que los 926 km medidos (la geometría no mapea 1:1 el sesgo
por satélite a error 3D, pero el orden es ese).

**F2.** 2.3/sin(14°) ≈ **9.5 m** para E26. La parte común (~2.3–4 m) la
absorbe el reloj del receptor; la parte que crece hacia el horizonte se
proyecta casi toda en la vertical → el U = +8.5 m de la pasada 1.

**F3.** 86 400/30 = 2880 épocas × 8 sats × 2 frecuencias ≈
**46 000 pseudorangos Galileo/día** (~23 000 por frecuencia).

## Conceptuales

**C1.** La ionósfera es un plasma: dispersiva, retardo ∝ 1/f² → dos
frecuencias la despejan algebraicamente. La tropósfera es aire neutro,
no dispersiva en banda L: las dos frecuencias ven lo mismo, así que solo
queda modelarla (o estimarla como incógnita extra).

**C2.** El oscilador del receptor (TCXO) deriva de forma errática a nivel
µs–ms; modelarlo bien costaría más que estimarlo. Como es un sesgo común,
una incógnita por época lo resuelve exacto y gratis.

**C3.** Presupuesto del residuo 1.02 m: órbita+reloj broadcast ~0.9–1 m
(lo que mediste en la 1.3, domina), tropo residual del modelo mínimo
(dm), multipath (dm) y ruido de código ×3 por la iono-free (dm).

**C4.** La componente común de la tropo se va al reloj; la componente
dependiente de la elevación apunta "hacia arriba" para todos los
satélites (todos tienen elevación positiva) → se proyecta en U. En
horizontal, los satélites al este y al oeste se compensan.

**C5.** 8 − 4 = 4 grados de libertad → residuos → estadística: detectar
y excluir un satélite mentiroso (RAIM), pesar por elevación, estimar la
tropo cenital como 5ª incógnita. Es la semilla de la **integridad**
(módulo 6): sin redundancia no hay forma de descubrir un spoofer parcial.

## Mini-simulacro

1. P₁,P₅ → P_IF (iono: exacta) → t_tx = t_rx − P/c (300 m si lo salteás)
   → órbita ICD (1 m) → Sagnac (32 m) → reloj sat (hasta cientos de km)
   → tropo (2–10 m según elevación) → GN 4 incógnitas.
2. **V.** La rotación ω⊕·τ corre al satélite ~ω⊕·τ·r ≈ 180 m en ECEF;
   cuánto de eso entra al rango depende de la componente este-oeste de la
   línea de vista — por eso el efecto neto en el fix (32 m) varía con la
   geometría.
3. γ = 1.7933 → P_IF = (1.7933·25 000 000 − 25 000 003)/0.7933 =
   **24 999 996.22 m**. Iono en E1: I₁ = (P₅−P₁)/(γ−1) = 3/0.7933 =
   **3.78 m** (y P_IF = P₁ − I₁ ✓).
4. Porque el reloj F/NAV está *definido* para el usuario E1/E5a (sin
   BGD). OSNMA firma el contenido I/NAV; un receptor autenticado que
   quiera usar E1/E5a aplica el BGD para trasladar el reloj. En el lab
   separamos los problemas: hoy posicionás; en el módulo 4 autenticás.
