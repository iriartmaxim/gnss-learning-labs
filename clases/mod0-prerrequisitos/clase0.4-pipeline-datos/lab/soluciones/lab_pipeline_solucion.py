#!/usr/bin/env python3
"""lab_pipeline_solucion.py — Clase 0.4: censo y cruce de los datos bajados.

Solución de referencia del lab. Uso (desde la raíz del repo):

    python3 clases/mod0-prerrequisitos/clase0.4-pipeline-datos/lab/soluciones/lab_pipeline_solucion.py [carpeta]

con carpeta = data/raw/2026/166 por defecto. Solo stdlib.
"""
import sys
from collections import Counter
from pathlib import Path

NOMBRES = {"G": "GPS", "E": "Galileo", "R": "GLONASS", "C": "BeiDou",
           "J": "QZSS", "I": "NavIC", "S": "SBAS"}


def censo_nav(nav: Path):
    """Censo del RINEX nav crudo: cuenta efemérides por constelación.

    Una efeméride = una línea de cabecera 'Xnn AAAA MM DD ...' (X en
    NOMBRES, nn dígitos). Devuelve (Counter por constelación, set de
    SV Galileo únicos, p. ej. {'E02', ...}).
    """
    con, sv_gal = Counter(), set()
    with open(nav) as f:
        for linea in f:
            if linea[:1] in NOMBRES and linea[1:3].isdigit():
                con[linea[0]] += 1
                if linea[0] == "E":
                    sv_gal.add(linea[:3])
    return con, sv_gal


def sats_sp3(sp3: Path):
    """Satélites declarados en las líneas '+ ' del header SP3 (cols 10–60,
    grupos de 3). Corta en '++' (ahí empiezan las precisiones)."""
    sats = []
    for linea in open(sp3):
        if linea.startswith("+ "):
            campo = linea[9:60]
            sats += [campo[i:i + 3] for i in range(0, len(campo), 3)]
        if linea.startswith("++"):
            break
    return [s for s in sats if s[:1] in NOMBRES]


def cruce_galileo(sv_gal_nav: set, sats_sp3_lista: list):
    """Intersección de los Galileo del nav con los del SP3."""
    gal_sp3 = {s for s in sats_sp3_lista if s[0] == "E"}
    return sv_gal_nav & gal_sp3, sv_gal_nav ^ gal_sp3


def main() -> int:
    carpeta = Path(sys.argv[1] if len(sys.argv) > 1 else "data/raw/2026/166")
    nav = next(carpeta.glob("BRDC*_MN.rnx"))
    sp3 = next(carpeta.glob("*ORB.SP3"))
    es_ref = carpeta.as_posix().rstrip("/").endswith("2026/166")

    # 1) censo nav
    con, sv_gal = censo_nav(nav)
    print(f"== {nav.name}")
    for c in sorted(con):
        print(f"  {NOMBRES[c]:8s} {con[c]:6d} efemerides")

    # 2) censo SP3
    sats = sats_sp3(sp3)
    csp3 = Counter(s[0] for s in sats)
    print(f"== {sp3.name}")
    print(f"  {len(sats)} satelites: "
          + ", ".join(f"{NOMBRES[c]} {n}" for c, n in sorted(csp3.items())))

    # 3) cruce nav vs SP3 (Galileo)
    inter, dif = cruce_galileo(sv_gal, sats)
    print(f"== cruce Galileo nav∩SP3: {len(inter)} en comun"
          + (f" | difieren: {sorted(dif)}" if dif else " | sin diferencias"))

    # 4) tasa de re-emision por satelite
    for c in ("G", "E"):
        n_sat = csp3.get(c, 0)
        if n_sat and con.get(c):
            tasa = con[c] / n_sat
            print(f"  {NOMBRES[c]:8s} {con[c]:6d} efem / {n_sat} sat "
                  f"= {tasa:6.1f} por sat/dia (una cada {1440/tasa:4.0f} min)")

    if es_ref:
        assert con["G"] == 450, f"GPS: {con['G']} != 450"
        assert con["E"] == 11119, f"Galileo: {con['E']} != 11119"
        assert con["C"] == 901, f"BeiDou: {con['C']} != 901"
        assert len(sats) == 116, f"SP3: {len(sats)} != 116"
        assert len(inter) == 30 and not dif, f"cruce: {len(inter)}, dif {sorted(dif)}"
        print("VALIDACION 2026/166: OK (450 / 11119 / 901 / 116 / 30∩30)")
    print("LISTO: pipeline 0.4 verificado")
    return 0


if __name__ == "__main__":
    sys.exit(main())
