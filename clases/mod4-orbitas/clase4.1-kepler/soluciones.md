# Soluciones — Clase 4.1

## Ejercicios a mano

**E1.** n₀ = √(μ/a³) = √(3.986e14 / (2.96e7)³) = √(3.986e14 / 2.594e22)
= √(1.537e-8) = **1.240e-4 rad/s**. Período T = 2π/n₀ = **50675 s ≈
14 h 04 m**. En un día sidéreo (86164 s): 86164/50675 = **1.70 vueltas**.
Como no es entero, la geometría no se repite al día: hace falta buscar
el ciclo donde SÍ cierra — 17 vueltas en 10 días (17 × 50675 = 861478 s
≈ 10 días sidéreos). Ese es exactamente el ciclo de repetición de 10
días que usaste en la 3.4 para el multipath sideral. Todo cierra.

**E2.** Δn ≈ 2.5e-9 rad/s en 2 h (7200 s): error de anomalía
2.5e-9 × 7200 = **1.8e-5 rad**. Por el radio orbital: 1.8e-5 × 2.96e7 =
**533 m**. Coincide con los 546 m del lab (la pequeña diferencia es que
el error real no es puramente along-track y el Δn de E05 no es
exactamente 2.5e-9). La intuición clave: Δn es un error de *fase*, así
que crece lineal con el tiempo y se proyecta sobre la dirección del
movimiento — por eso domina el residuo lejos de Toe.

**E3.** Ω̇ = −1.5 · n · J2 · (R_T/a)² · cos(i). Con n = 1.24e-4,
J2 = 1.08e-3, R_T/a = 6378/29600 = 0.2155, cos(56°) = 0.559:
Ω̇ = −1.5 × 1.24e-4 × 1.08e-3 × 0.0464 × 0.559 = **−5.2e-9 rad/s**.
Compará con el OmegaDot del mensaje (típicamente −5.0 a −5.4e-9 rad/s
para Galileo): coincide en orden y signo. El ICD lo transmite como
parámetro porque el receptor NO conoce el estado real de la órbita ni
quiere modelar fuerzas — recibe el ajuste ya hecho por el segmento de
control, que además incluye efectos que la fórmula analítica de J2 sola
no captura (luni-solar, términos de mayor grado). Transmitir el número
ajustado es más simple y más preciso que calcularlo.

## Fermi

**F1.** Error radial de 500 m con el satélite en el horizonte: se
proyecta casi entero sobre la línea de vista → **~500 m de rango**.
Error tangencial (along/cross-track): perpendicular a la línea de vista
cuando el satélite está alto → **casi 0**. La componente radial importa
más porque es la que más se alinea con la dirección receptor-satélite en
la mayoría de las geometrías; los errores tangenciales se proyectan con
factores pequeños (seno del ángulo). Por eso POD y los reportes de
calidad orbital siempre separan RTN y miran la radial con lupa: es la
que se filtra directo al rango y, de ahí, al PVT.

**F2.** Broadcast: ~0.7 m de salto cada 3 h. Para un solo juego válido
24 h con el mismo error, el modelo de fuerzas del receptor tendría que
predecir la órbita a <1 m durante 8× más tiempo — necesitaría integrar
todas las perturbaciones (imposible con los parámetros del mensaje) o
recibir un modelo de fuerzas completo (miles de bits). Es más barato
re-emitir: el segmento de control ya tiene la órbita precisa por POD, y
mandar parámetros frescos cada 3 h cuesta unos pocos bits por hora vs.
transmitir un integrador orbital. La ingeniería eligió ancho de banda
sobre validez temporal.

**F3.** 30 estaciones × 1 rango cada 30 s × 86400 s/día = 30 × 2880 =
**86400 mediciones/día por satélite** (menos las que no lo ven: en la
práctica ~1/3 lo tiene arriba en cada instante, ~30000 útiles). Ajustar
~15 parámetros de un arco orbital contra decenas de miles de
observaciones redundantes, con física detallada de fuerzas, reduce el
error a ~cm: la redundancia promedia el ruido de medición y las fuerzas
modeladas capturan lo que la broadcast no puede seguir con un solo juego
de parámetros. Es la diferencia entre ajustar 15 números a 6
observaciones (broadcast, arco corto, pocos parámetros) y a 30000 (POD).

