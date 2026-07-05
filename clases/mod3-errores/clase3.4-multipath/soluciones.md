# Soluciones — Clase 3.4

## Ejercicios a mano

**E1.** De Φ₁ − Φ₅ = (γ−1)·I + (B₁−B₅) sale I = (Φ₁−Φ₅)/(γ−1) + cte.
Entonces MP₁ = P₁ − Φ₁ − 2I = P₁ − (1+k)·Φ₁ + k·Φ₅ + cte, con
k = 2/(γ−1) = **2.521**. Verificación: el coeficiente de ρ (geometría +
relojes + tropo, común a los tres observables) es 1 − (1+k) + k = 0 ✓;
el de I es 1 + (1+k) − kγ = 2 − 2 = 0 ✓. Para MP₅ el retardo propio es
γI: MP₅ = P₅ − Φ₅ − 2γI = P₅ − k'·Φ₁ + (k'−1)·Φ₅ con
k' = 2γ/(γ−1) = **4.521**. Todo lo que dependía del camino desapareció:
quedan multipath + ruido + una constante que vive y muere con el arco.

**E2.** Fasores: directo 1·e^{j0}, reflejo α·e^{jψ}. La fase de la suma
es δ = atan[α·senψ / (1 + α·cosψ)], máxima cuando el reflejo llega en
cuadratura efectiva: δ_max = asin(α). Como α < 1, δ_max < 90° = un
cuarto de ciclo ⇒ el error de fase es **< λ/4 SIEMPRE**, sin importar la
geometría. En metros: E1 → 19.03/4 = **4.76 cm**; E5a → 25.48/4 =
**6.37 cm**. (Curioso: la cota de fase de E5a es *mayor* — λ más larga —
y sin embargo su código es mejor: cota de fase y envelope de código son
animales distintos.)

**E3.** Δ = 2h·sin(el) con h = 2 m: 10° → **0.69 m**, 30° → **2.0 m**,
90° → **4.0 m**. En chips: E1 (293 m) → 0.002 / 0.007 / 0.014; E5a
(29.3 m) → 0.02 / 0.07 / 0.14. Ambos ecos son "cercanos" (Δ ≪ chip):
caen en la zona lineal del discriminador, donde el sesgo depende de Δ y
de la amplitud α — casi NO del chip. La ventaja del chip corto no está
acá: está en que E5a **corta** los ecos de más de ~44 m (1.5 chips)
que E1 sigue tragando hasta ~440 m. El suelo pega parejo; el galpón de
la otra cuadra, solo en E1.

## Fermi

**F1.** f ≈ (2h/λ)·d(sin el)/dt. Con 2h/λ = 21 ciclos por unidad de
sin(el) y d(sin el)/dt = cos(20°)·0.1°/min ≈ 0.0016 /min: f ≈ 0.035
ciclos/min ⇒ **período ≈ 29 min** — a 30 s de muestreo son ~58 muestras
por ciclo: sobra. Un satélite más rápido (0.5°/min) da ~6 min, también
visible. Y la inversión es GNSS-IR: medí f en tus datos y despejá h —
la altura de la antena sobre el reflector, gratis.

**F2.** Del RMS de 34 cm a baja elevación, ~la mitad es ruido blanco y
~la mitad multipath lento (τ ≈ 5–10 min). Promediando: 1 min (2
muestras) el ruido baja √2 y el MP ni se entera → ~29 cm; 5 min → ruido
casi muerto, MP intacto → ~25 cm; 20 min → recién ahí el promedio cruza
el tiempo de correlación y el MP empieza a ceder → ~12–15 cm. **El codo
está en τ_corr**: antes, promediar mata solo ruido; después, empieza a
matar multipath. Por eso el código suavizado por fase (Hatch) usa
ventanas de ~100 s y no de una hora (además lo limita la divergencia
iono de la 3.1).

**F3.** GPS: la geometría vuelve cada día sidéreo (86164 s) ⇒ se
adelanta 86400 − 86164 = **236 s/día** (mirá 3m56s antes cada día).
Galileo: 17 órbitas en 10 días sidéreos = 861 641 s ⇒ contra los
864 000 s civiles se adelanta **2359 s ≈ 39.3 min por ciclo**. El día
186, E30 repite lo del 176 unos 39 min antes: si el arco arrancó 11:15,
esperalo ~10:36. (Tu lag medido, −2430 s, difiere 71 s del nominal:
drift orbital real + resolución de 30 s + ancho del pico de
correlación.)

