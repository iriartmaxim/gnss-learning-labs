# Soluciones — Clase 7.3 (DGNSS)

Referencia: día 166, 12:00–13:00, E1 monofrecuencia. Los produce el lab.

## Lab

| Métrica | Referencia |
|---|---|
| Baseline | 715 km |
| Épocas comunes | 121 |
| RMS standalone E1 | 4.46 m |
| RMS DGNSS | 1.09 m |
| Mejora | 76 % (×4.1) |

**TODO 1 (PRC):** `prc[s] = np.linalg.norm(xyz - pos_base) - Pc`. El primer
término es la verdad (base conocida); `Pc` es la pseudodistancia ya
corregida por reloj de satélite/tropo. La diferencia captura el error
común residual (órbita + iono + reloj residual) visto en la base.

**TODO 2 (aplicar):** `Pc += prc[s]` antes de acumular para el PVT del
rover. Al sumar la corrección de la base, el error común se cancela en el
ajuste.

## E1 — cuánto queda

El reloj de +8 m común se cancela **entero** (queda ~0). El multipath de
3 m del rover, que la base no ve, queda **intacto**: DGNSS no toca los
errores locales. Moraleja: el diferencial ataca el sesgo común, no el
ruido propio.

## E2 — residual atmosférico

715 km × ~1–2 mm/km ≈ 0.7–1.4 m de decorrelación iono → del orden del
1.09 m medido. La cuenta cierra: casi todo el residual del DGNSS a esta
distancia es atmósfera decorrelacionada, no reloj/órbita (esos ya se
cancelaron).

## E3 — con iono-free

Con iono-free la ionosfera ya está removida en ambos, así que el
diferencial solo tendría por cancelar el reloj de satélite residual y la
órbita — errores ya chicos con broadcast. La mejora sería marginal (de
hecho, sobre 715 km puede empeorar, porque inyecta la tropo decorrelada de
la base). Por eso el lab usa E1 sola: ahí el diferencial tiene algo grande
(la iono) que corregir.

## F1 — residual a 20 km

Si el residual escala ~linealmente con el baseline: 20/715 × 1.09 ≈ **3 cm**
de residual atmosférico a 20 km. Por eso el DGNSS operativo con bases
cercanas llega a decímetros/cm de código — y con fase (RTK), a cm reales.

## F2 — edad de la corrección

3600 PRC por satélite por hora (una por segundo). La *edad* importa porque
el reloj del satélite deriva y su geometría cambia (~3.7 km/s): una PRC de
hace 10 s ya no describe bien el error actual. Los formatos RTCM incluyen
la tasa de cambio del PRC justamente para extrapolar entre mensajes.

## Mini-simulacro

1. PRC=‖s−base‖−P_corr_base; absorbe reloj sat + órbita + atmósfera de la
base. 2. común: reloj sat, órbita, iono/tropo (si cerca); local: multipath,
ruido. 3. baseline 715 km → atmósfera decorrelacionada. 4. E1: la iono es
error grande a corregir → gran mejora; iono-free ya la quitó. 5. DGNSS
código dm-m; RTK fase+ambigüedades cm baseline corto; PPP productos
precisos globales sin base, converge lento.
