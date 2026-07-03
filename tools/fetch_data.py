#!/usr/bin/env python3
"""fetch_data.py — descarga y descomprime datos GNSS reales (BRDC, SP3, CLK).

Fuentes anónimas por HTTPS/HTTP (sin cuenta):
  - BRDC nav multi-GNSS : BKG   https://igs.bkg.bund.de/root_ftp/IGS/BRDC/
  - SP3 / CLK  MGEX     : CODE  http://ftp.aiub.unibe.ch/CODE_MGEX/CODE/
    (finales: latencia ~2 semanas; para fechas recientes cae al SP3
     rapido de IGS en BKG, que es SOLO GPS y se avisa por pantalla)

  - OBS RINEX 30 s    : BKG   https://igs.bkg.bund.de/root_ftp/IGS/obs/
    (Hatanaka: si el paquete 'hatanaka' esta instalado deja el .rnx;
     si no, queda el .crx y se imprime como convertirlo)

Uso:
    python tools/fetch_data.py --date 2026-06-15
    python tools/fetch_data.py --date 2026-06-15 --que brdc,sp3,clk
    python tools/fetch_data.py --date 2026-06-15 --dest data/raw
    python tools/fetch_data.py --date 2026-06-15 --que obs --estacion CORD00ARG

Deja los archivos DESCOMPRIMIDOS en <dest>/<yyyy>/<ddd>/ y saltea lo que
ya existe (idempotente). Solo stdlib: urllib + gzip.

Otras fuentes (documentadas en la clase 0.4, no automatizadas aca):
  - CDDIS (NASA)  : requiere cuenta Earthdata.
  - RAMSAC (IGN)  : RINEX de observacion de la red CORS argentina;
                    portal con formulario -> descarga manual
                    (las IGS argentinas LPGS/CORD/UNSA/MGUE/RIO2/RGDG
                     salen automaticas con --que obs).
  - galmon.eu     : telemetria Galileo en vivo (modulo 4, OSNMA).
"""
from __future__ import annotations

import argparse
import gzip
import re
import shutil
import sys
import urllib.error
import urllib.request
from datetime import date, datetime
from pathlib import Path

BKG_BRDC = "https://igs.bkg.bund.de/root_ftp/IGS/BRDC/{yyyy}/{ddd}/"
BKG_OBS = "https://igs.bkg.bund.de/root_ftp/IGS/obs/{yyyy}/{ddd}/"
BKG_IGS_PROD = "https://igs.bkg.bund.de/root_ftp/IGS/products/{week}/"
CODE_MGEX = "http://ftp.aiub.unibe.ch/CODE_MGEX/CODE/{yyyy}/"

# prioridad de archivos BRDC dentro del indice de BKG (todos multi-GNSS)
BRDC_PRIORIDAD = ("BRDC00IGS_R", "BRDC00WRD_R", "BRD400DLR_S", "BRDM00DLR_S")

GPS_EPOCH = date(1980, 1, 6)


def semana_gps(d: date) -> int:
    return (d - GPS_EPOCH).days // 7


def listar_indice(url: str) -> list[str]:
    """Devuelve los href de un indice de directorio Apache/nginx."""
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            html = r.read().decode("utf-8", "replace")
    except urllib.error.URLError as e:
        print(f"  [aviso] no pude listar {url}: {e}")
        return []
    return re.findall(r'href="([^"?/][^"]*)"', html)


def descargar(url: str, destino: Path) -> bool:
    """Descarga url -> destino. True si quedo el archivo."""
    try:
        print(f"  bajando {url}")
        with urllib.request.urlopen(url, timeout=120) as r, open(destino, "wb") as f:
            shutil.copyfileobj(r, f)
        kb = destino.stat().st_size / 1024
        print(f"  ok: {destino.name} ({kb:,.0f} KiB)")
        return True
    except urllib.error.HTTPError as e:
        print(f"  [aviso] HTTP {e.code} para {url}")
        return False
    except urllib.error.URLError as e:
        print(f"  [aviso] error de red: {e}")
        return False


def descomprimir_gz(gz: Path) -> Path:
    salida = gz.with_suffix("")  # saca el .gz
    with gzip.open(gz, "rb") as fin, open(salida, "wb") as fout:
        shutil.copyfileobj(fin, fout)
    gz.unlink()
    print(f"  descomprimido -> {salida.name} "
          f"({salida.stat().st_size/1024:,.0f} KiB)")
    return salida


def traer_brdc(d: date, destino: Path) -> Path | None:
    """Navegacion broadcast multi-GNSS del dia, desde BKG."""
    yyyy, ddd = d.strftime("%Y"), d.strftime("%j")
    nombre_esperado = f"BRDC00IGS_R_{yyyy}{ddd}0000_01D_MN.rnx"
    final = destino / nombre_esperado
    if final.exists():
        print(f"  ya existe {final.name}, salteo")
        return final

    base = BKG_BRDC.format(yyyy=yyyy, ddd=ddd)
    indice = listar_indice(base)
    candidatos = [h for pref in BRDC_PRIORIDAD
                  for h in indice if h.startswith(pref) and h.endswith(".rnx.gz")]
    if not candidatos:
        # sin indice: probar el nombre canonico directo
        candidatos = [f"BRDC00IGS_R_{yyyy}{ddd}0000_01D_MN.rnx.gz"]
    for nombre in candidatos:
        gz = destino / nombre
        if descargar(base + nombre, gz):
            return descomprimir_gz(gz)
    print("  [error] no consegui BRDC para ese dia")
    return None


