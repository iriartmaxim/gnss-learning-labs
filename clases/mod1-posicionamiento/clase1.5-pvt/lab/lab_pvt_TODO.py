# %% [markdown]
# # Lab 1.5 — Tu primer fix: PVT Galileo con datos reales (versión TODO)
#
# Con los pseudorangos E1/E5a de la estación LPGS (La Plata, IGS) y las
# efemérides broadcast del 2026-06-15 vas a calcular tu posición y
# compararla con la coordenada oficial. Prerequisito: datos de la 0.4 +
# el RINEX de observación (ver README, sección Datos).
# Correr desde la raíz del repo.

# %%
import numpy as np
import georinex as gr
from datetime import datetime

C = 299792458.0
MU = 3.986004418e14
OMEGA_E = 7.2921151467e-5
F1, F5 = 1575.42e6, 1176.45e6
GAMMA = None  # TODO: (F1/F5)**2 — el peso de la combinación iono-free
NAV = "data/raw/2026/166/BRDC00IGS_R_20261660000_01D_MN.rnx"
OBS = "data/raw/2026/166/LPGS00ARG_R_20261660000_01D_30S_MO.rnx"
POS_OFICIAL = np.array([2780102.9896, -4437418.9149, -3629404.5253])
INICIO_SEMANA = datetime(2026, 6, 14)
CAMPOS = ["sqrtA", "Eccentricity", "M0", "DeltaN", "Omega0", "OmegaDot",
          "Io", "IDOT", "omega", "Cuc", "Cus", "Crc", "Crs", "Cic", "Cis",
          "Toe", "DataSrc", "IODnav",
          "SVclockBias", "SVclockDrift", "SVclockDriftRate"]

def a_sow(t64):
    return float((t64 - np.datetime64(INICIO_SEMANA)) / np.timedelta64(1, "s"))

# %% [markdown]
# ## Parte A — Efemérides F/NAV
# Para la combinación E1/E5a el reloj correcto es el de **F/NAV**
# (¿qué valor de `DataSrc`? Pista: 256 + bit de F/NAV E5a).

# %%
FNAV = None  # TODO

def registros_fnav(ds):
    out = {}
    for sv in ds.sv.values:
        base = str(sv).split("_")[0]
        sel = ds.sel(sv=sv).dropna(dim="time", how="all")
        for t in sel.time.values:
            fila = sel.sel(time=t)
            if int(fila["DataSrc"].values) != FNAV:
                continue
            ef = {k: float(fila[k].values) for k in CAMPOS}
            ef["toc"] = a_sow(t)
            out.setdefault(base, []).append(ef)
    return out

def elegir_efemeride(efs, t_sow):
    return min(efs, key=lambda e: abs(e["Toe"] - t_sow))

# %% [markdown]
# ## Parte B — Órbita (copiá tu `kepler_a_ecef` de la 1.3) y reloj

# %%
def wrap_tk(dt):
    if dt > 302400:
        return dt - 604800
    if dt < -302400:
        return dt + 604800
    return dt

def kepler_E(ef, tk):
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

def kepler_a_ecef(ef, t_sow):
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
    dt = wrap_tk(t_sow - ef["toc"])
    poli = (ef["SVclockBias"] + ef["SVclockDrift"] * dt
            + ef["SVclockDriftRate"] * dt**2)
    E = kepler_E(ef, wrap_tk(t_sow - ef["Toe"]))
    rel = None  # TODO: -2*sqrt(MU*A)*e*sin(E)/C**2  (¿por qué es chica en Galileo?)
    return poli + rel

# %% [markdown]
# ## Parte C — Geometría local, tropo, Sagnac

# %%
def ecef_a_geodetica(p):
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
    lat, lon, h = ecef_a_geodetica(rec_ecef)
    enu = matriz_enu(lat, lon) @ (sat_ecef - rec_ecef)
    return np.arctan2(enu[2], np.hypot(enu[0], enu[1])), h

def tropo(el_rad, h):
    return None  # TODO: 2.3*exp(-h/7160)/sin(el)

def pseudorango_corregido(ef, P_if, t_rx_sow, rec_aprox=None):
    tau = P_if / C
    for _ in range(2):
        t_tx = t_rx_sow - tau
        xyz = kepler_a_ecef(ef, t_tx)
        tau = (np.linalg.norm(xyz - rec_aprox) / C
               if rec_aprox is not None else P_if / C)
    a = None  # TODO: el ángulo de Sagnac = OMEGA_E * tau
    rot = np.array([[np.cos(a), np.sin(a), 0],
                    [-np.sin(a), np.cos(a), 0],
                    [0, 0, 1]])
    xyz = rot @ xyz
    P = P_if + C * reloj_sat(ef, t_tx)
    if rec_aprox is None:
        return xyz, P, None
    el, h = el_y_h(xyz, rec_aprox)
    return xyz, P - tropo(el, h), el

# %% [markdown]
# ## Parte D — Gauss-Newton (tu solver de la 1.2, ahora con datos reales)

# %%
def gauss_newton_pvt(xyz_sats, pseudos, x0=np.zeros(3)):
    x = np.array([*x0, 0.0])
    for it in range(1, 15):
        dvec = xyz_sats - x[:3]
        rangos = np.linalg.norm(dvec, axis=1)
        res = pseudos - (rangos + x[3])
        J = None  # TODO: hstack de -dvec/rangos y una columna de unos
        dx = np.linalg.solve(J.T @ J, J.T @ res)
        x += dx
        if np.linalg.norm(dx[:3]) < 1e-4:
            break
    return x, res, it

def resolver_epoca(ep, t_rx, efs, cutoff_deg=10.0):
    crudos = []
    for sv in ep.sv.values:
        base = str(sv)
        p1, p5 = float(ep.sel(sv=sv)["C1X"]), float(ep.sel(sv=sv)["C5X"])
        if np.isnan(p1) or np.isnan(p5) or base not in efs:
            continue
        P_if = None  # TODO: (GAMMA*p1 - p5)/(GAMMA - 1)
        crudos.append((base, elegir_efemeride(efs[base], t_rx), P_if))
    datos = [pseudorango_corregido(ef, P, t_rx) for _, ef, P in crudos]
    fix1, _, _ = gauss_newton_pvt(np.array([d[0] for d in datos]),
                                  np.array([d[1] for d in datos]))
    datos2 = []
    for (base, ef, P) in crudos:
        xyz, Pc, el = pseudorango_corregido(ef, P, t_rx, fix1[:3])
        if np.degrees(el) >= cutoff_deg:
            datos2.append((xyz, Pc))
    fix2, res, _ = gauss_newton_pvt(np.array([d[0] for d in datos2]),
                                    np.array([d[1] for d in datos2]),
                                    fix1[:3])
    return fix2, res

# %%
# --- auto-test ---
efs = registros_fnav(gr.load(NAV, use="E"))
obs = gr.load(OBS, use="E", tlim=("2026-06-15T12:00", "2026-06-15T12:01"))
fix, res = resolver_epoca(obs.isel(time=0), a_sow(obs.time.values[0]), efs)
lat, lon, _ = ecef_a_geodetica(POS_OFICIAL)
enu = matriz_enu(lat, lon) @ (fix[:3] - POS_OFICIAL)
print(f"ENU = ({enu[0]:+.2f}, {enu[1]:+.2f}, {enu[2]:+.2f}) m | "
      f"3D = {np.linalg.norm(enu):.2f} m")
assert np.linalg.norm(enu) < 10, "el fix debería clavar < 10 m 3D"
print("OK (referencia: E=-0.21 N=+0.81 U=-1.76, 3D=1.95 m)")
