"""Clase 0.1 — Verificador de entorno del curso.

Chequea Python, las librerías del curso y las herramientas de línea de
comandos. Salida: una tabla con OK/FALTA y el veredicto final.

Uso: python verificar_entorno.py
"""
import importlib
import shutil
import subprocess
import sys

MINIMO_PYTHON = (3, 10)

# (nombre a importar, nombre pip si difiere, para qué se usa)
LIBRERIAS = [
    ("numpy", None, "todo el curso"),
    ("scipy", None, "señales (módulo 2) y utilidades"),
    ("matplotlib", None, "figuras de todos los labs"),
    ("pandas", None, "tablas de observables"),
    ("cryptography", None, "OSNMA (módulo 4)"),
    ("georinex", None, "lectura RINEX (clases 1.3, 1.5)"),
    ("hatanaka", None, "RINEX comprimido Hatanaka (0.4)"),
    ("unlzw3", None, "descompresión .Z legado (0.4)"),
    ("nbformat", None, "notebooks"),
]

HERRAMIENTAS = [
    ("git", "control de versiones del repo"),
    ("jupyter", "notebooks (opcional si usás VS Code)"),
]


def check_python():
    ok = sys.version_info >= MINIMO_PYTHON
    v = ".".join(map(str, sys.version_info[:3]))
    print(f"{'Python':<14} {v:<12} "
          f"{'OK' if ok else f'FALTA >= {MINIMO_PYTHON[0]}.{MINIMO_PYTHON[1]}'}")
    return ok


def check_lib(nombre, pip_name, uso):
    try:
        mod = importlib.import_module(nombre)
        v = getattr(mod, "__version__", "?")
        print(f"{nombre:<14} {v:<12} OK    ({uso})")
        return True
    except ImportError:
        pip = pip_name or nombre
        print(f"{nombre:<14} {'-':<12} FALTA -> pip install {pip}   ({uso})")
        return False


def check_tool(nombre, uso):
    ruta = shutil.which(nombre)
    if ruta:
        try:
            out = subprocess.run([nombre, "--version"], capture_output=True,
                                 text=True, timeout=10).stdout.strip()
            v = out.splitlines()[0][:40] if out else "?"
        except Exception:
            v = "?"
        print(f"{nombre:<14} {v:<40} OK    ({uso})")
        return True
    print(f"{nombre:<14} {'-':<40} FALTA ({uso})")
    return False


if __name__ == "__main__":
    print("=== Verificación del entorno gnss-learning-labs ===\n")
    resultados = [check_python()]
    print()
    resultados += [check_lib(*args) for args in LIBRERIAS]
    print()
    obligatorios_ok = all(resultados)
    opcionales = [check_tool(*args) for args in HERRAMIENTAS]

    print()
    if obligatorios_ok:
        print("VEREDICTO: entorno LISTO para los módulos 0 y 1.")
        if not all(opcionales):
            print("(faltan herramientas opcionales, revisá arriba)")
        sys.exit(0)
    else:
        print("VEREDICTO: FALTAN dependencias. Instalá lo marcado y re-corré.")
        sys.exit(1)
