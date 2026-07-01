"""Genera el escenario sintético de la clase 1.1 (trilateración pura).

Dos sets de 4 balizas sobre Buenos Aires: geometría "buena" (repartida en el
cielo) y "mala" (agrupada en un cono de ~30°). Rangos EXACTOS (sin reloj:
esto es trilateración, no pseudodistancia) y con ruido sigma = 1 m.

Uso: python generar_escenario_trilat.py   (escribe escenario_trilat.json)
"""
import json
import numpy as np

# --- WGS84: geodésicas -> ECEF -------------------------------------------
A_WGS84 = 6_378_137.0
F_WGS84 = 1.0 / 298.257223563
E2 = F_WGS84 * (2 - F_WGS84)


def geodetic_to_ecef(lat_deg, lon_deg, h):
    lat, lon = np.radians(lat_deg), np.radians(lon_deg)
    N = A_WGS84 / np.sqrt(1 - E2 * np.sin(lat) ** 2)
    x = (N + h) * np.cos(lat) * np.cos(lon)
    y = (N + h) * np.cos(lat) * np.sin(lon)
    z = (N * (1 - E2) + h) * np.sin(lat)
    return np.array([x, y, z])


def enu_basis(lat_deg, lon_deg):
    lat, lon = np.radians(lat_deg), np.radians(lon_deg)
    e = np.array([-np.sin(lon), np.cos(lon), 0.0])
    n = np.array([-np.sin(lat) * np.cos(lon), -np.sin(lat) * np.sin(lon), np.cos(lat)])
    u = np.array([np.cos(lat) * np.cos(lon), np.cos(lat) * np.sin(lon), np.sin(lat)])
    return e, n, u


def balizas_desde_azel(r_rx, e, n, u, lista_aer):
    pos = []
    for az_deg, el_deg, d in lista_aer:
        az, el = np.radians(az_deg), np.radians(el_deg)
        los = (np.sin(az) * np.cos(el) * e
               + np.cos(az) * np.cos(el) * n
               + np.sin(el) * u)
        pos.append(r_rx + d * los)
    return np.array(pos)


def main():
    rng = np.random.default_rng(42)
    lat, lon, h = -34.6037, -58.3816, 25.0
    r_rx = geodetic_to_ecef(lat, lon, h)
    e, n, u = enu_basis(lat, lon)

    # geometría BUENA: repartida en azimut y elevación
    buenas_aer = [(45.0, 60.0, 20.8e6), (135.0, 35.0, 22.4e6),
                  (225.0, 45.0, 21.6e6), (315.0, 20.0, 23.9e6)]
    # geometría MALA: las 4 balizas en un cono de ~30 grados
    malas_aer = [(40.0, 50.0, 21.3e6), (55.0, 45.0, 21.7e6),
                 (70.0, 40.0, 22.0e6), (50.0, 55.0, 21.1e6)]

    buenas = balizas_desde_azel(r_rx, e, n, u, buenas_aer)
    malas = balizas_desde_azel(r_rx, e, n, u, malas_aer)
    rg_b = np.linalg.norm(buenas - r_rx, axis=1)
    rg_m = np.linalg.norm(malas - r_rx, axis=1)

    out = {
        "descripcion": "Escenario clase 1.1: trilateracion pura (rangos exactos, sin reloj), receptor en Buenos Aires",
        "balizas_buenas_ecef_m": buenas.tolist(),
        "balizas_buenas_azel": [[a, el] for a, el, _ in buenas_aer],
        "balizas_malas_ecef_m": malas.tolist(),
        "balizas_malas_azel": [[a, el] for a, el, _ in malas_aer],
        "rangos_buenas_m": rg_b.tolist(),
        "rangos_buenas_ruido1m_m": (rg_b + rng.normal(0, 1.0, 4)).tolist(),
        "rangos_malas_m": rg_m.tolist(),
        "rangos_malas_ruido1m_m": (rg_m + rng.normal(0, 1.0, 4)).tolist(),
        "verdad": {"receptor_ecef_m": r_rx.tolist(),
                   "receptor_geodetico": [lat, lon, h]},
    }
    with open("escenario_trilat.json", "w") as f:
        json.dump(out, f, indent=2)
    print("escenario_trilat.json escrito | rangos buenas [km]:",
          np.round(rg_b / 1e3, 1))


if __name__ == "__main__":
    main()
