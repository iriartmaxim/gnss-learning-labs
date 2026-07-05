# Soluciones — Clase 3.2

## Ejercicios a mano

**E1.** γ₁₂ = (1575.42/1227.60)² = **1.6469**. Coeficientes:
γ/(γ−1) = 2.546 y 1/(γ−1) = 1.546. Amplificación:
√(2.546² + 1.546²) ≈ **2.98** — peor que el 2.59 de E1/E5a. La razón: L1
y L2 están más *cerca* en frecuencia, así que sus ionosferas se parecen
más y separarlas exige coeficientes más grandes (la combinación está
peor condicionada). Regla: cuanto más separadas las frecuencias, más
barata la iono-free — un motivo del diseño de L5/E5a.

**E2.** Igualando errores totales por observable:
b² + σ² = (2.59σ)² ⇒ b = σ·√(2.59² − 1) = **2.39·σ ≈ 0.72 m** con
σ = 0.3 m. Con sesgo residual del modelo por encima de ~0.7 m por
pseudorango, iono-free gana. Matiz honesto: en el *fix* la cuenta se
suaviza porque la parte del sesgo común a todos los satélites se absorbe
en el reloj — por eso en nuestra corrida Klobuchar ganó aun con residual
de 1.27 m en pseudorango.

**E3.** c·BGD = −1.33 m. En E1-only, ignorarlo sesga el pseudorango de
E29 en 1.33 m; como cada satélite tiene SU BGD (valores distintos de
±nanosegundos), la parte diferencial no se absorbe en el reloj y mete
del orden de **1–2 m** en el fix. En iono-free: **cero** — el reloj
F/NAV está referido a la combinación, el BGD desaparece por diseño.
Galileo eligió esa convención justamente para que el usuario de máxima
precisión no cargue con sesgos de hardware.

## Fermi

**F1.** N = 100 épocas ⇒ el ruido baja ×1/√100 = ×0.1:
σ_IF,suavizado ≈ 2.59 × 0.3 / 10 ≈ **0.08 m**. El ×2.59 se vuelve
irrelevante frente a sesgos de metros — por eso el iono-free operativo
(DFMC, receptores geodésicos) SIEMPRE viene con suavizado de fase. El
trade-off sesgo/ruido se resuelve pagando el ruido con tiempo.

**F2.** Tormenta G5, residual Klobuchar ~10 m por pseudorango: E1 crudo
puede irse a **decenas de metros** en vertical (F amplifica a baja
elevación); E1+Klobuchar queda con ~10 m de sesgo → vertical de
10–20 m; iono-free mantiene ~**1.5 m** (solo el ruido ×2.59, que la
tormenta no toca — el 1er orden se cancela exacto). Para el dron de
inspección: doble frecuencia sin discusión. La moraleja de la clase en
una tabla: la cuenta sesgo/ruido se invierte violentamente con la iono
brava.

**F3.** Para 3σ_media < 0.2 m con σ = 1 m: N > (3/0.2)² = **225 épocas**
= 112 min a 30 s. No llegás: un gradiente de tormenta pasa en minutos.
Por eso los monitores de gradiente ionosférico (GBAS/SBAS) usan la
**fase** (σ ~ mm): una época basta. Código para el nivel absoluto, fase
para la dinámica — el reparto de roles que explota la 3.4.

## Conceptuales

**C1.** Porque el servicio de referencia de Galileo OS es de doble
frecuencia: referir el reloj a la combinación E1/E5a hace que el usuario
iono-free no necesite NINGUNA corrección extra, y el costo (aplicar BGD)
lo paguen solo los single-frequency. El usuario E1-only corrige
dt_E1 = dt_IF − BGD, es decir resta c·BGD del pseudorango corregido —
exactamente la línea que completaste en el TODO.

**C2.** Todos los satélites están *arriba* (elevación 10–90°): un
retardo positivo correlacionado con la elevación no puede empujarte
hacia los costados (la simetría azimutal lo cancela en horizontal), pero
sí puede empujarte verticalmente, y su parte común se confunde con el
reloj. Formalmente: la columna U del jacobiano (sin(el)) está casi
alineada con el patrón del retardo iono/tropo (F(el)). Por eso TODO el
módulo 3 golpea la vertical — ya lo viste con la tropo en la cascada de
la 1.5 (8.58 m sin tropo, casi todo en U).

**C3.** Porque el ruido de fase es ~2 mm: 2.59 × 2 mm ≈ 5 mm — nada. El
problema nuevo: cada fase trae una **ambigüedad entera** N por satélite
y arco, y la combinación IF de fase tiene ambigüedad *no entera*
(mezcla de N₁ y N₅ con coeficientes irracionales), lo que complica
fijarla a entero. De ahí las combinaciones wide-lane y compañía — módulo
5. La fase es la reina de la precisión, pero cobra en ambigüedades.

**C4.** Spoofer coherente sin iono real: la divergencia queda ~constante
(solo DCB), sin estructura de elevación ni evolución temporal — anómala
contra cualquier climatología: detectable. Si solo captura E1: P₅ real
menos P₁ falso salta o deriva de forma incoherente — detección aún más
fácil. Por eso la divergencia es un observable de integridad estándar.
Límite: un spoofer sofisticado que modele iono plausible por satélite
sube mucho el costo del ataque pero no es imposible — otra razón para
autenticación criptográfica (OSNMA, módulo 4).

**C5.** El código se retrasa +I y la fase se adelanta −I ⇒
P − Φ = **2I** (+ ambigüedad + multipath). Dos códigos:
P₅ − P₁ = (γ−1)I = **0.79·I**. La código-fase tiene 2.5× más señal por
metro de iono Y menos ruido (una fase casi no aporta ruido frente al
código). Es muy superior para seguir la *variación* del TEC — pero la
ambigüedad desconocida le roba el valor absoluto. Combinación ganadora:
nivel absoluto por divergencia de códigos, dinámica por código−fase.
Exactamente la maquinaria de MP1/MP2 en la 3.4.

## Mini-simulacro

1. P_IF = (γP₁ − P₅)/(γ−1) = 2.261·P₁ − 1.261·P₅. Suman 1 para preservar
   ρ* (geometría + relojes + tropo) sin escalar.
2. El retardo iono oblicuo en E1. Lo contaminan el BGD del satélite
   (transmitido, corregible) y el DCB del receptor (offset común).
3. σ_IF = √(2.261² + 1.261²)·σ_P = 2.59·σ_P.
4. E1+Klobuchar (U = 0.78 vs 1.42 m): a las 8–9 h locales de invierno el
   sesgo residual del modelo es chico y el ×2.59 del iono-free domina.
   Error total = √(sesgo² + ruido²): esa mañana, ganó el modelo.
5. **Falso a medias**: el fix iono-free no lo necesita (el reloj F/NAV ya
   está referido a la combinación), pero cualquier uso single-frequency,
   toda mezcla de observables y el monitoreo de la divergencia sí — y
   "single-frequency" es la mayoría de los receptores del planeta.
