# Soluciones — Clase 5.2 (exclusión)

## Lab

**TODO 1**: al sacar el índice k, si el bias iba en j>k ahora va en j−1.
Referencia: full 1663/16.68; sin E07 → 8.3/1.98; sin E30 → 542/83.0.
**TODO 2**: E07, separación ×~200 (542/8.3 ≈ 65 el segundo... el
criterio usa el 2º mínimo: 542/8.3 = 65 → >10 ✓). **TODO 3**: T 8.3 <
16.3, err 1.98. **TODO 4**: 10 m.

## E1

8 simples; dobles C(8,2)=28 subconjuntos de 6 — y con 12 sats y triples,
C(12,3)=220: el árbol combinatorio de ARAIM.

## E2

Con 7 testigos el LSQ puede torcer más la solución hacia el bias (menos
redundancia que lo frene): parte del fallo se va del residuo al ERROR
(83 m). T baja no porque haya menos fallo sino porque se escondió mejor.

## E3

χ²(0.999, 3) = 16.3 — casualmente el mismo porque 5.1 usó dof mediano 3.
La regla: SIEMPRE recalcular con el dof del subconjunto que verificás.

## F1 / F2

En el README. Órdenes: 28→220 subconjuntos; decenas de GN/s hoy trivial.

## C1

Porque la hipótesis "fallo único en E07" puede ser falsa: si tras
excluir el T sigue alto, había fallo múltiple o el modelo miente —
excluir sin verificar es fabricar confianza.

## C2

Ningún subconjunto simple queda limpio (todos retienen un fallo) → nada
se desploma → el patrón GRITA "hipótesis de fallo único rota" → escalar
(pares, ARAIM) o degradar servicio.

## C3

La fila E30 es el slope en acción: E30 tenía geometría que CONTENÍA el
daño de E07. Los slopes de 5.1 miden eso por satélite: la exclusión
cambia la matriz de slopes entera — integridad y geometría son la misma
conversación.

## Mini-simulacro

1. Desploma el del culpable, resto alto. 2. Sacás 1 y necesitás ≥5 para
verificar. 3. Que la geometría redistribuye el fallo: culpabilidad ≠
"T baja". 4. Sin separación podés señalar a un inocente con ruido.
5. T_post < umbral(dof nuevo) y err/solución estables.

## Entrevista — guión

"Detección: T contra umbral. Identificación: n soluciones leave-one-out;
el subconjunto limpio se desploma; exijo separación del segundo mínimo.
Exclusión: saco, re-resuelvo, re-chequeo con el dof nuevo. Salidas:
excluido-y-verificado / detectado-sin-identificar (degrado servicio) /
patrón anómalo (fallo múltiple: escalo). Y política de re-admisión con
histéresis para no ciclar."

## Mini-caso

Mismo sat: re-admisión prematura (histéresis corta) — alargarla. Otro
sat: día malo de constelación — el FDE debe ser continuo, no evento
único. Modelo: si los T limpios también subieron (¿iono activa? ¿σ
optimista?), el problema es global y excluir satélites de a uno es
whack-a-mole: revisar σ y modelos antes que la lista negra.
