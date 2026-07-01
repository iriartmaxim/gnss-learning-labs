# Clase 1.1 — Soluciones

> Abrir después de intentar. El valor está en el intento, no en la respuesta.

## Blancos del README (§4.2)

- **B1:** dos circunferencias se cortan en **2** puntos (si se cortan); la tercera baliza debe ser no **colineal** con las otras dos.
- **B2:** la reflexión respecto del **plano de las balizas**.
- **B3:** falta agregar **el reloj del receptor (c·δt)** como incógnita, porque el receptor no mide distancias sino **tiempos de llegada** (→ pseudodistancias, clase 1.2).

## E1 — Intersección en 2D

Balizas $B_1(0,0)$, $B_2(6,0)$, $B_3(3,9)$; rangos $(5,5,5)$.

**a)** Ecuaciones de las dos primeras circunferencias:

$$x^2 + y^2 = 25 \qquad (x-6)^2 + y^2 = 25$$

Restándolas (el truco estándar: la resta elimina los cuadráticos y deja la **recta radical**):

$$x^2 - (x-6)^2 = 0 \;\Rightarrow\; 12x - 36 = 0 \;\Rightarrow\; x = 3$$

Sustituyendo: $9 + y^2 = 25 \Rightarrow y = \pm 4$. Candidatos: $(3, 4)$ y $(3, -4)$.

**b)** Distancia de cada candidato a $B_3(3,9)$:

$$d\big((3,4),B_3\big) = |9-4| = 5 \;✓ \qquad d\big((3,-4),B_3\big) = |9-(-4)| = 13 \;✗$$

Solución: $\mathbf{(3, 4)}$.

**c)** Las tres balizas deben ser **no colineales**. Si están alineadas, todo el sistema es simétrico respecto de esa recta y la ambigüedad no se puede romper (además $J^\top J$ se vuelve singular).

## E2 — Propagación de un error

Con la baliza Norte a gran distancia, su LOS es $\hat{n}$ (apunta al Norte). Un rango **1 m más largo** dice "estás 1 m más lejos de esa baliza": la solución se corre **1 m hacia el Sur**. El rango Este no cambia, así que no hay corrimiento Este-Oeste.

Moraleja: cada fila de $J$ ($-\mathbf{u}_i^\top$) es exactamente *la dirección sobre la que esa medición empuja la solución*. Los errores de rango se proyectan sobre la línea de vista — por eso la geometría (cómo se reparten esas direcciones) decide cuánto se amplifica el ruido.

## E3 — Tiempo ↔ distancia

$$\Delta d = c\,\Delta t \;\Rightarrow\; \Delta t = \frac{1\ \text{m}}{3\times10^8\ \text{m/s}} \approx 3.3\ \text{ns}$$

Para 1 cm: **~33 ps**. Ningún reloj barato sostiene eso — por eso el receptor GNSS no intenta tener razón en el tiempo: **estima su propio error de reloj como incógnita** (clase 1.2), y por eso los satélites llevan relojes atómicos.

## Fermi

**F1.** Sonido: $\Delta t = 1/343 \approx 2.9$ ms — lo mide cualquier microcontrolador. Luz: $\approx 3.3$ ns. Separación: **~6 órdenes de magnitud**. Todo el hardware exótico de GNSS (relojes atómicos, correladores) existe por esos 6 órdenes.

**F2.** $d \approx 343 \times 6 \approx 2.1$ km (la luz del relámpago llega "instantánea": 2 km en ~7 µs). Es ranging por tiempo de vuelo con tu oreja como receptor.

**F3.** $100\ \text{ns} \times c = 30$ m de error por rango; con geometría razonable (factor ~1.5–3), **decenas de metros** de error de posición — exactamente el orden del posicionamiento celular por tiempo (OTDOA/E-CID).

## Mini-simulacro

1. **Trilateración**: posición por *distancias* a puntos conocidos. **Triangulación**: por *ángulos*. GNSS usa la primera (mide tiempos → distancias; jamás ángulos).
2. **4 esferas.** Con 3 quedan 2 puntos (espejo respecto del plano de balizas); la 4ª, no coplanar, desambigua.
3. **Falso.** Duplicar mediciones en el mismo cono reduce el ruido ~$1/\sqrt{n}$, pero la amplificación geométrica ($\sqrt{\mathrm{tr}((J^\top J)^{-1})}$) sigue casi igual: en el lab, la geometría mala amplifica ×6.8 y eso no se compra con más balizas iguales.
4. **Hacia el Este**, ~2 m: el rango más largo empuja la solución *alejándola* de la baliza, a lo largo de su LOS.
5. **El sesgo de reloj del receptor** ($c\,\delta t$): el receptor mide tiempos con un reloj de cuarzo que miente, así que cada "distancia" viene contaminada por un mismo desconocido común — se agrega como 4ª incógnita (clase 1.2).

## Caso real — eLoran

**¿Por qué resiste el jamming?** Potencia recibida. La señal GNSS llega con ~10⁻¹⁶ W (está 20 000 km arriba y el transmisor emite cientos de watts); eLoran transmite **cientos de kilowatts a cientos de km**, en 100 kHz (propagación por onda de superficie). La señal llega del orden de **un millón de veces más fuerte**: para taparla hace falta un jammer enorme, visible y fácil de localizar — el atacante pierde la asimetría que lo favorece contra GNSS.

**¿Qué sacrifica?** Precisión (~10–20 m vs. metros), cobertura (regional, requiere infraestructura terrestre), y no da altura útil.

**Arquitectura multicapa:** GNSS (precisión global) + eLoran (backup robusto regional) + relojes de holdover (el timing sobrevive sin señal) + INS (puente inercial de corto plazo). Ninguna capa es perfecta; el diseño asume que cada una puede caer.

**Traducción a infraestructura crítica:** es defensa en profundidad aplicada a PNT — como no depender de un único IdP para autenticación: fuentes de tiempo redundantes y *tecnológicamente diversas* (que no compartan modo de falla), monitoreo cruzado entre capas (detectar cuando GNSS y eLoran discrepan ≈ detectar spoofing), y degradación controlada en vez de caída total.