## Conceptuales

**C1.** La corrección transmisible exige que el error sea **compartido**
entre receptores (iono: la misma nube de electrones para toda la
región) o **derivable de pocos datos** (tropo: P, T, e locales). El
multipath depende de la geometría fina — centímetros — de TU entorno:
solo tu antena lo ve, nadie puede calcularlo por vos. La escalera del
módulo: iono = global-corregible/medible; tropo = local-modelable;
multipath = local-**solo mitigable u observable**; ruido = ni siquiera
es señal — solo estadística (√N).

**C2.** La "constante" del MP incluye las ambigüedades N₁, N₅ — que son
constantes solo mientras el tracking no se corta. Un salto de ciclo
cambia N en un entero: con los coeficientes 3.521/2.521, un slip de 1
ciclo mete un escalón de ~65 cm en MP. Si restás una media global sobre
el escalón, ambos tramos quedan sesgados en sentidos opuestos:
multipath fantasma. `sub_arcos` corta donde |ΔMP| > 1 m entre épocas —
pesca slips de ≥2 ciclos; uno de exactamente 1 ciclo (~0.65 m) se le
cuela: los QC serios usan detectores dedicados (Melbourne–Wübbena,
TurboEdit) antes de formar el MP.

**C3.** Si σ(dif)/√2 ≈ RMS total, las muestras a 30 s ya están casi
decorrelacionadas: el proceso dominante vive por debajo de 30 s — es
decir, **ruido de código**, no multipath lento. Eso ES el certificado de
calidad de LPGS: choke ring + sitio limpio dejaron poco MP, y lo que
queda se esconde a baja elevación (Parte B) y en la componente lenta que
la correlación sideral rescata (Parte C). En una estación mala (chapa al
lado, antena de patch), el MP lento domina: σ(dif)/√2 ≪ RMS, y el
estimador separa limpio. El cociente σ_dif/RMS es, él solo, un
diagnóstico del sitio.

**C4.** Por el envelope: con Δ ≪ chip el sesgo está en la zona lineal
del discriminador y depende de Δ y α, no del chip — y a baja elevación
los ecos dominantes son exactamente esos (suelo cercano, Δ < 1 m, α
grande por ganancia de antena e incidencia rasante): E1 y E5a sufren
parecido, y el C/N0 más pobre empareja para abajo. La ventaja del chip
corto aparece con reflectores a decenas–cientos de metros (Δ comparable
al chip de E5a): E5a los corta de plano, E1 los integra. Elevaciones
medias/altas + entorno con estructuras = el reino de E5a (tu 20–25%).

**C5.** Un spoofer de una antena transmite TODOS los PRN por el mismo
canal físico, y eso deja tres huellas: (1) el multipath del camino
spoofer→víctima se imprime idéntico en todos los canales ⇒ la
correlación inter-canal de los MP se dispara (en cielo real cada
satélite tiene su geometría y sus MP son ~independientes); (2) la firma
de elevación desaparece: un "satélite a 80°" con fading de incidencia
rasante es un oxímoron físico; (3) la huella sideral: tu sitio imprime
en cada satélite un patrón MP(t) que se repite con el calendario
orbital — el atacante no lo conoce ni puede reproducirlo por-PRN
coherentemente, así que la *ruptura de la repetición esperada* delata.
Es defensa por capa física, ortogonal a OSNMA (que autentica los datos,
no el canal): juntas cierran la pinza — el módulo 6 empieza ahí.

## Mini-simulacro

1. MP₁ = P₁ − 3.521·Φ₁ + 2.521·Φ₅. Elimina geometría, relojes, tropo e
   iono; deja multipath + ruido + una constante por arco.
2. La fase es interferencia de fasores: corrimiento ≤ asin(α) < λ/4
   (4.8 cm en E1). El código correla el eco completo: sesgo hasta
   ~chip/2, y el chip mide cientos de metros.
3. Cada 10 días: 17 órbitas de 14h04m45s caben exactas en 10 días
   sidéreos; contra el reloj civil la geometría se adelanta 2359 s.
4. 25.1 cm global; 34 cm por debajo de 30° contra 11–14 cm por encima
   de 45°: ×3 del horizonte al cenit.
5. **Falso**: la figura 3 muestra r = 0.60 entre el E30 de hoy y el de
   hace 10 días corrido −2430 s (y r ≈ 0 sin corrimiento). El azar no
   tiene memoria; la geometría sí.
