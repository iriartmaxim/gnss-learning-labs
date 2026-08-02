# Soluciones — Clase 6.2 (cadena OSNMA)

Núcleo end-to-end reproducible (reusa 6.1). "CADENA OSNMA OK".

## Lab

| Chequeo | Referencia |
|---|---|
| Stream limpio | 20 autenticados / 0 rechazados |
| Stream con frame manipulado (época 10) | 19 / 1 (el alterado falla) |
| Clave TESLA falsa vs KROOT | rechazada |

**TODO 1:** `if hmac.compare_digest(tag_tesla(clave, datos), tag): aut += 1
else: rec += 1`. El tag solo cierra si los datos NO fueron alterados y la
clave es la correcta.

## Conexión con galmon (feed real)

[galmon.eu](https://galmon.eu) publica telemetría Galileo en vivo,
incluyendo los campos OSNMA (DSM-KROOT, tags, claves TESLA reveladas). La
lógica de verificación es **idéntica** a este lab; lo que cambia es la
fuente: en vez de un stream sintético, parseás el feed. Requiere red y
seguir el formato vigente del OSNMA SIS ICD / Receiver Guidelines. El
núcleo sintético prueba que tu verificador es correcto antes de enchufarlo
a datos vivos.

## E1 — por qué el orden importa

Se verifica de la raíz hacia afuera: primero que la pubkey está en el árbol
(contra la raíz embebida, lo único en lo que confiás de fábrica), después
que firmó el KROOT, y recién entonces se aceptan las claves TESLA y los
tags. Invertir el orden sería confiar en algo no probado.

## E2 — la revelación diferida en el stream

La clave de la época e se usa para el tag de e, pero se **revela en e+1**.
El receptor guarda el tag y espera la clave; al llegar, verifica que es de
la cadena (hash hasta KROOT) y que el tag cierra. Si un atacante intentara
inventar la clave antes, no podría (hash de un solo sentido, 6.1).

## Mini-simulacro

1. raíz Merkle→pubkey→firma→KROOT→TESLA→tags→datos. 2. porque es lo único
embebido/confiable de fábrica. 3. la clave se revela un subframe después
del tag. 4. el tag no cierra → se rechaza el frame. 5. galmon (feed vivo).
