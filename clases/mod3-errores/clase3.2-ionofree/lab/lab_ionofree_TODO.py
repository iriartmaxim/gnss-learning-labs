# %% [markdown]
# # Lab 3.2 — La combinación iono-free con observables reales (TODO)
#
# En la 3.1 **modelaste** la ionosfera (Klobuchar). Acá la **medís**: con
# dos frecuencias, la divergencia P5−P1 aísla el retardo iono satélite por
# satélite. Después corrés el PVT en tres sabores — E1 crudo, E1+Klobuchar,
# iono-free — y descubrís el trade-off central de estimación: **sesgo vs
# ruido** (iono-free elimina el sesgo pero amplifica el ruido ×2.6).
#
# Reusa el motor de la 1.5 y el Klobuchar de la 3.1 por import.
# Correr desde la raíz del repo (georinex tarda ~2-3 min).

# %%
import sys
import warnings
from pathlib import Path

import numpy as np

warnings.filterwarnings("ignore")
RAIZ = Path.cwd()
sys.path.insert(0, str(RAIZ / "clases/mod1-posicionamiento/clase1.5-pvt/lab/soluciones"))
sys.path.insert(0, str(RAIZ / "clases/mod3-errores/clase3.1-ionosfera/lab/soluciones"))
from lab_pvt_solucion import (C, GAMMA, NAV, OBS, a_sow, ecef_a_geodetica,
                              elegir_efemeride, gauss_newton_pvt, matriz_enu,
                              pseudorango_corregido, registros_fnav,
                              POS_OFICIAL)
from lab_klobuchar_solucion import LAT, LON, klobuchar, leer_iono_header

# %% [markdown]
# ## Parte A — Medir la iono con la divergencia de código
#
# Los dos pseudorangos ven la MISMA geometría, relojes y troposfera, pero
# distinta ionosfera (I y γ·I con γ = (f₁/f₅)² ≈ 1.793):
#
# $$ P_5 - P_1 = (\gamma - 1)\,I_1 + c(\gamma-1)\,\mathrm{BGD} + \mathrm{DCB}_{rx} $$
#
# Despejá I₁ (el BGD del satélite viene en el F/NAV; el DCB del receptor
# queda como offset común a todos los satélites).

# %%
def registros_bgd(ds):
    """BGD(E1,E5a) [s] por satélite (registros F/NAV, DataSrc 258)."""
    out = {}
    for sv in ds.sv.values:
        base = str(sv).split("_")[0]
        sel = ds.sel(sv=sv).dropna(dim="time", how="all")
        for t in sel.time.values:
            fila = sel.sel(time=t)
            if int(fila["DataSrc"].values) == 258:
                out[base] = float(fila["BGDe5a"].values)
                break
    return out


def el_az(sat_ecef, rec_ecef):
    lat, lon, _ = ecef_a_geodetica(rec_ecef)
    e, n, u = matriz_enu(lat, lon) @ (sat_ecef - rec_ecef)
    return (np.degrees(np.arctan2(u, np.hypot(e, n))),
            np.degrees(np.arctan2(e, n)) % 360)


def iono_divergencia(p1, p5, bgd):
    """Retardo iono en E1 [m] medido con la divergencia de código."""
    return None    # TODO: (p5 - p1)/(GAMMA - 1) - C*bgd


# %% [markdown]
# ## Parte B — El PVT en tres sabores
#
# Completá las dos decisiones del sabor: qué observable usar (iono-free o
# P1) y qué corrección de reloj aplicar. Ojo: el reloj F/NAV está referido
# a la combinación E1/E5a, así que el usuario E1-only debe restarle c·BGD.