## Conceptuales

**C1.** Porque un modelo de fuerzas (gravedad de alto grado, luni-solar,
presión de radiación con el modelo del cuerpo) no cabe en el mensaje ni
el receptor quiere integrarlo en tiempo real. El ICD hace el trabajo en
tierra: el segmento de control ajusta parámetros keplerianos +
correcciones para que, evaluados con Kepler simple, reproduzcan la
órbita real sobre el arco. El receptor solo evalúa una fórmula cerrada
(anomalía → correcciones → ECEF): barato, determinista, sin integración
numérica. Es delegar la física a tierra y transmitir solo el resultado.

**C2.** Porque las correcciones NO son ortogonales: cada una se ajustó
en presencia de las otras para que el conjunto reproduzca la órbita.
Apagar solo Δn deja los armónicos "tirando" en una dirección que Δn
compensaba → residuo grande (546 m). Apagar TODO vuelve a la elipse
kepleriana desnuda, que resulta estar más cerca de la órbita real en
promedio sobre el arco (239 m) porque los términos que se "descompensan"
al quitar uno solo vuelven a estar ausentes juntos. No es que la elipse
sea mejor modelo: es que los parches solo tienen sentido TODOS juntos, y
quitar uno rompe el balance más que quitarlos todos. Moraleja: el ajuste
es un paquete, no una suma de efectos independientes.

**C3.** Δn e IDOT son ∝ tk: corrigen efectos que se *acumulan* con el
tiempo (deriva de fase, deriva de inclinación) y por eso valen cero en
el instante de referencia Toe y crecen linealmente. Los armónicos Cxx
dependen de la posición en la órbita (2φ), no del tiempo transcurrido:
corrigen la perturbación *permanente* del achatamiento (J2), que actúa
en cada punto de la órbita — incluido Toe. La firma temporal delata la
física: lo acumulativo se anula en el origen, lo permanente no.

**C4.** Con un arco de 12 h en vez de 3 h, el mismo juego de parámetros
tendría que seguir la órbita real 4× más tiempo, y como el error del
ajuste crece con la distancia a Toe, el salto en el empalme sería mucho
mayor (metros a decenas de metros). El salto sub-métrico de Galileo es
consecuencia directa de re-emitir seguido Y de un segmento de control de
alta calidad (buena POD detrás, parámetros bien ajustados). Un salto
grande delataría un arco demasiado largo o una determinación pobre — de
hecho, monitorear los saltos de empalme es una técnica de control de
calidad de la efeméride.

**C5.** OSNMA (M6) autentica el ORIGEN y la INTEGRIDAD del mensaje:
garantiza que los parámetros de efeméride vienen de Galileo y no fueron
alterados en vuelo — con eso, un atacante no puede inyectar una
efeméride falsa que el receptor acepte como auténtica. Pero OSNMA no
valida que los números sean *físicamente sensatos* (no es su trabajo).
Un chequeo de sanidad como el de este lab —¿el semieje corresponde a un
MEO?, ¿la excentricidad es la típica?, ¿el salto contra la efeméride
anterior es sub-métrico?, ¿la órbita propagada es consistente con la
anterior?— es una defensa complementaria: atrapa efemérides corruptas
por error (no por ataque) y agrega una capa de plausibilidad física
sobre la capa criptográfica. Defensa en profundidad: cripto + física.

## Mini-simulacro

1. Porque 6 elementos definen una elipse de DOS cuerpos; la órbita real
   sufre J2, luni-solar y presión de radiación, que la apartan km en
   medio día. Hacen falta correcciones.
2. Achatamiento terrestre (J2, dominante) > atracción luni-solar >
   presión de radiación solar.
3. Δn e IDOT se anulan en Toe (∝ tk, corrigen efectos acumulativos); los
   armónicos Cxx no (dependen de la posición 2φ, corrigen J2 que es
   permanente).
4. Δn valía 546 m de máximo en el arco (cero en Toe). La elipse pura
   extrapolada 12 h: 3603 m ≈ 3.6 km.
5. **Falso**: es un kepleriano con 10 correcciones adicionales (Δn,
   IDOT, OmegaDot, 6 armónicos Cxx) que absorben las perturbaciones
   sobre un arco de ~3 h.
