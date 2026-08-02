#!/usr/bin/env python3
"""timescales.py — escalas de tiempo y marcos de referencia GNSS (SOLUCIÓN).

Conversiones entre TAI, UTC, GPST y GST, manejo de segundos intercalares
(leap seconds), GGTO GPS↔Galileo, semana/segundo-de-semana, y una rotación
mínima ECEF↔ECI. Incluye una batería de tests (asserts) al final.

Correr:  python3 timescales.py   → ejecuta los tests y termina en "TESTS OK".
"""
from __future__ import annotations

from datetime import datetime, timedelta

# --- constantes de las escalas ---------------------------------------------
GPS_EPOCH = datetime(1980, 1, 6)      # 1980-01-06 00:00:00 (GPST)
GST_EPOCH = datetime(1999, 8, 22)     # 1999-08-22 00:00:00 (GST)
TAI_MINUS_GPS = 19                    # s, constante: GPST = TAI − 19
OMEGA_E = 7.2921151467e-5             # rad/s, rotación terrestre

# Tabla histórica de segundos intercalares (UTC = TAI − ΔAT).
# (fecha de entrada en vigor, ΔAT acumulado). El último es de 2017-01-01.
LEAP_TABLE = [
    (datetime(1999, 1, 1), 32),
    (datetime(2006, 1, 1), 33),
    (datetime(2009, 1, 1), 34),
    (datetime(2012, 7, 1), 35),
    (datetime(2015, 7, 1), 36),
    (datetime(2017, 1, 1), 37),
]


def leap_seconds(utc: datetime) -> int:
    """ΔAT = TAI − UTC vigente en esa fecha UTC (segundos intercalares)."""
    dat = LEAP_TABLE[0][1]
    for fecha, val in LEAP_TABLE:
        if utc >= fecha:
            dat = val
    return dat


# --- conversiones entre escalas --------------------------------------------
def tai_from_utc(utc: datetime) -> datetime:
    return utc + timedelta(seconds=leap_seconds(utc))


def utc_from_tai(tai: datetime) -> datetime:
    # aproximación: el ΔAT cambia lento; se resuelve con la fecha aproximada
    return tai - timedelta(seconds=leap_seconds(tai))


def gps_from_tai(tai: datetime) -> datetime:
    return tai - timedelta(seconds=TAI_MINUS_GPS)


def tai_from_gps(gpst: datetime) -> datetime:
    return gpst + timedelta(seconds=TAI_MINUS_GPS)


def gps_from_utc(utc: datetime) -> datetime:
    """GPST = UTC + (ΔAT − 19). Hoy (ΔAT=37): GPST − UTC = 18 s."""
    return utc + timedelta(seconds=leap_seconds(utc) - TAI_MINUS_GPS)


def utc_from_gps(gpst: datetime) -> datetime:
    return gpst - timedelta(seconds=leap_seconds(gpst) - TAI_MINUS_GPS)


def gst_from_gps(gpst: datetime, ggto_ns: float = 0.0) -> datetime:
    """GST ≈ GPST salvo el GGTO (offset broadcast, nanosegundos).

    Nota: datetime tiene resolución de microsegundos; para GGTO a nivel ns
    conviene tratarlo como un offset float (ver ggto_segundos), no folderlo
    en un datetime. Acá se ofrece por completitud."""
    return gpst + timedelta(seconds=ggto_ns * 1e-9)


def ggto_segundos(ggto_ns: float) -> float:
    """GGTO en segundos (offset float): el GPS-Galileo Time Offset real es
    de nanosegundos y así se maneja en el observable, no en la fecha."""
    return ggto_ns * 1e-9


# --- semana / segundo de semana --------------------------------------------
def gps_week_sow(gpst: datetime):
    """(semana GPS, segundo de semana) de un instante GPST."""
    dt = gpst - GPS_EPOCH
    semana = dt.days // 7
    sow = (dt.days % 7) * 86400 + dt.seconds + dt.microseconds * 1e-6
    return semana, sow


def from_week_sow(semana: int, sow: float) -> datetime:
    return GPS_EPOCH + timedelta(weeks=semana, seconds=sow)


# --- marcos: rotación mínima ECEF <-> ECI ----------------------------------
def gmst_rad(utc: datetime) -> float:
    """Ángulo de rotación de la Tierra (aprox., rad) desde J2000."""
    j2000 = datetime(2000, 1, 1, 12)
    dias = (utc - j2000).total_seconds() / 86400.0
    return (4.894961 + OMEGA_E * 86400.0 * dias) % (2 * 3.141592653589793)


def eci_to_ecef(xyz_eci, utc: datetime):
    import numpy as np
    a = gmst_rad(utc)
    R = np.array([[np.cos(a), np.sin(a), 0],
                  [-np.sin(a), np.cos(a), 0], [0, 0, 1]])
    return R @ np.asarray(xyz_eci, float)


def ecef_to_eci(xyz_ecef, utc: datetime):
    import numpy as np
    a = gmst_rad(utc)
    R = np.array([[np.cos(a), -np.sin(a), 0],
                  [np.sin(a), np.cos(a), 0], [0, 0, 1]])
    return R @ np.asarray(xyz_ecef, float)


# --- tests -----------------------------------------------------------------
def tests():
    import numpy as np
    ok = 0

    # 1) leap seconds vigentes
    assert leap_seconds(datetime(2026, 6, 15)) == 37, "ΔAT 2026 debe ser 37"
    assert leap_seconds(datetime(2013, 1, 1)) == 35, "ΔAT 2013 debe ser 35"
    ok += 1

    # 2) GPST − UTC hoy = 18 s
    utc = datetime(2026, 6, 15, 12, 0, 0)
    dgps = (gps_from_utc(utc) - utc).total_seconds()
    assert dgps == 18, f"GPST−UTC debe ser 18 s, dio {dgps}"
    ok += 1

    # 3) GPST = TAI − 19 (constante, sin leaps)
    tai = tai_from_utc(utc)
    assert (tai - gps_from_tai(tai)).total_seconds() == 19
    ok += 1

    # 4) ida y vuelta UTC<->GPS
    assert utc_from_gps(gps_from_utc(utc)) == utc
    ok += 1

    # 5) semana/sow del día de referencia (2026-06-15 12:00 = semana 2423)
    sem, sow = gps_week_sow(gps_from_utc(utc))
    assert sem == 2423, f"semana esperada 2423, dio {sem}"
    # lunes 12:00 UTC → GPST 12:00:18 → sow = 1*86400 + 43218
    assert abs(sow - (86400 + 43218)) < 1e-6, f"sow inesperado: {sow}"
    ok += 1

    # 6) round-trip semana/sow
    t = from_week_sow(sem, sow)
    sem2, sow2 = gps_week_sow(t)
    assert sem2 == sem and abs(sow2 - sow) < 1e-6
    ok += 1

    # 7) GGTO: se maneja como offset float en ns (datetime solo llega a µs)
    assert abs(ggto_segundos(5.0) - 5e-9) < 1e-18, "GGTO 5 ns → 5e-9 s"
    ok += 1

    # 8) ECEF<->ECI es rotación (preserva la norma) e invertible
    r = np.array([2780102.99, -4437418.91, -3629404.53])
    r_eci = ecef_to_eci(r, utc)
    assert abs(np.linalg.norm(r_eci) - np.linalg.norm(r)) < 1e-6
    assert np.allclose(eci_to_ecef(r_eci, utc), r, atol=1e-6)
    ok += 1

    print(f"TESTS OK: {ok}/8 pasaron")
    return ok


if __name__ == "__main__":
    tests()