# %%
def resolver_flex(ep, t_rx, efs, bgd, ab, modo, cutoff_deg=10.0):
    crudos = []
    for sv in ep.sv.values:
        base = str(sv)
        p1, p5 = float(ep.sel(sv=sv)["C1X"]), float(ep.sel(sv=sv)["C5X"])
        if np.isnan(p1) or np.isnan(p5) or base not in efs or base not in bgd:
            continue
        ef = elegir_efemeride(efs[base], t_rx)
        if modo == "if":
            P = None       # TODO: la combinación iono-free de p1 y p5
            dbgd = 0.0
        else:
            P = p1
            dbgd = None    # TODO: la corrección BGD en metros (C * bgd)
        crudos.append((base, ef, P, dbgd))
    d1 = [pseudorango_corregido(ef, P, t_rx) for _, ef, P, _ in crudos]
    fix1, _, _ = gauss_newton_pvt(np.array([d[0] for d in d1]),
                                  np.array([d[1] - c4 for d, (_, _, _, c4)
                                            in zip(d1, crudos)]))
    datos = []
    for base, ef, P, dbgd in crudos:
        xyz, Pc, el = pseudorango_corregido(ef, P, t_rx, fix1[:3])
        eld, azd = el_az(xyz, fix1[:3])
        if eld < cutoff_deg:
            continue
        Pc = Pc - dbgd
        if modo == "e1klo":
            Pc = Pc - float(klobuchar(LAT, LON, eld, azd,
                                      t_rx % 86400.0, *ab))
        datos.append((xyz, Pc))
    fix2, res, _ = gauss_newton_pvt(np.array([d[0] for d in datos]),
                                    np.array([d[1] for d in datos]), fix1[:3])
    return fix2, res


def enu(fix_xyz):
    lat, lon, _ = ecef_a_geodetica(POS_OFICIAL)
    return matriz_enu(lat, lon) @ (fix_xyz - POS_OFICIAL)


# %%
import georinex as gr
co = leer_iono_header(NAV)
ab = (co["GPSA"], co["GPSB"])
print("cargando nav + obs (georinex, paciencia)...")
ds = gr.load(NAV, use="E")
efs, bgd = registros_fnav(ds), registros_bgd(ds)
obs = gr.load(OBS, use="E", tlim=("2026-06-15T12:00", "2026-06-15T12:20"))

ep, t_rx = obs.isel(time=0), a_sow(obs.time.values[0])
print("\niono medida vs Klobuchar (12:00 UTC):")
for sv in ep.sv.values:
    base = str(sv)
    p1, p5 = float(ep.sel(sv=base)["C1X"]), float(ep.sel(sv=base)["C5X"])
    if np.isnan(p1) or np.isnan(p5) or base not in bgd:
        continue
    print(f"  {base}: medida {iono_divergencia(p1, p5, bgd[base]):5.2f} m")

print("\nPVT tres sabores (20 min, cada 60 s):")
rms = {}
for modo in ("e1", "e1klo", "if"):
    errs = []
    for i in range(0, len(obs.time), 2):
        try:
            fx, _ = resolver_flex(obs.isel(time=i),
                                  a_sow(obs.time.values[i]), efs, bgd, ab, modo)
            errs.append(enu(fx[:3]))
        except Exception:
            pass
    rms[modo] = np.sqrt(np.mean(np.array(errs)**2, axis=0))
    print(f"  {modo:6s}: RMS E/N/U = {rms[modo][0]:.2f} / "
          f"{rms[modo][1]:.2f} / {rms[modo][2]:.2f} m")

# %% [markdown]
# ## Auto-test

# %%
k_teo = None    # TODO: sqrt((GAMMA/(GAMMA-1))**2 + (1/(GAMMA-1))**2)
assert abs(k_teo - 2.59) < 0.02, "el factor de amplificación de ruido"
assert rms["e1"][2] / rms["if"][2] > 1.5, "iono-free mejora la vertical"
assert rms["e1"][2] / rms["e1klo"][2] > 1.5, "Klobuchar también"
print(f"OK: iono medida y PVT en tres sabores — el ruido se paga ×{k_teo:.2f}")
