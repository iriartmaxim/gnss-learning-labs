# %% [markdown]
# # Lab 1.3 — De la efemeride broadcast a la posicion ECEF (version TODO)
#
# Vas a tomar una efemeride Galileo REAL (del BRDC que bajaste en la 0.4),
# propagar la orbita con el algoritmo del ICD y validar contra el SP3
# preciso del mismo dia. Prerequisito: haber corrido
# `python3 tools/fetch_data.py --date 2026-06-15 --que brdc,sp3`.
# Correr desde la raiz del repo.

# %%
import numpy as np
import georinex as gr
from datetime import datetime

MU = 3.986004418e14        # GM terrestre [m3/s2]
OMEGA_E = 7.2921151467e-5  # rotacion terrestre [rad/s]
NAV = "data/raw/2026/166/BRDC00IGS_R_20261660000_01D_MN.rnx"
SP3 = "data/raw/2026/166/COD0MGXFIN_20261660000_01D_05M_ORB.SP3"
CAMPOS = ["sqrtA", "Eccentricity", "M0", "DeltaN", "Omega0", "OmegaDot",
          "Io", "IDOT", "omega", "Cuc", "Cus", "Crc", "Crs", "Cic", "Cis",
          "Toe", "GALWeek", "DataSrc", "IODnav"]

print("cargando nav Galileo (georinex, ~1 min)...")
DS = gr.load(NAV, use="E")

# %% [markdown]
# ## Parte A — Filtrar I/NAV
# `DataSrc` es un bitmask (RINEX 3.04): bit0 = I/NAV E1-B, bit1 = F/NAV
# E5a, bit2 = I/NAV E5b; bits 8/9 dicen de que mensaje salen reloj y Toc.
# ¿Que valor entero corresponde a "I/NAV E1-B + E5b con reloj I/NAV"?
# (Ese es el mensaje que firma OSNMA en el modulo 4.)

# %%
INAV = None  # TODO: el valor del bitmask (pista: 512 + 4 + 1)

def registros_inav(ds):
    out = {}
    for sv in ds.sv.values:
        base = str(sv).split("_")[0]   # E02_1 -> E02 (mensajes duplicados)
        sel = ds.sel(sv=sv).dropna(dim="time", how="all")
        for t in sel.time.values:
            fila = sel.sel(time=t)
            if int(fila["DataSrc"].values) != INAV:
                continue
            ef = {k: float(fila[k].values) for k in CAMPOS}
            out.setdefault(base, []).append(ef)
    return out

def elegir_efemeride(efs, t_sow):
    return min(efs, key=lambda e: abs(e["Toe"] - t_sow))

# %% [markdown]
# ## Parte B — El algoritmo del ICD
# Completa los TODO siguiendo la cadena de la clase 0.3:
# tk -> n -> M -> Kepler(E) -> nu -> phi -> correcciones -> u, r, i ->
# plano orbital -> Omega(t) -> ECEF.

# %%
def kepler_a_ecef(ef, t_sow):
    A = ef["sqrtA"] ** 2
    e = ef["Eccentricity"]
    tk = t_sow - ef["Toe"]
    if tk > 302400:
        tk -= 604800
    elif tk < -302400:
        tk += 604800

    n = None    # TODO: sqrt(MU/A^3) + DeltaN
    M = None    # TODO: M0 + n*tk
    E = M
    for _ in range(30):
        dE = (M - (E - e * np.sin(E))) / (1 - e * np.cos(E))
        E += dE
        if abs(dE) < 1e-13:
            break
    nu = None   # TODO: 2*atan2(sqrt(1+e) sin(E/2), sqrt(1-e) cos(E/2))
    phi = nu + ef["omega"]
    s2, c2 = np.sin(2 * phi), np.cos(2 * phi)
    du = ef["Cus"] * s2 + ef["Cuc"] * c2
    dr = ef["Crs"] * s2 + ef["Crc"] * c2
    di = ef["Cis"] * s2 + ef["Cic"] * c2
    u = phi + du
    r = None    # TODO: A(1 - e cosE) + dr
    i = ef["Io"] + ef["IDOT"] * tk + di
    xp, yp = r * np.cos(u), r * np.sin(u)
    Om = None   # TODO: Omega0 + (OmegaDot - OMEGA_E)*tk - OMEGA_E*Toe
    x = xp * np.cos(Om) - yp * np.cos(i) * np.sin(Om)
    y = xp * np.sin(Om) + yp * np.cos(i) * np.cos(Om)
    z = yp * np.sin(i)
    return np.array([x, y, z])

# %% [markdown]
# ## Parte C — Leer el SP3 y comparar
# El SP3 esta en tiempo GPS (GAL y GPS van sincronos a nivel metrico).

# %%
INICIO_SEMANA = datetime(2026, 6, 14)  # domingo 00:00, semana 2423

def a_sow(dt):
    return (dt - INICIO_SEMANA).total_seconds()

def leer_sp3(ruta):
    datos, t = {}, None
    for lin in open(ruta):
        if lin.startswith("*"):
            c = lin.split()
            t = a_sow(datetime(int(c[1]), int(c[2]), int(c[3]),
                               int(c[4]), int(c[5]), int(float(c[6]))))
        elif lin.startswith("P") and t is not None:
            sv = lin[1:4]
            xyz = None  # TODO: 3 floats de 14 col (km) -> metros
            datos.setdefault(sv, []).append((t, xyz))
    return {sv: (np.array([p[0] for p in v]),
                 np.vstack([p[1] for p in v])) for sv, v in datos.items()}

# %%
# --- auto-test ---
efs = registros_inav(DS)
sp3 = leer_sp3(SP3)
assert len(efs) == 30, f"esperaba 30 SVs I/NAV, tengo {len(efs)}"
ef = elegir_efemeride(efs["E19"], a_sow(datetime(2026, 6, 15, 12, 0)))
tt, xyz = sp3["E19"]
m = np.abs(tt - ef["Toe"]) <= 3600
err = np.array([np.linalg.norm(kepler_a_ecef(ef, t) - p)
                for t, p in zip(tt[m], xyz[m])])
print(f"E19 +-1h: RMS {err.mean():.2f} m | max {err.max():.2f} m")
assert err.mean() < 10, "el broadcast deberia ser metrico en +-1 h"
print("OK (referencia: RMS 0.91 m, max 1.86 m)")
