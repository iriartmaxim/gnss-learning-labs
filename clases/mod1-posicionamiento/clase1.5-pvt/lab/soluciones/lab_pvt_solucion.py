#!/usr/bin/env python3
"""Lab 1.5 — Tu primer fix: PVT Galileo con datos reales (SOLUCION).

Estacion LPGS (La Plata, IGS): pseudorangos E1/E5a del 2026-06-15,
efemerides broadcast F/NAV, correcciones de reloj/relatividad/Sagnac/
troposfera y Gauss-Newton. Validacion contra la coordenada oficial.
Correr desde la raiz del repo. Requiere data/raw/2026/166 (0.4 + obs).
"""
import numpy as np
import georinex as gr
from datetime import datetime

C = 299792458.0            # m/s
MU = 3.986004418e14
OMEGA_E = 7.2921151467e-5
F1, F5 = 1575.42e6, 1176.45e6
GAMMA = (F1 / F5) ** 2     # 1.7933: pesos de la combinacion iono-free
NAV = "data/raw/2026/166/BRDC00IGS_R_20261660000_01D_MN.rnx"
OBS = "data/raw/2026/166/LPGS00ARG_R_20261660000_01D_30S_MO.rnx"
POS_OFICIAL = np.array([2780102.9896, -4437418.9149, -3629404.5253])
INICIO_SEMANA = datetime(2026, 6, 14)   # domingo 00:00, semana 2423
CAMPOS = ["sqrtA", "Eccentricity", "M0", "DeltaN", "Omega0", "OmegaDot",
          "Io", "IDOT", "omega", "Cuc", "Cus", "Crc", "Crs", "Cic", "Cis",
          "Toe", "DataSrc", "IODnav",
          "SVclockBias", "SVclockDrift", "SVclockDriftRate"]

def a_sow(t64):
    """np.datetime64 -> segundos de la semana 2423."""
    return float((t64 - np.datetime64(INICIO_SEMANA)) / np.timedelta64(1, "s"))

# --- Parte A: efemerides F/NAV (el mensaje del usuario E1/E5a) -----------
# 258 = 256+2: F/NAV E5a, con reloj referido a la combinacion E1/E5a.
# Para nuestra iono-free E1/E5a es EL reloj correcto (sin BGD).
def registros_fnav(ds):
    out = {}
    for sv in ds.sv.values:
        base = str(sv).split("_")[0]
        sel = ds.sel(sv=sv).dropna(dim="time", how="all")
        for t in sel.time.values:
            fila = sel.sel(time=t)
            if int(fila["DataSrc"].values) != 258:
                continue
            ef = {k: float(fila[k].values) for k in CAMPOS}
            ef["toc"] = a_sow(t)   # el reloj se refiere a la epoca Toc
            out.setdefault(base, []).append(ef)
    return out

def elegir_efemeride(efs, t_sow):
    return min(efs, key=lambda e: abs(e["Toe"] - t_sow))

# --- Parte B: orbita (clase 1.3) + reloj del satelite --------------------
def kepler_E(ef, tk):
    """Anomalia excentrica por Newton (reusa la logica de 0.3/1.3)."""
    A = ef["sqrtA"] ** 2
    e = ef["Eccentricity"]
    n = np.sqrt(MU / A**3) + ef["DeltaN"]
    M = ef["M0"] + n * tk
    E = M
    for _ in range(30):
        dE = (M - (E - e * np.sin(E))) / (1 - e * np.cos(E))
        E += dE
        if abs(dE) < 1e-13:
            break
    return E

def wrap_tk(dt):
    if dt > 302400:
        return dt - 604800
    if dt < -302400:
        return dt + 604800
    return dt

