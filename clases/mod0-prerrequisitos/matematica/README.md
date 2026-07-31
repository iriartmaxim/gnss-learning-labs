# Matemática previa — la rampa al motor de mínimos cuadrados

> Bloque del máster: Prerrequisitos (transversal)

Es el **"Refresco matemático dirigido"** del path: la cadena de
prerrequisitos que hace falta para cursar la [clase 0.2 (mínimos
cuadrados, Gauss-Newton y rotaciones)](../clase0.2-minimos-cuadrados/README.md)
entendiendo cada paso, no recitándolo. Material destilado del cuaderno
de estudio a mano; el criterio de diseño: **números antes que símbolos,
un concepto por vez, y verificación propia de cada regla**.

## La cadena de dependencias

```
Límites  ──►  Derivadas  ──►  Mínimos cuadrados  ──►  Jacobiano / Gauss-Newton / PVT
 (h→0)      (ritmo, ∂,        (ecuaciones            (clase 0.2 y puente
            cadena)           normales)               a la 1.2)
```

Cada flecha es un "necesito esto para entender lo siguiente". Se estudia
de izquierda a derecha.

## Orden de estudio

1. [limites.md](limites.md) — la idea de *acercarse* a un valor ($h \to 0$)
   y el caso $0/0$ indeterminado. El cimiento: **la derivada es un 0/0
   resuelto**.
2. [derivadas.md](derivadas.md) — ritmo de cambio medido con tablas, las
   4 piezas básicas y sus 2 reglas, la justificación analítica por
   definición, derivada parcial (congelar) y regla de la cadena — hasta
   derivar la $S$ completa y armar las **ecuaciones normales**.
3. **Clase 0.2** — acá se entra al lab: mínimos cuadrados con las
   ecuaciones normales, la versión ponderada, Gauss-Newton y rotaciones.
4. [jacobiano-y-linealizacion.md](jacobiano-y-linealizacion.md) — el
   cierre: gradiente → jacobiano (fila = observación, columna =
   parámetro), linealización y su error $h^2$, el loop de Gauss-Newton y
   el puente a la matriz de geometría $G$ del PVT. Deja respondido el
   **Checkpoint del Módulo 0**.
5. [repaso-autotests.md](repaso-autotests.md) — para las sesiones de
   repaso espaciado: toda la cadena en auto-tests plegados, bloque por
   bloque. Regla: **recuperar, no reconocer**.

## Cómo usar este material

- **A mano primero**: papel, calculadora y un borrador. La máquina solo
  para aritmética repetitiva o para verificar (cada nota trae su
  verificador en Python).
- **Terminología formal al frente** (sustitución directa, cociente
  incremental, discontinuidad evitable, matriz jacobiana, ecuaciones
  normales…), con lo informal entre paréntesis como apoyo.
- **Chequeos de cordura siempre**: distancias jamás negativas, resultados
  en ventanas esperadas, verificar sustituyendo.
- Los ejercicios traen la solución plegada (`▸ Solución`): resolvé antes
  de desplegar.

## Dónde desemboca

El checkpoint del Módulo 0 pide *explicar por qué linealizar el problema
PVT lo convierte en mínimos cuadrados iterativos, y qué rol juega el
jacobiano*. Esta rampa existe para poder responderlo con fundamento:
sin límites no hay derivada, sin derivadas no hay jacobiano, sin
jacobiano no hay Gauss-Newton — y sin Gauss-Newton no hay posición.
