# %% [markdown]
# # Lab 3.1 — Ionosfera broadcast: Klobuchar y NeQuick-G (TODO)
#
# En la 1.5 eliminaste la ionosfera con la combinación iono-free (dos
# frecuencias). Pero la mayoría de los receptores del mundo usan UNA
# frecuencia: su única defensa es un **modelo broadcast**. GPS transmite
# 8 coeficientes (Klobuchar, corrige ~50% RMS); Galileo transmite 3
# (NeQuick-G, ~70%). Acá implementás Klobuchar completo según IS-GPS-200
# con los coeficientes REALES del día 166/2026 — el mismo BRDC de la 1.5 —
# y estimás cuánto error ionosférico tenían los 8 satélites de tu PVT.
#
# Correr desde la raíz del repo.

# %%
import json
import re
from pathlib import Path

import numpy as np

C = 299_792_458.0
BRDC = Path("data/raw/2026/166/BRDC00IGS_R_20261660000_01D_MN.rnx")
LAT, LON = -34.907, -57.932          # LPGS (La Plata)

# %% [markdown]
# ## Parte A — Leer los coeficientes del header RINEX
#
# El header del BRDC trae líneas `IONOSPHERIC CORR`:
# ```
# GPSA   1.1176E-08  2.2352E-08 ...   (alpha de Klobuchar)
# GPSB   1.0240E+05  1.4746E+05 ...   (beta de Klobuchar)
# GAL    1.2650E+02  4.6484E-01 ...   (ai0-2 de NeQuick-G)
# ```

# %%
def leer_iono_header(ruta=BRDC):
    out = {}
    with open(ruta) as f:
        for linea in f:
            if "END OF HEADER" in linea:
                break
            if "IONOSPHERIC CORR" not in linea:
                continue
            clave = linea[:4].strip()
            if clave in ("GPSA", "GPSB", "GAL"):
                # TODO: extraer los floats con re.findall y guardarlos
                out[clave] = None
    return out


# %% [markdown]
# ## Parte B — Klobuchar (IS-GPS-200 §20.3.3.5.2.5)
#
# El modelo: un **coseno diurno** de amplitud AMP y período PER (ambos
# polinomios cúbicos en la latitud geomagnética del punto de perforación),
# con el pico clavado a las **14:00 hora local** y un piso nocturno de
# **5 ns**. Un factor de **oblicuidad** F mapea el retardo vertical al
# oblicuo. Todo en semicírculos (grados/180).

# %%
def klobuchar(lat_deg, lon_deg, elev_deg, azim_deg, t_sod, alpha, beta):
    phi_u = lat_deg / 180.0
    lam_u = lon_deg / 180.0
    E = np.asarray(elev_deg) / 180.0
    A = np.radians(azim_deg)

    # 1) ángulo central Tierra->IPP:  psi = 0.0137/(E+0.11) - 0.022
    psi = None            # TODO
    # 2) latitud del IPP (clamp a +-0.416)
    phi_i = None          # TODO: np.clip(phi_u + psi*cos(A), ...)
    # 3) longitud del IPP
    lam_i = None          # TODO: lam_u + psi*sin(A)/cos(phi_i*pi)
    # 4) latitud geomagnética
    phi_m = None          # TODO: phi_i + 0.064*cos((lam_i - 1.617)*pi)
    # 5) hora local del IPP (segundos)
    t = None              # TODO: (4.32e4*lam_i + t_sod) % 86400
    # 6) amplitud (polinomio en phi_m, >= 0)
    AMP = None            # TODO
    # 7) período (polinomio en phi_m, >= 72000)
    PER = None            # TODO
    # 8) fase (pico en 50400 s = 14:00)
    x = None              # TODO: 2*pi*(t - 50400)/PER
    # 9) oblicuidad
    F = None              # TODO: 1 + 16*(0.53 - E)**3
    # 10) retardo (s): de día coseno truncado, de noche 5 ns
    noche = 5e-9
    dia = noche + AMP * (1 - x**2 / 2 + x**4 / 24)
    T = np.where(np.abs(x) < 1.57, F * dia, F * noche)
    return T * C          # metros


def oblicuidad(elev_deg):
    E = np.asarray(elev_deg) / 180.0
    return None           # TODO


# %% [markdown]
# ## Parte C — Aplicalo a TU PVT de la 1.5
#
# El JSON de la 1.5 guarda los 8 Galileo usados y sus elevaciones. Estimá
# el retardo oblicuo de cada uno a las 12:00 UTC — el error que la
# combinación iono-free eliminó por construcción.

# %%
co = leer_iono_header()
alpha, beta = co["GPSA"], co["GPSB"]
print("alpha:", alpha, "\nbeta:", beta)

# curva diurna en el cenit
horas = np.arange(0, 24.01, 0.25)
cen = np.array([klobuchar(LAT, LON, 90, 0, h * 3600, alpha, beta)
                for h in horas])
h_pico_loc = (horas[np.argmax(cen)] + LON / 15.0) % 24
print(f"piso nocturno {cen.min():.2f} m | pico {cen.max():.2f} m "
      f"a las {h_pico_loc:.1f} hora local")

res15 = json.load(open("clases/mod1-posicionamiento/clase1.5-pvt/"
                       "data/resultados_1_5.json"))
for sv, elev in res15["usados"]:
    d = float(klobuchar(LAT, LON, elev, 0, 12 * 3600, alpha, beta))
    print(f"  {sv}  elev {elev:5.1f} -> iono ~ {d:5.2f} m")

# %% [markdown]
# ## Auto-test

# %%
assert abs(cen.min() - 5e-9 * C) < 0.01, "piso nocturno debe ser 5 ns x c"
assert abs(h_pico_loc - 14.0) < 0.4, "el pico de Klobuchar es a las 14 locales"
assert abs(float(oblicuidad(90)) - 1.0) < 0.01, "F(90) = 1"
assert 2.9 < float(oblicuidad(5)) < 3.2, "F(5 grados) ~ 3"
print("OK: Klobuchar validado con los coeficientes reales del broadcast")
