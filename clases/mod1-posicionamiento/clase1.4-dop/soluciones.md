# Clase 1.4 — Soluciones

> Abrir después de intentar. El valor está en el intento, no en la respuesta.

## Blancos del README (§4.3)

- **B1:** el DOP depende de la **geometría** de los satélites y no del **ruido/error** de medición.
- **B2:** error esperado ≈ **DOP** × **σ_UERE**.
- **B3:** líneas de vista casi **coplanares** → $G^\top G$ casi **singular** (DOP → ∞).

## E1 — La inversa 3×3 a mano

**a)** Con las columnas $c_1 = (-0.6, 0.8, 0)$, $c_2 = (-0.8, -0.6, 1)$, $c_3 = (1,1,1)$:

$$G^\top G = \begin{pmatrix} 1 & 0 & 0.2 \\ 0 & 2 & -0.4 \\ 0.2 & -0.4 & 3 \end{pmatrix}$$

(diagonal: $\lVert c_1\rVert^2 = 1$, $\lVert c_2\rVert^2 = 2$, $\lVert c_3\rVert^2 = 3$; los cruces son productos punto).

**b)** De la clase 1.2 sabés que $\det(G) = 2.4$; entonces

$$\det(G^\top G) = \det(G)^2 = 5.76$$

(verificalo expandiendo si querés: $1\cdot(6-0.16) - 0 + 0.2\cdot(0-0.4) = 5.84 - 0.08 = 5.76$ ✓).

**c)** Diagonal de la inversa por cofactores ($Q_{ii} = M_{ii}/\det$, con $M_{ii}$ el menor):

$$Q_{11} = \frac{2\cdot 3 - 0.16}{5.76} = \frac{5.84}{5.76} \approx 1.0139, \quad Q_{22} = \frac{3 - 0.04}{5.76} \approx 0.5139, \quad Q_{33} = \frac{2}{5.76} \approx 0.3472$$

$$\text{"GDOP"} = \sqrt{1.875} \approx 1.369, \quad \text{"PDOP"}_{2D} = \sqrt{1.528} \approx 1.236, \quad \text{TDOP} = \sqrt{0.347} \approx 0.589$$

La solución del lab verifica estos números numéricamente al final de su corrida — cotejá contra esa salida.

## E2 — La identidad

$$\text{GDOP}^2 = \mathrm{tr}(Q) = \underbrace{Q_{11}+Q_{22}+Q_{33}}_{\text{PDOP}^2} + \underbrace{Q_{44}}_{\text{TDOP}^2}$$

La traza es una suma: se parte donde uno quiera. Y sí: **HDOP² + VDOP² = PDOP²**, porque la traza del bloque de posición es invariante ante la rotación a ENU ($\mathrm{tr}(RQR^\top) = \mathrm{tr}(Q)$ para $R$ ortogonal), y en ENU esa traza se parte en $(Q_{ee}+Q_{nn}) + Q_{uu}$.

## E3 — Presupuesto de error

$$\text{error horizontal } 1\sigma \approx \text{HDOP} \times \sigma = 1.2 \times 5 = 6\ \text{m}$$

Regla práctica del 95%: ≈ 2 × 6 = **12 m**. (La regla exacta depende de la forma de la elipse; 2× es el número de bolsillo para reportes.)

## Fermi

**F1.** GPS solo: de ~31 operativos, la mitad está del otro lado del planeta y algunos quedan bajo el horizonte local → **~8–12 visibles** a cielo abierto. Con las cuatro constelaciones (~120 satélites utilizables): **~25–35**. Por eso el HDOP multi-GNSS a cielo abierto baja de ~1 a ~0.6.

**F2.** Los satélites están todos en el hemisferio superior. En horizontal, las líneas de vista llegan "de todos lados" y los errores se compensan; en vertical, todas las mediciones empujan desde arriba y no hay ninguna restricción desde abajo: la componente vertical queda menos observada. Resultado típico: VDOP ≈ 1.5–2 × HDOP (en el lab: 1.46).

**F3.** Si los 4 están pegados al cénit, sus vectores unitarios son casi iguales → las tres primeras columnas de cada fila de $G$ son casi las mismas → filas casi linealmente dependientes → $G^\top G$ casi singular → **DOP → ∞**. Además el LOS casi vertical no aporta nada de información horizontal. Es el peor subconjunto del lab (GDOP ≈ 1204) llevado al extremo.

## Mini-simulacro

1. GDOP = $\sqrt{\mathrm{tr}(Q)}$ (todo), PDOP = posición 3D, TDOP = reloj; **GDOP² = PDOP² + TDOP²**.
2. Porque los satélites solo están sobre el horizonte: la vertical se observa desde un solo semiespacio, sin líneas de vista que "sostengan desde abajo".
3. RMS 3D ≈ PDOP × σ = 2 × 4 = **8 m**.
4. **Falso.** Descarta mediciones ruidosas (baja σ) pero degrada la geometría (sube DOP): en el lab, máscara 10°→45° lleva el PDOP de 1.56 a 7.83. Se decide mirando el producto DOP × σ.
5. Que **predice el error real**: con σ = 1 m y PDOP = 1.558, el RMS 3D empírico de 300 corridas fue 1.56 m — cociente 1.00.

## Caso real — cañón urbano

**¿Dirección del peor error?** Perpendicular a la calle (*cross-street*): los satélites visibles quedan alineados con el eje de la calle, así que hay buena observabilidad a lo largo y pésima a lo cruzado — la elipse de error es una aguja perpendicular a la franja de cielo visible. Por eso el receptor "te cruza de vereda" o te pone en la paralela.

**¿Más satélites de la misma constelación o multi-GNSS?** Multi-GNSS. El problema no es la cantidad sino que todos caen en la misma franja de cielo; más constelaciones aumentan la densidad de líneas de vista *dentro de esa franja disponible* y mejoran el condicionamiento de $G^\top G$ mucho más rápido que esperar a que pase otro satélite de la misma constelación.

**¿Qué alerta operativa da un DOP que salta de golpe?** Que la solución dejó de ser confiable *aunque el receptor siga entregando posición*: menos satélites, geometría degenerada, o mediciones excluidas. En clave del módulo 6: si el DOP y los residuos cambian de forma abrupta sin causa ambiental (no entraste a un túnel), es exactamente el tipo de anomalía que un monitor anti-spoofing debe levantar — un spoofer que captura de a poco los canales altera la consistencia geométrica antes de dominar la solución.
