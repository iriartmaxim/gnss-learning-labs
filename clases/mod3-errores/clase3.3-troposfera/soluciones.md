# Soluciones — Clase 3.3

## Ejercicios a mano

**E1.** ZHD(990) ≈ 2.256 m y ZHD(1030) ≈ 2.347 m: **9.1 cm** de
diferencia = 40 hPa × 2.28 mm/hPa. No hace falta un barómetro de
precisión: con ±1 hPa (cualquier sensor barato, o la presión de un
modelo meteorológico) el ZHD queda a ~2 mm. La lección: cuando la física
te regala una relación exacta (hidrostática), la exactitud del modelo la
hereda la exactitud del *dato de entrada* — y acá el dato es baratísimo.

**E2.** Capa plano-paralela de espesor H: el rayo con elevación *el*
recorre L = H/sin(el) dentro de la capa, y el retardo es proporcional al
camino ⇒ m(el) = 1/sin(el). Lo rompen debajo de ~10°: (1) la
**curvatura terrestre** — la capa se curva con la Tierra y el camino
real crece menos que 1/sin (que diverge a el→0; el valor real a 0° es
~38, no ∞); (2) la **refracción** — el rayo se curva hacia abajo
(bending), alarga el camino y hace que la elevación aparente difiera de
la geométrica. Las funciones de Niell/GMF/VMF parametrizan ambas cosas.

**E3.** PWV ≈ 0.15 × 88 mm ≈ **13 mm** hoy: si todo el vapor de tu
columna condensara de golpe, caerían 13 mm de lluvia. En la tarde
tropical: 0.15 × 400 = **60 mm** — una columna cargadísima (y un ZWD
que ya no es el 4% sino el 15% del retardo total). El mismo número que
para vos es error, para el meteorólogo es el estado del cielo.

## Fermi

**F1.** ±20 hPa ⇒ ±4.6 cm de ZHD cenital; con mapeo típico ~1.5–2 y la
parte que no absorbe el reloj, del orden de **±5–8 cm en la vertical**.
Contra un fix de código iono-free con U RMS = 1.42 m: irrelevante — ISA
alcanza. Con fase/PPP (nivel cm) la cuenta cambia: ahí se usa presión
real (sensor o modelo meteo), que baja el error a mm. El sensor se
justifica según la liga en la que jugás.

**F2.** 5 hPa ⇒ ΔZHD ≈ 11 mm de diferencia cenital entre estación y
avión. A 5° de elevación: ×11.5 ≈ **13 cm diferenciales** que el GBAS no
puede corregir (su hipótesis es "misma atmósfera"). En un presupuesto de
integridad CAT-I donde los límites de alerta son de pocos metros y cada
término se audita en centímetros, un frente puede comerse una fracción
visible del presupuesto — por eso "anomalous troposphere" tiene su σ y
sus monitores dedicados en el threat model.

**F3.** ~100 estaciones sobre ~2.8 M km² ⇒ una cada ~170 km, cada
15 min. Los radiosondeos: ~10 sitios, cada 12 h. El "radar de vapor"
GNSS gana ~×20 en resolución espacial y ~×50 en temporal, funciona
nublado y de noche, y el costo marginal es cero (las estaciones ya
existen para geodesia). Por eso E-GVAP y GEONET asimilan PWV
operativamente — y por eso tu estación LPGS es también un instrumento
meteorológico.

## Conceptuales

**C1.** La ionosfera es **plasma**: electrones libres cuyo índice de
refracción depende de la frecuencia (dispersión ∝ 1/f²) — dos
frecuencias miden dos retardos distintos y permiten despejarlo. La
troposfera es **gas neutro**: la polarizabilidad molecular tiene sus
resonancias en el infrarrojo y el óptico, lejísimos de banda L, así que
n es constante en todas las señales GNSS — ninguna combinación la
toca. Checkpoint del módulo cerrado: dispersiva ⇒ se mide y elimina;
no dispersiva ⇒ se modela.

**C2.** Por el **equilibrio hidrostático**: dP/dz = −ρg ⇒
∫ρ dz = P₀/g, *exacto e independiente de cómo se distribuya la densidad
en la vertical*. Como el retardo seco es proporcional a esa integral,
medir P en superficie lo determina a ~1 mm. El vapor de agua no cumple
su propia hidrostática (se evapora, condensa y lo transporta el viento):
su integral vertical NO se deduce de e y T en superficie — la fórmula
del ZWD es una regresión climatológica con ~1–4 cm de error. Seco =
física; húmedo = estadística.

**C3.** PPP agrega el **ZWD residual como incógnita** del filtro, con
firma m_w(el) en cada observación. Es separable de la altura porque
m(el) crece hacia el horizonte mientras la proyección vertical
(sin(el)) crece hacia el cenit — firmas opuestas en elevación. Pero la
correlación con la vertical y el reloj sigue siendo alta: es el trío
correlacionado clásico (U, ZWD, dt_rx), y por eso la vertical de PPP
converge lento y los satélites bajos (bien pesados) ayudan a separarlo.
Costo: tiempo de convergencia; premio: el ZWD estimado es el PWV del
caso real.

**C4.** Los +10 cm cenitales se reparten: la parte del patrón m(el) que
se parece a "un poco para todos" la absorbe el **reloj del receptor**, y
lo que se proyecta a U (~5–10 cm) queda **enterrado bajo el ruido** del
código iono-free (U RMS 1.42 m, dominado por el ×2.59 de la 3.2).
Dejaría de ser empate: con observables de fase (σ ~ mm), con código
suavizado (Hatch), o en verano húmedo donde el ZWD ×4 convierte la
diferencia en ~35 cm.

**C5.** La tropo **no viaja en la señal**: el receptor la calcula solo,
con datos locales — el spoofer ni la controla ni necesita falsificarla
(a diferencia de efemérides y relojes del mensaje, que OSNMA protege en
el módulo 4). No es canal de ataque directo; el vector exótico sería
envenenar los datos meteo externos (modelos que alimentan VMF) en
sistemas que los ingieren — cadena de suministro de datos, no RF. En
GBAS el observable que sí preocupa es el **gradiente tropo anómalo**
estación–avión (frentes, inversiones, ductos): rompe la hipótesis
diferencial y por eso vive en el threat model con σ propia.

## Mini-simulacro

1. ZHD = 0.0022768·P/(1 − 0.00266·cos2φ − 0.00028·h_km): la columna de
   aire seco (hidrostática). ZWD = 0.002277·(1255/T + 0.05)·e: el vapor.
2. Porque ∫ρdz = P/g es exacto (equilibrio hidrostático): P en
   superficie determina la masa de la columna entera, se distribuya como
   se distribuya.
3. m(5°) = 11.47 vs F_iono(5°) = 3.03: la tropo está pegada al suelo y
   el rayo rasante la atraviesa casi horizontal; la iono, a 350 km, se
   salva por la curvatura terrestre.
4. La tropo valía ~5 m de vertical (6.65 → 1.42, ×4.7). El salto
   mínimo→Saastamoinen fue +2 cm (empate): el residuo de ~10 cm queda
   bajo el ruido del código y en parte lo come el reloj.
5. **Falso**: el ZHD se modela con presión (mm) y el ZWD residual se
   *estima* como incógnita — no se elimina: se convierte en producto
   (PWV para meteorología). Eliminar es privilegio de lo dispersivo.