def traer_sp3(d: date, destino: Path) -> Path | None:
    """Orbitas precisas: CODE MGEX final (multi-GNSS); si no esta
    publicado aun, SP3 rapido de IGS (solo GPS)."""
    yyyy, ddd = d.strftime("%Y"), d.strftime("%j")
    fin = f"COD0MGXFIN_{yyyy}{ddd}0000_01D_05M_ORB.SP3"
    final = destino / fin
    if final.exists():
        print(f"  ya existe {final.name}, salteo")
        return final
    gz = destino / (fin + ".gz")
    if descargar(CODE_MGEX.format(yyyy=yyyy) + fin + ".gz", gz):
        return descomprimir_gz(gz)

    print("  [aviso] final MGEX no disponible (fecha muy reciente): "
          "pruebo el rapido de IGS (SOLO GPS)")
    rap = f"IGS0OPSRAP_{yyyy}{ddd}0000_01D_15M_ORB.SP3"
    final = destino / rap
    if final.exists():
        print(f"  ya existe {final.name}, salteo")
        return final
    gz = destino / (rap + ".gz")
    url = BKG_IGS_PROD.format(week=semana_gps(d)) + rap + ".gz"
    if descargar(url, gz):
        return descomprimir_gz(gz)
    print("  [error] no consegui SP3 para ese dia")
    return None


def traer_clk(d: date, destino: Path) -> Path | None:
    """Relojes precisos 30 s, CODE MGEX final (para la clase 1.5)."""
    yyyy, ddd = d.strftime("%Y"), d.strftime("%j")
    nombre = f"COD0MGXFIN_{yyyy}{ddd}0000_01D_30S_CLK.CLK"
    final = destino / nombre
    if final.exists():
        print(f"  ya existe {final.name}, salteo")
        return final
    gz = destino / (nombre + ".gz")
    if descargar(CODE_MGEX.format(yyyy=yyyy) + nombre + ".gz", gz):
        return descomprimir_gz(gz)
    print("  [aviso] CLK final no disponible para esa fecha")
    return None


def traer_obs(d: date, destino: Path, estacion: str) -> Path | None:
    """RINEX de observacion 30 s de una estacion IGS, desde BKG.

    Viene en Hatanaka comprimido (.crx.gz). Si el paquete `hatanaka`
    esta instalado, deja directamente el .rnx; si no, deja el .crx e
    imprime el comando para convertirlo (fetch_data sigue siendo
    stdlib-only)."""
    yyyy, ddd = d.strftime("%Y"), d.strftime("%j")
    est = estacion.upper()
    nombre = f"{est}_R_{yyyy}{ddd}0000_01D_30S_MO"
    rnx, crx, gz = (destino / (nombre + ext)
                    for ext in (".rnx", ".crx", ".crx.gz"))
    if rnx.exists():
        print(f"  ya existe {rnx.name}, salteo")
        return rnx
    if not (crx.exists() or gz.exists()):
        url = BKG_OBS.format(yyyy=yyyy, ddd=ddd) + nombre + ".crx.gz"
        if not descargar(url, gz):
            print(f"  [error] no consegui observacion de {est}; "
                  "argentinas tipicas: LPGS00ARG CORD00ARG UNSA00ARG "
                  "MGUE00ARG RIO200ARG RGDG00ARG")
            return None
    try:
        import hatanaka
    except ImportError:
        if gz.exists() and not crx.exists():
            descomprimir_gz(gz)
        print("  [aviso] sin el paquete 'hatanaka' queda en formato "
              "Hatanaka (.crx). Para pasarlo a RINEX:\n"
              "      pip install hatanaka\n"
              f"      python3 -c \"import hatanaka; "
              f"hatanaka.decompress_on_disk('{crx}')\"")
        return crx
    objetivo = gz if gz.exists() else crx
    salida = Path(hatanaka.decompress_on_disk(str(objetivo)))
    if salida.exists() and salida != objetivo:
        objetivo.unlink(missing_ok=True)
    print(f"  hatanaka -> {salida.name} "
          f"({salida.stat().st_size/1024:,.0f} KiB)")
    return salida


def main() -> int:
    ap = argparse.ArgumentParser(
        description="descarga BRDC/SP3/CLK reales para un dia dado")
    ap.add_argument("--date", required=True, help="dia UTC, formato YYYY-MM-DD")
    ap.add_argument("--dest", default="data/raw",
                    help="carpeta base de salida (default: data/raw)")
    ap.add_argument("--que", default="brdc,sp3",
                    help="que bajar, separado por comas: brdc,sp3,clk,obs "
                         "(default: brdc,sp3)")
    ap.add_argument("--estacion", default="LPGS00ARG",
                    help="estacion IGS para --que obs (default: LPGS00ARG)")
    args = ap.parse_args()

    d = datetime.strptime(args.date, "%Y-%m-%d").date()
    destino = Path(args.dest) / d.strftime("%Y") / d.strftime("%j")
    destino.mkdir(parents=True, exist_ok=True)
    print(f"dia {d} (DOY {d.strftime('%j')}, semana GPS {semana_gps(d)}) "
          f"-> {destino}/")

    pedidos = [p.strip().lower() for p in args.que.split(",") if p.strip()]
    resultados: dict[str, Path | None] = {}
    for p in pedidos:
        print(f"\n[{p}]")
        if p == "brdc":
            resultados[p] = traer_brdc(d, destino)
        elif p == "sp3":
            resultados[p] = traer_sp3(d, destino)
        elif p == "clk":
            resultados[p] = traer_clk(d, destino)
        elif p == "obs":
            resultados[p] = traer_obs(d, destino, args.estacion)
        else:
            print(f"  [aviso] no conozco '{p}' (opciones: brdc, sp3, clk, obs)")
            resultados[p] = None

    print("\n=== resumen ===")
    ok = True
    for p, ruta in resultados.items():
        estado = ruta.name if ruta else "FALTA"
        ok = ok and ruta is not None
        print(f"  {p:5s} -> {estado}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
