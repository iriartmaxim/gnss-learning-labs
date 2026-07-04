#!/usr/bin/env python3
"""fetch_iq.py — baja las capturas IQ de gnss-sdr para la clase 2.2.

Capturas oficiales del proyecto gnss-sdr (chicas, sin cuenta), en
sourceforge. Deja los .dat en data/raw/iq/ y saltea lo ya bajado.
Solo stdlib: urllib. Correr desde la raíz del repo:

    python3 tools/fetch_iq.py            # baja las 3 (GPS, Galileo, CTTC)
    python3 tools/fetch_iq.py --solo gps # baja solo una
"""
from __future__ import annotations

import argparse
import shutil
import sys
import urllib.error
import urllib.request
from pathlib import Path

BASE = "https://sourceforge.net/projects/gnss-sdr/files/data/{f}/download"

CAPTURAS = {
    "gps": "GPS_L1_CA_ID_1_Fs_4Msps_2ms.dat",
    "galileo": "Galileo_E1_ID_1_Fs_4Msps_8ms.dat",
    "cttc": "GSoC_CTTC_capture_2012_07_26_4Msps_4ms.dat",
}


def descargar(url: str, destino: Path) -> bool:
    try:
        print(f"  bajando {destino.name}")
        req = urllib.request.Request(url, headers={"User-Agent": "curl/8"})
        with urllib.request.urlopen(req, timeout=180) as r, \
                open(destino, "wb") as f:
            shutil.copyfileobj(r, f)
        print(f"  ok: {destino.name} ({destino.stat().st_size/1024:,.0f} KiB)")
        return True
    except urllib.error.URLError as e:
        print(f"  [error] {e}")
        return False


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dest", default="data/raw/iq",
                    help="carpeta de salida (default: data/raw/iq)")
    ap.add_argument("--solo", choices=sorted(CAPTURAS),
                    help="bajar solo una captura")
    args = ap.parse_args()

    destino = Path(args.dest)
    destino.mkdir(parents=True, exist_ok=True)
    pedidos = [args.solo] if args.solo else list(CAPTURAS)

    ok = True
    for clave in pedidos:
        nombre = CAPTURAS[clave]
        ruta = destino / nombre
        print(f"\n[{clave}]")
        if ruta.exists():
            print(f"  ya existe {ruta.name}, salteo")
            continue
        ok = descargar(BASE.format(f=nombre), ruta) and ok

    print("\n=== resumen ===")
    for clave in pedidos:
        ruta = destino / CAPTURAS[clave]
        print(f"  {clave:8s} -> {'OK' if ruta.exists() else 'FALTA'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
