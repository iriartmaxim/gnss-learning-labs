# %% [markdown]
# # Lab 3.3 — Troposfera: Saastamoinen y el error que no se resta (TODO)
#
# La ionosfera se pudo **eliminar** (3.2) porque es dispersiva. La
# troposfera no: es gas neutro y retrasa igual en cualquier frecuencia de
# banda L — la doble frecuencia no la ve. La única defensa es **modelarla**,
# y la buena noticia es que se deja: el 96% es hidrostático (exacto con la
# presión) y solo el vapor de agua (~dm) es rebelde.
#
# Acá implementás Saastamoinen (ZHD + ZWD), lo comparás con el modelo
# mínimo de la 1.5, y lo **inyectás** en el motor PVT para medir cuánto
# vale cada troposfera en la vertical.
#
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
sys.path.insert(0, str(RAIZ / "clases/mod3-errores/clase3.2-ionofree/lab/soluciones"))
import lab_pvt_solucion as pvt
from lab_pvt_solucion import NAV, OBS, POS_OFICIAL, a_sow, ecef_a_geodetica
from lab_klobuchar_solucion import leer_iono_header
from lab_ionofree_solucion import enu, registros_bgd, resolver_flex

T_K, RH = 283.15, 0.70          # invierno en La Plata: 10 C, 70% RH

# %% [markdown]
# ## Parte A — El modelo Saastamoinen
#
# **ZHD** (hidrostático): la columna de aire seco integrada ES la presión
# en superficie dividida por g — por eso con P medida es exacto a ~1 mm:
#
# $$ \mathrm{ZHD} = \frac{0.0022768\,P}{1 - 0.00266\cos(2\varphi) - 0.00028\,h_{km}} $$
#
# **ZWD** (húmedo): el vapor no está en equilibrio hidrostático — esta es
# la parte difícil (~cm de error):
#
# $$ \mathrm{ZWD} = 0.002277\left(\frac{1255}{T} + 0.05\right) e $$

# %%
def presion_isa(h_m):
    return 1013.25 * (1 - 2.2557e-5 * h_m) ** 5.2568


def es_agua(T_K):
    Tc = T_K - 273.15
    return 6.11 * np.exp(17.27 * Tc / (237.3 + Tc))


def saastamoinen_zhd(P_hPa, lat_deg, h_m):
    den = None    # TODO: 1 - 0.00266*cos(2*lat) - 0.00028e-3*h
    return None   # TODO: 0.0022768 * P / den


def saastamoinen_zwd(T_K, e_hPa):
    return None   # TODO: 0.002277 * (1255/T + 0.05) * e


def mapeo_simple(el_rad):
    return None   # TODO: 1/sin(el)


def tropo_saastamoinen(el_rad, h):
    """Retardo oblicuo [m] — misma firma que pvt.tropo (para inyectar)."""
    P = presion_isa(h)
    e = RH * es_agua(T_K)
    lat = np.degrees(np.arctan2(POS_OFICIAL[2],
                                np.hypot(POS_OFICIAL[0], POS_OFICIAL[1])))
    return (saastamoinen_zhd(P, lat, h) + saastamoinen_zwd(T_K, e)) \
        * mapeo_simple(el_rad)


# %%
lat, lon, h = ecef_a_geodetica(POS_OFICIAL)
P = presion_isa(h)
e = RH * es_agua(T_K)
zhd = saastamoinen_zhd(P, np.degrees(lat), h)
zwd = saastamoinen_zwd(T_K, e)
print(f"h = {h:.1f} m | P = {P:.1f} hPa | e = {e:.2f} hPa")
print(f"ZHD = {zhd:.4f} m | ZWD = {zwd:.4f} m | cenital = {zhd+zwd:.4f} m")
for el in (90, 30, 15, 5):
    print(f"  elev {el:2d} -> oblicuo {(zhd+zwd)*mapeo_simple(np.radians(el)):6.2f} m")

# %% [markdown]
# ## Parte B — Inyectar el modelo en el PVT
#
# `pseudorango_corregido` (1.5) llama a `tropo(el, h)` de su módulo:
# reemplazando `pvt.tropo` cambiás la troposfera de TODO el motor sin
# tocar una línea — el patrón de inyección de dependencias. Corré el fix
# iono-free con tres troposferas y mirá la vertical.

# %%
import georinex as gr
co = leer_iono_header(NAV)
ab = (co["GPSA"], co["GPSB"])
print("cargando nav + obs (paciencia)...")
ds = gr.load(NAV, use="E")
efs, bgd = pvt.registros_fnav(ds), registros_bgd(ds)
obs = gr.load(OBS, use="E", tlim=("2026-06-15T12:00", "2026-06-15T12:20"))

tropo_original = pvt.tropo
sabores = {"sin": lambda el, hh: 0.0,
           "min": tropo_original,
           "saas": tropo_saastamoinen}
rms = {}
for k, f in sabores.items():
    pvt.tropo = f
    errs = []
    for i in range(0, len(obs.time), 2):
        try:
            fx, _, _ = resolver_flex(obs.isel(time=i),
                                     a_sow(obs.time.values[i]),
                                     efs, bgd, ab, "if")
            errs.append(enu(fx[:3]))
        except Exception:
            pass
    rms[k] = np.sqrt(np.mean(np.array(errs)**2, axis=0))
    print(f"  {k:5s}: RMS E/N/U = {rms[k][0]:.2f} / {rms[k][1]:.2f} / "
          f"{rms[k][2]:.2f} m")
pvt.tropo = tropo_original

# %% [markdown]
# ## Auto-test

# %%
assert 2.25 < zhd < 2.35, "ZHD a nivel del mar ~2.3 m"
assert 0.04 < zwd < 0.20, "ZWD de invierno ~dm"
assert abs(float(mapeo_simple(np.radians(5))) - 11.47) < 0.05
assert rms["sin"][2] / rms["min"][2] > 3, "sin tropo la vertical explota"
assert abs(rms["saas"][2] - rms["min"][2]) < 0.5, "Saastamoinen ~ mínimo"
print("OK: la tropo es grande pero mansa — un buen modelo la doma")