def kepler_a_ecef(ef, t_sow):
    """Posicion ECEF [m] segun el ICD (identica a la clase 1.3)."""
    A = ef["sqrtA"] ** 2
    e = ef["Eccentricity"]
    tk = wrap_tk(t_sow - ef["Toe"])
    E = kepler_E(ef, tk)
    nu = 2 * np.arctan2(np.sqrt(1 + e) * np.sin(E / 2),
                        np.sqrt(1 - e) * np.cos(E / 2))
    phi = nu + ef["omega"]
    s2, c2 = np.sin(2 * phi), np.cos(2 * phi)
    u = phi + ef["Cus"] * s2 + ef["Cuc"] * c2
    r = A * (1 - e * np.cos(E)) + ef["Crs"] * s2 + ef["Crc"] * c2
    i = ef["Io"] + ef["IDOT"] * tk + ef["Cis"] * s2 + ef["Cic"] * c2
    xp, yp = r * np.cos(u), r * np.sin(u)
    Om = ef["Omega0"] + (ef["OmegaDot"] - OMEGA_E) * tk - OMEGA_E * ef["Toe"]
    return np.array([xp * np.cos(Om) - yp * np.cos(i) * np.sin(Om),
                     xp * np.sin(Om) + yp * np.cos(i) * np.cos(Om),
                     yp * np.sin(i)])

def reloj_sat(ef, t_sow):
    """Error del reloj del satelite [s]: polinomio F/NAV + relatividad.

    dt_rel = -2 sqrt(mu A) e sinE / c^2  (excentricidad de la orbita:
    el reloj late distinto en perigeo y apogeo; ~decenas de ns = metros).
    """
    dt = wrap_tk(t_sow - ef["toc"])
    poli = (ef["SVclockBias"] + ef["SVclockDrift"] * dt
            + ef["SVclockDriftRate"] * dt**2)
    E = kepler_E(ef, wrap_tk(t_sow - ef["Toe"]))
    rel = (-2 * np.sqrt(MU * ef["sqrtA"]**2) * ef["Eccentricity"]
           * np.sin(E)) / C**2
    return poli + rel

# --- Parte C: geometria local y troposfera -------------------------------
def ecef_a_geodetica(p):
    """ECEF -> (lat, lon, h) WGS-84 (iteracion clasica)."""
    a, f = 6378137.0, 1 / 298.257223563
    e2 = f * (2 - f)
    x, y, z = p
    lon = np.arctan2(y, x)
    rho = np.hypot(x, y)
    lat = np.arctan2(z, rho * (1 - e2))
    for _ in range(6):
        N = a / np.sqrt(1 - e2 * np.sin(lat)**2)
        h = rho / np.cos(lat) - N
        lat = np.arctan2(z, rho * (1 - e2 * N / (N + h)))
    return lat, lon, h

def matriz_enu(lat, lon):
    sl, cl = np.sin(lat), np.cos(lat)
    so, co = np.sin(lon), np.cos(lon)
    return np.array([[-so, co, 0],
                     [-sl * co, -sl * so, cl],
                     [cl * co, cl * so, sl]])

def el_y_h(sat_ecef, rec_ecef):
    """Elevacion del satelite y altura del receptor (para la tropo)."""
    lat, lon, h = ecef_a_geodetica(rec_ecef)
    enu = matriz_enu(lat, lon) @ (sat_ecef - rec_ecef)
    return np.arctan2(enu[2], np.hypot(enu[0], enu[1])), h

def tropo(el_rad, h):
    """Retardo troposferico [m]: ~2.3 m cenitales a nivel del mar, decae
    exponencial con la altura, mapeo 1/sin(el). Modelo minimo (Saastamoinen
    seco simplificado): suficiente a nivel metro."""
    return 2.3 * np.exp(-h / 7160.0) / np.sin(el_rad)

