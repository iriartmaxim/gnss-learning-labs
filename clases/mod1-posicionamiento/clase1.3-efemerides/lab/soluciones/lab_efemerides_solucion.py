#!/usr/bin/env python3
"""Lab 1.3 — De la efemeride broadcast a la posicion ECEF (SOLUCION).

Parsea una efemeride Galileo REAL (BRDC 2026-06-15), propaga la orbita
segun el algoritmo del ICD y valida contra el SP3 preciso del mismo dia.
Correr desde la raiz del repo. Requiere: data/raw/2026/166 (clase 0.4).
"""
import numpy as np
import georinex as gr

MU = 3.986004418e14        # GM terrestre [m3/s2] (valor del ICD)
OMEGA_E = 7.2921151467e-5  # rotacion terrestre [rad/s]
NAV = "data/raw/2026/166/BRDC00IGS_R_20261660000_01D_MN.rnx"
SP3 = "data/raw/2026/166/COD0MGXFIN_20261660000_01D_05M_ORB.SP3"
CAMPOS = ["sqrtA", "Eccentricity", "M0", "DeltaN", "Omega0", "OmegaDot",
          "Io", "IDOT", "omega", "Cuc", "Cus", "Crc", "Crs", "Cic", "Cis",
          "Toe", "GALWeek", "DataSrc", "IODnav"]

print("cargando nav Galileo (georinex, ~1 min)...")
DS = gr.load(NAV, use="E")

# --- Parte A: aplanar registros y quedarse con I/NAV ---------------------
# DataSrc es un bitmask (RINEX 3.04): bit0=I/NAV E1-B, bit1=F/NAV E5a,
# bit2=I/NAV E5b, bit8/9=de que mensaje salen reloj y Toc.
# 517 = 512+4+1 -> I/NAV E1-B + E5b con reloj I/NAV: el mensaje que firma
# OSNMA (modulo 4). Nos quedamos SOLO con esos registros.
def registros_inav(ds):
    """dict sv_base -> lista de efemerides (dicts) con DataSrc==517."""
    out = {}
    for sv in ds.sv.values:
        base = str(sv).split("_")[0]
        sel = ds.sel(sv=sv).dropna(dim="time", how="all")
        for t in sel.time.values:
            fila = sel.sel(time=t)
            if int(fila["DataSrc"].values) != 517:
                continue
            ef = {k: float(fila[k].values) for k in CAMPOS}
            ef["epoca"] = t
            out.setdefault(base, []).append(ef)
    return out

def elegir_efemeride(efs, t_sow):
    """La efemeride del sv cuyo Toe este mas cerca de t_sow [s de semana]."""
    return min(efs, key=lambda e: abs(e["Toe"] - t_sow))

# --- Parte B: el algoritmo del ICD (Kepler -> ECEF) ----------------------
def kepler_a_ecef(ef, t_sow):
    """Posicion ECEF [m] del satelite en t_sow (segundos de semana GAL).

    Pasos del ICD (identicos en GPS IS-200 y Galileo OS SIS ICD):
      tiempo desde Toe -> anomalia media -> Kepler (Newton) -> verdadera
      -> argumento de latitud + correcciones armonicas -> radio e
      inclinacion corregidos -> plano orbital -> ECEF con Omega(t).
    """
    A = ef["sqrtA"] ** 2
    e = ef["Eccentricity"]
    tk = t_sow - ef["Toe"]
    # cruce de semana: tk debe caer en [-302400, 302400]
    if tk > 302400:
        tk -= 604800
    elif tk < -302400:
        tk += 604800

    n = np.sqrt(MU / A**3) + ef["DeltaN"]      # mov. medio corregido
    M = ef["M0"] + n * tk                       # anomalia media
    E = M                                       # Kepler por Newton
    for _ in range(30):
        dE = (M - (E - e * np.sin(E))) / (1 - e * np.cos(E))
        E += dE
        if abs(dE) < 1e-13:
            break
    nu = 2 * np.arctan2(np.sqrt(1 + e) * np.sin(E / 2),
                        np.sqrt(1 - e) * np.cos(E / 2))
    phi = nu + ef["omega"]                      # argumento de latitud
    s2, c2 = np.sin(2 * phi), np.cos(2 * phi)
    du = ef["Cus"] * s2 + ef["Cuc"] * c2        # correcciones armonicas
    dr = ef["Crs"] * s2 + ef["Crc"] * c2
    di = ef["Cis"] * s2 + ef["Cic"] * c2
    u = phi + du
    r = A * (1 - e * np.cos(E)) + dr
    i = ef["Io"] + ef["IDOT"] * tk + di
    xp, yp = r * np.cos(u), r * np.sin(u)       # plano orbital
    # ascension recta del nodo en ECEF (arrastra la rotacion terrestre)
    Om = (ef["Omega0"] + (ef["OmegaDot"] - OMEGA_E) * tk
          - OMEGA_E * ef["Toe"])
    x = xp * np.cos(Om) - yp * np.cos(i) * np.sin(Om)
    y = xp * np.sin(Om) + yp * np.cos(i) * np.cos(Om)
    z = yp * np.sin(i)
    return np.array([x, y, z])

