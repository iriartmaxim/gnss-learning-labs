"""Genera el escenario sintético de la clase 1.2.

5 satélites con geometría realista (az/el sobre Buenos Aires), receptor con
sesgo de reloj de +2.5 ms. Guarda posiciones ECEF, pseudodistancias limpias
y con ruido (sigma = 1 m), y la verdad de referencia para validar.

Uso: python generar_escenario.py   (escribe escenario_5sats.json en este dir)
"""
import json
import numpy as np

C = 299_792_458.0  # m/s

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
    """Vectores unitarios Este, Norte, Up en ECEF para un punto dado."""
    lat, lon = np.radians(lat_deg), np.radians(lon_deg)
    e = np.array([-np.sin(lon), np.cos(lon), 0.0])
    n = np.array([-np.sin(lat) * np.cos(lon), -np.sin(lat) * np.sin(lon), np.cos(lat)])
    u = np.array([np.cos(lat) * np.cos(lon), np.cos(lat) * np.sin(lon), np.sin(lat)])
    return e, n, u


def main():
    rng = np.random.default_rng(42)

    # Receptor: Buenos Aires
    lat, lon, h = -34.6037, -58.3816, 25.0
    r_rx = geodetic_to_ecef(lat, lon, h)
    e, n, u = enu_basis(lat, lon)

    # Sesgo de reloj del receptor (arranque en frío): +2.5 ms
    dt_rx = 2.5e-3  # s

    # Satélites: (azimut°, elevación°, distancia oblicua m) ~ shell MEO GPS
    sats_aer = [
        (30.0, 65.0, 20.6e6),
        (110.0, 40.0, 21.9e6),
        (200.0, 25.0, 23.3e6),
        (280.0, 50.0, 21.3e6),
        (340.0, 15.0, 24.3e6),
    ]
    sat_pos, ranges = [], []
    for az_deg, el_deg, d in sats_aer:
        az, el = np.radians(az_deg), np.radians(el_deg)
        los = (np.sin(az) * np.cos(el) * e
               + np.cos(az) * np.cos(el) * n
               + np.sin(el) * u)          # unitario receptor->satélite (ENU->ECEF)
        p = r_rx + d * los
        sat_pos.append(p)
        ranges.append(np.linalg.norm(p - r_rx))

    ranges = np.array(ranges)
    pr_clean = ranges + C * dt_rx
    pr_noisy = pr_clean + rng.normal(0.0, 1.0, size=len(ranges))

    out = {
        "descripcion": "Escenario clase 1.2: 5 satelites sinteticos, receptor en Buenos Aires con sesgo de reloj +2.5 ms",
        "c_m_s": C,
        "sat_ecef_m": [list(map(float, p)) for p in sat_pos],
        "sat_azel_deg": [[a, el] for a, el, _ in sats_aer],
        "pseudodistancias_m": list(map(float, pr_clean)),
        "pseudodistancias_ruido1m_m": list(map(float, pr_noisy)),
        "verdad": {
            "receptor_ecef_m": list(map(float, r_rx)),
            "receptor_geodetico": [lat, lon, h],
            "dt_receptor_s": dt_rx,
            "c_dt_receptor_m": C * dt_rx,
        },
    }
    with open("escenario_5sats.json", "w") as f:
        json.dump(out, f, indent=2)
    print("escenario_5sats.json escrito")
    print("c*dt =", C * dt_rx, "m  |  rangos [km]:", np.round(ranges / 1e3, 1))


if __name__ == "__main__":
    main()
