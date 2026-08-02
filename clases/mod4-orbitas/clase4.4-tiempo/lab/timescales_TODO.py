# %% [markdown]
# # Lab 4.4 — timescales.py: escalas de tiempo y marcos (ESQUELETO)
#
# Completá los TODO y corré: los tests (asserts) validan tus conversiones.
# Referencia completa en lab/soluciones/timescales.py.
#
#     python3 clases/mod4-orbitas/clase4.4-tiempo/lab/timescales_TODO.py

# %%
from datetime import datetime, timedelta
GPS_EPOCH = datetime(1980, 1, 6)
TAI_MINUS_GPS = 19
LEAP_TABLE = [(datetime(1999,1,1),32),(datetime(2006,1,1),33),(datetime(2009,1,1),34),
              (datetime(2012,7,1),35),(datetime(2015,7,1),36),(datetime(2017,1,1),37)]

# %% [markdown]
# ## TODO 1 — segundos intercalares vigentes (ΔAT = TAI − UTC)
# Devolvé el último valor de la tabla cuya fecha sea <= utc.

# %%
def leap_seconds(utc):
    dat = LEAP_TABLE[0][1]
    # TODO 1: recorré LEAP_TABLE y quedate con el último val cuya fecha <= utc
    ...
    return dat

# %% [markdown]
# ## TODO 2 — GPST desde UTC
# GPST = UTC + (ΔAT − 19). Hoy (ΔAT=37) da +18 s.

# %%
def gps_from_utc(utc):
    # TODO 2: return utc + timedelta(seconds=leap_seconds(utc) - TAI_MINUS_GPS)
    ...

# %% [markdown]
# ## TODO 3 — semana y segundo de semana GPS

# %%
def gps_week_sow(gpst):
    dt = gpst - GPS_EPOCH
    # TODO 3: semana = dt.days // 7 ; sow = (dt.days % 7)*86400 + dt.seconds
    ...
    return semana, sow

# %%
utc = datetime(2026, 6, 15, 12, 0, 0)
assert leap_seconds(utc) == 37
assert (gps_from_utc(utc) - utc).total_seconds() == 18
sem, sow = gps_week_sow(gps_from_utc(utc))
assert sem == 2423 and abs(sow - (86400 + 43218)) < 1e-6
print(f"semana {sem}, sow {sow:.0f} — TESTS OK")
print("LISTO: timescales 4.4")
