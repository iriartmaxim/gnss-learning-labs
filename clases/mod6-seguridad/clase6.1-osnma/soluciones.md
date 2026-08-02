# Soluciones — Clase 6.1 (primitivas OSNMA)

Vectores autogenerados (reproducibles). El lab termina en "OSNMA PRIMITIVAS OK: 4/4".

## Lab

**TODO 1 (TESLA):** `claves[i] = hashlib.sha256(claves[i+1]).digest()`.
Verificar: hashear la clave revelada `indice` veces y comparar con la KROOT
con `hmac.compare_digest`.

**TODO 2 (Merkle):** al reconstruir, `x = _h(hermano + x)` si la hoja es
hijo derecho (`soy_derecha`), si no `_h(x + hermano)`.

**TODO 3 (ECDSA):** `clave_pub.verify(firma, dig, ec.ECDSA(Prehashed(hashes.SHA256())))`
dentro del try/except; si no lanza, la firma es válida.

## E1 — hashes para verificar TESLA

Clave 7: **7 hashes** (hasheás 7 veces hasta llegar a K0). Clave 30: **30
hashes**. Cuanto más lejos de la raíz, más cómputo — pero es barato (SHA-256
es rápido) y el receptor puede cachear estados intermedios.

## E2 — prueba de Merkle de 1024 hojas

log₂(1024) = **10 hashes hermanos**. Mejor que enviar 1024 claves (10 × 32 B
= 320 B vs 32 KB): la prueba es logarítmica y la raíz de 32 B ya está
embebida. Escala a millones de hojas con pruebas de ~20 hashes.

## E3 — por qué no se puede fabricar la clave futura

El hash es **de un solo sentido**: conocés K_i pero calcular K_{i+1} tal que
H(K_{i+1})=K_i es invertir SHA-256, computacionalmente inviable (2²⁵⁶). Por
eso conocer todas las claves reveladas no ayuda a predecir la próxima: van
en la dirección "difícil" del hash.

## F1 — ancho de banda de los tags

~10 B por tag × varios por subframe = decenas de bytes extra sobre el
mensaje. En E1-B (250 bps) eso es caro: por eso OSNMA usa tags truncados y
un esquema de MACs cuidado para no ahogar el canal de datos.

## F2 — fuerza bruta

2²⁵⁶ ≈ 10⁷⁷ posibilidades. Ni con todo el cómputo del planeta por la edad
del universo se recorre una fracción. Adivinar una clave TESLA antes de que
se revele es imposible en la práctica: la seguridad no está en el secreto
eterno sino en el **orden temporal**.

## Mini-simulacro

1. claves K_i=H(K_{i+1}); se verifica hasheando la revelada hasta la KROOT.
2. que una pubkey pertenece al conjunto, contra la raíz embebida. 3. la
KROOT de la cadena TESLA. 4. raíz Merkle→pubkey→firma→KROOT→TESLA→tags→
datos. 5. autentica los datos, no el rango.
