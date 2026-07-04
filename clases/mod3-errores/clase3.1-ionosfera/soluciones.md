# Soluciones — Clase 3.1

## Ejercicios a mano

**E1.** En L1: Δρ = 40.3·TEC/f² = 40.3 × 30×10¹⁶ / (1575.42×10⁶)² ≈
**4.87 m** (equivale a 30 × 0.162 m/TECU). En L5:
40.3 × 30×10¹⁶ / (1176.45×10⁶)² ≈ **8.73 m**. El cociente es
(f₁/f₅)² = (1575.42/1176.45)² ≈ **1.79**: la frecuencia más baja sufre
más porque el efecto va como 1/f². Esa dependencia conocida y exacta es
justo lo que explota la combinación iono-free (3.2).

**E2.** 5 ns × c ≈ **1.5 m** de retardo en cada pseudorango. El matiz
importante: la parte **común** a todos los satélites la absorbe el sesgo
de reloj del receptor (la 5ª incógnita), así que no va entera a la
posición. Lo que daña es la parte **diferencial** — cada satélite tiene
distinta F por su elevación — que con PDOP ~2 mete del orden de **1–3 m**,
concentrado en la vertical (los satélites bajos, más afectados, son los
que dan la geometría vertical).

**E3.** F(0°) = 1 + 16·(0.53)³ = 1 + 16 × 0.1489 ≈ **3.38**. Pero a
elevación rasante el modelo de cascarón delgado a 350 km es una
caricatura: el rayo real atraviesa cientos de km de ionosfera con
estructura horizontal, el multipath explota, la troposfera también se
amplifica (~10× a 5°, clase 3.3) y la señal puede difractarse. Por eso
la máscara de elevación (5–10°) descarta esos satélites en vez de
confiar en que F los corrija.

## Fermi

**F1.** El residual de Klobuchar escala aproximadamente con el TEC: si hoy
es ~1 m, en el máximo solar esperá **~3 m**. En una G5 el TEC puede ×5–10
con gradientes espaciales que el coseno global no representa: residuales
de **>10 m**, y localmente el modelo puede hasta *empeorar* la medición
(corrige con el signo de la climatología, no del evento). Es la cola que
motivó los SBAS y, para aplicaciones críticas, la doble frecuencia.

**F2.** La Plata (magnética ~−25°) está en el borde de la **anomalía
ecuatorial** (±20°), la región con mayor TEC del planeta y burbujas de
plasma al anochecer; además Sudamérica carga con la anomalía magnética
del Atlántico Sur. Europa a +45° magnéticos vive una ionosfera mucho más
mansa. Conclusión: **a los usuarios sudamericanos** les rinde más
NeQuick-G — el MODIP y el perfil 3D capturan la estructura ecuatorial que
el coseno de Klobuchar aplana. No es casual que la validación de
NeQuick-G le preste atención especial a Brasil/Argentina.

**F3.** Klobuchar: 8 números renovados ~a diario ≈ 10⁻⁴ números/s.
SBAS: ~200 puntos de grilla cada ~5 min ≈ 0.7 números/s. Cociente:
**~10⁴ más ancho de banda de corrección** — y por eso sube de ~50% a
~85% en la tabla de defensas. La precisión de la corrección iono es, en
el fondo, cuánta información fresca te llega sobre el estado del plasma.

## Conceptuales

**C1.** La ionosfera es **plasma** (electrones libres): su índice de
refracción depende de la frecuencia → dispersiva → dos frecuencias miden
dos retardos distintos y permiten despejar el TEC (iono-free). La
troposfera es **gas neutro**: en banda L su retardo es el mismo a
cualquier frecuencia → NO se puede eliminar con doble frecuencia → hay
que **modelarla** (Saastamoinen, clase 3.3). Misma atmósfera, física
opuesta, estrategias opuestas.

**C2.** Por la **inercia de la ionización**: la producción fotoquímica
máxima es al mediodía, pero la densidad integrada sigue subiendo mientras
la producción supere la recombinación — el equilibrio se alcanza ~2 horas
después. Es el mismo motivo por el que la hora más calurosa del día es
~15:00 y no las 12:00.

**C3.** El IPP (punto de perforación) es donde tu rayo cruza el cascarón
a 350 km que concentra el TEC. La ionosfera que atravesás es la de **ese
punto** — que para un satélite a 15° de elevación puede estar a más de
1000 km de tu receptor, con otra hora local y otra latitud geomagnética.
Evaluar el modelo en tu posición sería corregir con la ionosfera
equivocada.

**C4.** La combinación **código menos fase** (code-minus-carrier):
P − Φ = 2·I + multipath + ruido + const. El retardo iono aparece
**duplicado** (el código se retrasa +I, la fase se adelanta −I) y la
geometría/reloj/tropo se cancelan (idénticos en ambos). Con la
ambigüedad de fase constante entre saltos de ciclo, la variación de P−Φ
traza la evolución del TEC oblicuo — y su parte de alta frecuencia es el
multipath: la base de MP1/MP2 en la 3.4.

**C5.** Vería residuales iono **anómalos**: cercanos a cero (el spoofer
no simuló retardo), con el signo o la estructura horaria equivocada, o
inconsistentes entre satélites (todos idénticos cuando deberían variar
con la elevación). Pero **no es robusto solo**: un spoofer cuidadoso puede
inyectar retardos plausibles por satélite, y una tormenta real produce
residuales enormes legítimos (falsos positivos). Sirve como una capa más
de un detector multi-observable — junto con C/N0, simetría del pico
(2.3), consistencia con inercial y, de raíz, OSNMA (módulo 4).

## Mini-simulacro

1. Δρ_código = +40.3·TEC/f²; la fase, mismo módulo y **signo opuesto**.
2. Pico a las **14:00 hora local** del IPP; piso nocturno **5 ns ≈ 1.5 m**.
3. F(5°) ≈ 3.0: un satélite a 5° de elevación acumula el triple del TEC
   vertical porque su rayo atraviesa el cascarón casi de costado.
4. Klobuchar: 8 coef, coseno diurno en el IPP, ~50% RMS. NeQuick-G: 3
   coef + grilla MODIP, perfil 3D de densidad integrado por el rayo, ~70%.
5. **Falso, con tres matices**: (a) la combinación amplifica el ruido ~×3
   (3.2); (b) queda el efecto de 2º orden (~cm, importa en PPP); (c)
   necesitás dos frecuencias visibles y sanas — en jamming selectivo o
   receptores baratos no las tenés.
