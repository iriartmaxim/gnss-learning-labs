# Soluciones — Clase 6.5 (jamming)

IQ sintética determinista. El lab termina en "JAMMING OK".

## Lab

| Métrica | Referencia |
|---|---|
| Subida de potencia con jammer | ~30 dB (J/S) |
| Detección por energía | 100 % (falsa alarma 0 %) |
| Caída de C/N0 | ~26 dB-Hz |
| Tracking | PERDIDO (C/N0 ~28 dB-Hz < 30) |

**TODO 1:** `disparo = pot > base + k*sig`. La detección por energía es lo
que hace el AGC de un receptor real: la potencia total salta y se satura.

**Por qué el C/N0 cae aunque la potencia suba:** el jammer eleva el **piso
de ruido**; el C/N0 mide la señal GNSS *sobre* ese piso, así que cae aunque
la potencia total del canal suba. Mirar el pico del espectro engaña (se
engancha al jammer); hay que mirar la señal en su bin sobre el ruido.

## E1 — jamming vs spoofing

Jamming: **niega** el servicio (ahoga la señal con ruido/potencia) —
ruidoso y fácil de detectar (salta el AGC). Spoofing: **engaña** (señales
falsas creíbles) — sutil y difícil. El jammer es un martillo; el spoofer,
un carterista.

## E2 — chirp vs CW

El CW (tono fijo) concentra su energía en una frecuencia: un filtro notch
puede recortarlo. El chirp barre toda la banda, así que ningún notch fijo
lo saca — por eso es el jammer barato más efectivo (y el más común en los
"personal privacy devices" de camioneros).

## F1 — potencia del jammer

Un jammer de 1 W a 100 m contra una señal GNSS de ~1e-16 W: J/S de ~130 dB
en el peor caso. Por eso basta un dispositivo diminuto y barato para negar
GNSS en cientos de metros: la señal llega feblísima desde 20 000 km.

## Mini-simulacro

1. jamming niega, spoofing engaña. 2. el AGC/energía salta (potencia total).
3. el jammer sube el piso de ruido → C/N0 (señal/ruido) cae. 4. el chirp
barre la banda, evade el notch. 5. abajo de ~30 dB-Hz el lazo pierde
enganche.