# --- Parte D: de la observacion al pseudorango corregido -----------------
def pseudorango_corregido(ef, P_if, t_rx_sow, rec_aprox=None):
    """(xyz_sat con Sagnac, pseudorango corregido, elevacion).

    Con rec_aprox=None NO aplica tropo ni calcula elevacion (pasada 1:
    todavia no sabemos donde estamos). Con rec_aprox (pasada 2) aplica
    tropo con la elevacion vista desde ese punto.
    """
    tau = P_if / C                      # tiempo de vuelo (~80 ms)
    for _ in range(2):                  # iterar: t_tx = t_rx - tau
        t_tx = t_rx_sow - tau
        xyz = kepler_a_ecef(ef, t_tx)
        rec = rec_aprox if rec_aprox is not None else np.zeros(3)
        tau = np.linalg.norm(xyz - rec) / C if rec_aprox is not None else P_if / C
    a = OMEGA_E * tau                   # Sagnac: la Tierra roto omega*tau
    rot = np.array([[np.cos(a), np.sin(a), 0],
                    [-np.sin(a), np.cos(a), 0],
                    [0, 0, 1]])
    xyz = rot @ xyz
    dt_sat = reloj_sat(ef, t_tx)        # el reloj del sat adelanta/atrasa
    P = P_if + C * dt_sat
    if rec_aprox is None:
        return xyz, P, None
    el, h = el_y_h(xyz, rec_aprox)
    return xyz, P - tropo(el, h), el

# --- Parte E: Gauss-Newton (la 1.2, ahora en serio) ----------------------
def gauss_newton_pvt(xyz_sats, pseudos, x0=np.zeros(3)):
    """Resuelve (x, y, z, c*dt_rx). Arranca del centro de la Tierra."""
    x = np.array([*x0, 0.0])
    for it in range(1, 15):
        d = xyz_sats - x[:3]
        rangos = np.linalg.norm(d, axis=1)
        res = pseudos - (rangos + x[3])
        J = np.hstack([-d / rangos[:, None], np.ones((len(pseudos), 1))])
        dx = np.linalg.solve(J.T @ J, J.T @ res)
        x += dx
        if np.linalg.norm(dx[:3]) < 1e-4:
            break
    return x, res, it

def resolver_epoca(ep, t_rx, efs, cutoff_deg=10.0):
    """Fix de una epoca en dos pasadas. Devuelve (fix, usados, it)."""
    crudos = []
    for sv in ep.sv.values:
        base = str(sv)
        p1, p5 = float(ep.sel(sv=sv)["C1X"]), float(ep.sel(sv=sv)["C5X"])
        if np.isnan(p1) or np.isnan(p5) or base not in efs:
            continue
        P_if = (GAMMA * p1 - p5) / (GAMMA - 1)   # iono-free E1/E5a
        crudos.append((base, elegir_efemeride(efs[base], t_rx), P_if))
    # pasada 1: sin tropo, desde el centro de la Tierra
    datos = [pseudorango_corregido(ef, P, t_rx) for _, ef, P in crudos]
    fix1, _, it1 = gauss_newton_pvt(np.array([d[0] for d in datos]),
                                    np.array([d[1] for d in datos]))
    # pasada 2: tropo + cutoff de elevacion, desde fix1
    datos2, usados = [], []
    for (base, ef, P) in crudos:
        xyz, Pc, el = pseudorango_corregido(ef, P, t_rx, fix1[:3])
        if np.degrees(el) >= cutoff_deg:
            datos2.append((xyz, Pc))
            usados.append((base, np.degrees(el)))
    fix2, res, it2 = gauss_newton_pvt(np.array([d[0] for d in datos2]),
                                      np.array([d[1] for d in datos2]),
                                      fix1[:3])
    return fix1, fix2, usados, res, (it1, it2)

def error_enu(fix_xyz):
    lat, lon, _ = ecef_a_geodetica(POS_OFICIAL)
    return matriz_enu(lat, lon) @ (fix_xyz - POS_OFICIAL)

