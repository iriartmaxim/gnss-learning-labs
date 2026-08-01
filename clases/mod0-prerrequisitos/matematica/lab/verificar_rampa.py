#!/usr/bin/env python3
"""Verificador de la rampa matemática (lab-lite).

Chequea los números de referencia de toda la cadena: si termina en
"RAMPA OK", estás en condiciones de entrar al lab de la clase 0.2.
Correr desde la raíz del repo:

    python3 clases/mod0-prerrequisitos/matematica/lab/verificar_rampa.py
"""
import numpy as np

fallas = []
def check(nombre, cond):
    print(f"  {'OK ' if cond else 'MAL'}  {nombre}")
    if not cond:
        fallas.append(nombre)

print("== Derivadas: el verificador universal (ritmo) ==")
def ritmo(f, x, h=1e-3):
    return (f(x + h) - f(x)) / h
check("constante -> 0", abs(ritmo(lambda b: 9, 5)) < 1e-9)
check("rampa -6b -> -6", abs(ritmo(lambda b: -6 * b, 5) + 6) < 1e-9)
check("b^2 en 5 -> 2b = 10", abs(ritmo(lambda b: b**2, 5) - 10) < 0.01)
check("cadena: (3-b)^2 en b=1 -> 2b-6 = -4", abs(ritmo(lambda b: (3 - b)**2, 1) + 4) < 0.01)

print("== Ecuaciones normales: la tabla de 9 puntos ==")
x = np.array([7, 1, 10, 5, 4, 3, 13, 10, 2], float)
y = np.array([2, 9, 2, 5, 7, 11, 2, 5, 14], float)
n = len(x)
check("montones: Σx=55 Σy=57 Σxy=233 Σx²=473",
      (x.sum(), y.sum(), (x * y).sum(), (x**2).sum()) == (55, 57, 233, 473))
m = (n * (x * y).sum() - x.sum() * y.sum()) / (n * (x**2).sum() - x.sum()**2)
b = (y.sum() - m * x.sum()) / n
check("m ≈ -0,8425", abs(m + 0.8425) < 5e-4)
check("b ≈ 11,48", abs(b - 11.48) < 5e-2)
check("verificación 473m + 55b ≈ 233", abs(473 * m + 55 * b - 233) < 1e-9)

print("== Linealización: el error h² ==")
p0, h = 3.0, 0.5
pred = p0**2 + 2 * p0 * h
check("predicción 12, realidad 12.25, error 0.25 = h²",
      abs((p0 + h)**2 - pred - h**2) < 1e-12)

print("== Gauss-Newton 1D: p² = 9 desde p0 = 2 ==")
p = 2.0
pasos = []
for _ in range(3):
    r = 9 - p**2          # residuo: medido - predicho
    J = 2 * p             # jacobiano 1D (el ritmo)
    delta = r / J         # (JᵀJ)δ = Jᵀr en 1D
    p += delta
    pasos.append(round(p, 4))
check("iteraciones 3.25 -> 3.0096 -> 3.0000", pasos[:2] == [3.25, 3.0096] and abs(p - 3) < 1e-4)

print("== Jacobiano: numérico vs analítico (modelo del Lab 0.2) ==")
def jac_numerico(f, p, h=1e-6):
    p = np.asarray(p, float)
    f0 = np.asarray(f(p))
    J = np.zeros((f0.size, p.size))
    for j in range(p.size):
        dp = p.copy(); dp[j] += h
        J[:, j] = (np.asarray(f(dp)) - f0) / h
    return J
xs = np.array([0.0, 1.0, 2.0])
fm = lambda q: q[0] * np.exp(q[1] * xs)
q = np.array([2.0, 0.5])
J_ana = np.column_stack([np.exp(q[1] * xs), q[0] * xs * np.exp(q[1] * xs)])
check("‖J_num − J_ana‖ < 1e-4", np.abs(jac_numerico(fm, q) - J_ana).max() < 1e-4)

print("== Fila del PVT: el gradiente unitario ==")
g = np.array([3.0, 4.0]) / 5.0
check("∇√(x²+y²) en (3,4) = (0.6, 0.8), unitario",
      np.allclose(g, [0.6, 0.8]) and abs(np.linalg.norm(g) - 1) < 1e-12)

print()
if fallas:
    print(f"RAMPA INCOMPLETA: revisá {fallas}")
    raise SystemExit(1)
print("RAMPA OK: estás en condiciones de entrar al lab de la clase 0.2")