# --- Parte C: parser SP3 propio (~25 lineas) -----------------------------
from datetime import datetime, timedelta

INICIO_SEMANA = datetime(2026, 6, 14)  # domingo 00:00 = semana GPS/GAL 2423

def a_sow(dt):
    """datetime -> segundos de la semana 2423 (GPS/GAL van sincronos)."""
    return (dt - INICIO_SEMANA).total_seconds()

def leer_sp3(ruta):
    """dict sv -> (array sow, array xyz[m]). Solo posiciones (lineas P)."""
    datos, t = {}, None
    with open(ruta) as f:
        for lin in f:
            if lin.startswith("%c") and "GPS" in lin:
                pass  # sistema de tiempo GPS confirmado en el header
            if lin.startswith("*"):
                c = lin.split()
                t = a_sow(datetime(int(c[1]), int(c[2]), int(c[3]),
                                   int(c[4]), int(c[5]), int(float(c[6]))))
            elif lin.startswith("P") and t is not None:
                sv = lin[1:4]
                xyz = np.array([float(lin[4:18]), float(lin[18:32]),
                                float(lin[32:46])]) * 1000.0  # km -> m
                datos.setdefault(sv, []).append((t, xyz))
    return {sv: (np.array([p[0] for p in v]),
                 np.vstack([p[1] for p in v])) for sv, v in datos.items()}

# --- Partes D-F: validacion contra el SP3 --------------------------------
if __name__ == "__main__":
    import json
    efs = registros_inav(DS)
    sp3 = leer_sp3(SP3)
    print(f"SVs con I/NAV en el nav: {len(efs)} | SVs Galileo en SP3: "
          f"{sum(1 for s in sp3 if s.startswith('E'))}")

    # D) un satelite al mediodia: broadcast vs preciso dentro del ajuste
    SV = "E19"
    t_obj = a_sow(datetime(2026, 6, 15, 12, 0))
    ef = elegir_efemeride(efs[SV], t_obj)
    print(f"\n[D] {SV}: Toe={ef['Toe']:.0f} s (IODnav {ef['IODnav']:.0f})")
    tt, xyz = sp3[SV]
    res = {}
    for ventana in (3600, 7200):
        m = np.abs(tt - ef["Toe"]) <= ventana
        err = np.array([np.linalg.norm(kepler_a_ecef(ef, t) - p)
                        for t, p in zip(tt[m], xyz[m])])
        res[ventana] = err
        print(f"    +-{ventana//3600} h: {m.sum()} epocas | RMS "
              f"{err.mean():.2f} m | max {err.max():.2f} m")
    assert res[3600].mean() < 10, "broadcast deberia ser metrico en +-1 h"

    # E) la misma efemeride envejecida: error vs |t - Toe|
    print("\n[E] degradacion fuera del intervalo de ajuste:")
    curva = []
    for t, p in zip(tt, xyz):
        dt_h = (t - ef["Toe"]) / 3600
        if abs(dt_h) <= 12:
            curva.append((dt_h, float(np.linalg.norm(kepler_a_ecef(ef, t) - p))))
    curva.sort()
    for h in (1, 2, 6, 12):
        e_h = [e for d, e in curva if abs(abs(d) - h) < 0.05]
        if e_h:
            print(f"    |dt|={h:2d} h -> {max(e_h):9.1f} m")

    # F) toda la constelacion, +-1 h alrededor del Toe de cada SV
    print("\n[F] RMS por satelite (+-1 h, efemeride del mediodia):")
    tabla = {}
    for sv in sorted(efs):
        if sv not in sp3:
            continue
        e = elegir_efemeride(efs[sv], t_obj)
        t2, x2 = sp3[sv]
        m = np.abs(t2 - e["Toe"]) <= 3600
        err = np.array([np.linalg.norm(kepler_a_ecef(e, t) - p)
                        for t, p in zip(t2[m], x2[m])])
        tabla[sv] = float(err.mean())
    med = float(np.median(list(tabla.values())))
    for sv, r in tabla.items():
        print(f"    {sv}: {r:6.2f} m" + ("  <- peor" if r == max(tabla.values()) else ""))
    print(f"    mediana constelacion: {med:.2f} m")
    assert med < 5, "la mediana de la constelacion deberia ser < 5 m"

    json.dump({"sv": SV, "toe": ef["Toe"], "curva": curva, "tabla": tabla},
              open("clases/mod1-posicionamiento/clase1.3-efemerides/data/resultados_1_3.json", "w"))
    print("\nLISTO: resultados guardados para las figuras")