# --- Main: fix, serie de 1 hora y cascada de correcciones ----------------
if __name__ == "__main__":
    import json
    print("cargando nav (georinex, ~1 min)...")
    efs = registros_fnav(gr.load(NAV, use="E"))
    print(f"SVs con F/NAV: {len(efs)}")
    print("cargando obs LPGS 12:00-13:00 (georinex)...")
    obs = gr.load(OBS, use="E", tlim=("2026-06-15T12:00", "2026-06-15T13:00"))
    print(f"epocas: {len(obs.time)}")

    # [E] una epoca con lupa: 12:00:00
    ep, t_rx = obs.isel(time=0), a_sow(obs.time.values[0])
    fix1, fix2, usados, res, (it1, it2) = resolver_epoca(ep, t_rx, efs)
    e1, e2 = error_enu(fix1[:3]), error_enu(fix2[:3])
    print(f"\n[E] 12:00 UTC | sats: {len(usados)} ->",
          " ".join(f"{s}({el:.0f}deg)" for s, el in usados))
    print(f"    pasada 1 (sin tropo, GN desde el centro de la Tierra, "
          f"{it1} it): E={e1[0]:+.2f} N={e1[1]:+.2f} U={e1[2]:+.2f} m")
    print(f"    pasada 2 (tropo + cutoff, {it2} it):        "
          f"E={e2[0]:+.2f} N={e2[1]:+.2f} U={e2[2]:+.2f} m "
          f"| 3D={np.linalg.norm(e2):.2f} m")
    print(f"    reloj receptor: {fix2[3]/C*1e6:+.3f} us ({fix2[3]:+.1f} m)"
          f" | residuos RMS {np.sqrt(np.mean(res**2)):.2f} m")
    assert np.linalg.norm(e2) < 10, "el fix deberia clavar <10 m 3D"
    assert abs(e2[2]) < abs(e1[2]), "la tropo debe achicar el sesgo vertical"

    # [F] serie 12:00-13:00
    serie = []
    for i in range(len(obs.time)):
        epi, ti = obs.isel(time=i), a_sow(obs.time.values[i])
        try:
            _, f2, us, _, _ = resolver_epoca(epi, ti, efs)
            serie.append([ti, *error_enu(f2[:3]), len(us)])
        except Exception:
            pass
    S = np.array(serie)
    rms = np.sqrt(np.mean(S[:, 1:4]**2, axis=0))
    print(f"\n[F] {len(S)} epocas | RMS E/N/U = "
          f"{rms[0]:.2f} / {rms[1]:.2f} / {rms[2]:.2f} m | "
          f"horizontal {np.hypot(rms[0], rms[1]):.2f} m | "
          f"3D {np.linalg.norm(rms):.2f} m")
    assert np.linalg.norm(rms) < 10

    # [G] cascada: que pasa si "olvido" cada correccion (epoca 12:00)
    casc = {"completo": float(np.linalg.norm(e2))}
    sin_rel = []
    for s, el in usados:
        ef = elegir_efemeride(efs[s], t_rx)
        P1 = float(ep.sel(sv=s)["C1X"]); P5 = float(ep.sel(sv=s)["C5X"])
        P = (GAMMA * P1 - P5) / (GAMMA - 1)
        xyz, Pc, _ = pseudorango_corregido(ef, P, t_rx, fix2[:3])
        tk = wrap_tk(t_rx - P/C - ef["Toe"])
        rel = (-2*np.sqrt(MU*ef["sqrtA"]**2)*ef["Eccentricity"]
               * np.sin(kepler_E(ef, tk))) / C**2
        sin_rel.append((xyz, Pc - C*rel))          # quito la relatividad
    fr, _, _ = gauss_newton_pvt(np.array([d[0] for d in sin_rel]),
                                np.array([d[1] for d in sin_rel]), fix2[:3])
    casc["sin_relatividad"] = float(np.linalg.norm(error_enu(fr[:3])))
    casc["sin_tropo"] = float(np.linalg.norm(e1))
    json.dump({"epoca": "2026-06-15T12:00", "usados": usados,
               "enu_12": [float(v) for v in e2], "serie": S.tolist(),
               "rms_enu": rms.tolist(), "cascada": casc},
              open("clases/mod1-posicionamiento/clase1.5-pvt/data/resultados_1_5.json", "w"))
    print(f"\n[G] 3D completo {casc['completo']:.2f} m | sin relatividad "
          f"{casc['sin_relatividad']:.2f} m | sin tropo {casc['sin_tropo']:.2f} m")
    print("\nLISTO: resultados guardados para las figuras")
