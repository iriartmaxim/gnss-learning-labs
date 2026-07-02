"""Genera los datos sintéticos de la clase 0.2 (mínimos cuadrados).

Dos datasets:
  - recta: y = 2 + 3x con ruido; la mitad de los puntos con sigma=0.5 y la
    otra mitad con sigma=3.0 (para el ajuste PONDERADO).
  - exponencial: y = a*exp(b*x) con a=2, b=0.5 y ruido, para Gauss-Newton.

Uso: python generar_datos_ajuste.py   (escribe datos_ajuste.json)
"""
import json
import numpy as np


def main():
    rng = np.random.default_rng(42)

    # --- recta con ruido heterocedástico -----------------------------------
    a_true, b_true = 2.0, 3.0          # y = a + b x
    x = np.linspace(0, 10, 20)
    sigmas = np.where(np.arange(20) < 10, 0.5, 3.0)
    y = a_true + b_true * x + rng.normal(0, sigmas)

    # --- exponencial para el ajuste no lineal ------------------------------
    p_true = (2.0, 0.5)                # y = p0 * exp(p1 * x)
    xe = np.linspace(0, 4, 15)
    ye = p_true[0] * np.exp(p_true[1] * xe) * (1 + rng.normal(0, 0.03, 15))

    out = {
        "descripcion": "Datos clase 0.2: recta con ruido heterocedastico y exponencial para Gauss-Newton",
        "recta": {"x": x.tolist(), "y": y.tolist(), "sigma": sigmas.tolist(),
                  "verdad": [a_true, b_true]},
        "exponencial": {"x": xe.tolist(), "y": ye.tolist(),
                        "verdad": list(p_true)},
    }
    with open("datos_ajuste.json", "w") as f:
        json.dump(out, f, indent=2)
    print("datos_ajuste.json escrito")


if __name__ == "__main__":
    main()
