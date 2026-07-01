"""Genera el escenario sintético de la clase 1.4 (DOP y geometría).

10 satélites sobre Buenos Aires con azimut/elevación repartidos (incluye
bajos para jugar con la máscara de elevación). La distancia oblicua se
calcula con la geometría de una capa orbital de radio R = 26 560 km:

    d(el) = sqrt(R^2 - (Re*cos el)^2) - Re*sin el

Pseudodistancias con el mismo sesgo de reloj de la clase 1.2 (+2.5 ms)
y versión con ruido sigma = 1 m.

Uso: python generar_escenario_10sats.py   (escribe escenario_10sats.json)
"""
import json
import numpy as np

C_LUZ = 299_792_458.0
R_ORBITA = 26_560e3   # radio geocéntrico de la capa (tipo GPS/Galileo)
RE = 6_378e3

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


def distancia_oblicua(el_deg):
    el = np.radians(el_deg)
    return np.sqrt(R_ORBITA**2 - (RE * np.cos(el)) ** 2) - RE * np.sin(el)


def main():
    rng = np.random.default_rng(7)
    lat, lon, h = -34.6037, -58.3816, 25.0
    r_rx = geodetic_to_ecef(lat, lon, h)
    e, n, u = enu_basis(lat, lon)

    azel = [(20.0, 75.0), (80.0, 55.0), (140.0, 40.0), (200.0, 30.0),
            (260.0, 50.0), (320.0, 15.0), (50.0, 25.0), (110.0, 10.0),
            (230.0, 65.0), (300.0, 35.0)]

    sats = []
    for az_deg, el_deg in azel:
        az, el = np.radians(az_deg), np.radians(el_deg)
        los = (np.sin(az) * np.cos(el) * e
               + np.cos(az) * np.cos(el) * n
               + np.sin(el) * u)
        sats.append(r_rx + distancia_oblicua(el_deg) * los)
    sats = np.array(sats)

    dt_rx = 2.5e-3                       # mismo sesgo que la clase 1.2
    rho = np.linalg.norm(sats - r_rx, axis=1)
    pr = rho + C_LUZ * dt_rx

    out = {
        "descripcion": "Escenario clase 1.4: 10 satelites sobre Buenos Aires para DOP (mascaras, subconjuntos, Monte Carlo)",
        "sat_ecef_m": sats.tolist(),
        "sat_azel_deg": [list(p) for p in azel],
        "pseudodistancias_m": pr.tolist(),
        "pseudodistancias_ruido1m_m": (pr + rng.normal(0, 1.0, len(azel))).tolist(),
        "verdad": {"receptor_ecef_m": r_rx.tolist(),
                   "receptor_geodetico": [lat, lon, h],
                   "sesgo_reloj_s": dt_rx,
                   "c_dt_m": C_LUZ * dt_rx},
    }
    with open("escenario_10sats.json", "w") as f:
        json.dump(out, f, indent=2)
    print("escenario_10sats.json escrito | elevaciones:",
          sorted(el for _, el in azel))


if __name__ == "__main__":
    main()
