#!/usr/bin/env python3
"""Solución — mapear cada archivo de data/raw a su eslabón del arco.

Correr desde la raíz del repo:
    python3 clases/mod0-prerrequisitos/vision-global/lab/soluciones/lab_arco_solucion.py
"""
import sys
from pathlib import Path

# eslabón del arco al que alimenta cada tipo de archivo, y clase que lo usa
def clasificar(nombre: str):
    n = nombre.upper()
    if n.endswith(".DAT"):
        return ("señal", "mod2 (2.1-2.4)")
    if "_MO." in n or n.endswith("_MO.RNX") or "_MO.CRX" in n:
        return ("observable", "1.5 (PVT), 3.x (errores)")
    if "ORB.SP3" in n:
        return ("órbita (precisa)", "1.3, 4.1, 4.2")
    if "CLK.CLK" in n:
        return ("error/reloj", "1.5, 4.3")
    if "_MN." in n:
        return ("órbita (broadcast)", "1.3, 4.1")
    return ("¿?", "—")


def main() -> int:
    raiz = Path("data/raw")
    if not raiz.exists():
        print("No encuentro data/raw — corré tools/fetch_data.py (clase 0.4)")
        return 1
    archivos = sorted(p.name for p in raiz.rglob("*") if p.is_file())
    print(f"== {len(archivos)} archivos en data/raw, mapeados al arco ==\n")
    conteo = {}
    for a in archivos:
        eslabon, clase = clasificar(a)
        conteo[eslabon] = conteo.get(eslabon, 0) + 1
        print(f"  {a:48s} -> {eslabon:20s} [{clase}]")

    print("\n== censo por eslabón ==")
    for eslabon, n in sorted(conteo.items()):
        print(f"  {eslabon:20s} {n}")

    # auto-test: los cuatro eslabones de datos tienen que estar presentes
    esperados = {"señal", "observable", "órbita (broadcast)", "órbita (precisa)", "error/reloj"}
    faltan = esperados - set(conteo)
    assert not faltan, f"faltan eslabones (¿bajaste todo en 0.4?): {faltan}"
    assert "¿?" not in conteo, "quedó un archivo sin clasificar"
    print("\nMAPEO OK: el arco señal→observable→órbita→error está cubierto por tus datos")
    return 0


if __name__ == "__main__":
    sys.exit(main())
