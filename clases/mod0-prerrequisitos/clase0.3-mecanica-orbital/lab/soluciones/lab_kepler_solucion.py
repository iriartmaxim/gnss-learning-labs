"""Clase 0.3 — SOLUCIÓN: mecánica orbital mínima para leer una efeméride.

Ecuación de Kepler por Newton, cadena de anomalías M -> E -> nu, periodos y
velocidades de las órbitas que importan, tercera ley, y regresión nodal por
J2 (el número que explica por qué las efemérides traen OMEGA_DOT).

Uso: python lab_kepler_solucion.py   (desde lab/soluciones/)
"""
import numpy as np

MU = 3.986004418e14        # parámetro gravitacional terrestre [m^3/s^2]
RE = 6_378_137.0           # radio ecuatorial [m]
J2 = 1.08263e-3            # achatamiento dinámico
OMEGA_E = 7.2921151467e-5  # rotación terrestre [rad/s]


def kepler_newton(M, e, tol=1e-12, max_iter=30):
    """Resuelve E - e*sin(E) = M por Newton. Devuelve (E, iteraciones)."""
    E = M if e < 0.8 else np.pi
    for k in range(1, max_iter + 1):
        f = E - e * np.sin(E) - M
        fp = 1.0 - e * np.cos(E)
        dE = f / fp
        E = E - dE
        if abs(dE) < tol:
            return E, k
    raise RuntimeError("Kepler no convergió")


def anomalia_verdadera(E, e):
    return 2.0 * np.arctan2(np.sqrt(1 + e) * np.sin(E / 2),
                            np.sqrt(1 - e) * np.cos(E / 2))


def periodo(a):
    return 2 * np.pi * np.sqrt(a**3 / MU)


def vel_circular(a):
    return np.sqrt(MU / a)


def regresion_nodal_J2(a, e, i_rad):
    """OMEGA_dot por J2 [rad/s]: -(3/2) J2 (Re/p)^2 n cos(i)."""
    n = np.sqrt(MU / a**3)
    p = a * (1 - e**2)
    return -1.5 * J2 * (RE / p) ** 2 * n * np.cos(i_rad)


if __name__ == "__main__":
    print("=== Parte A: la ecuación de Kepler por Newton ===")
    print(f"{'e':>6} {'M [rad]':>8} {'E [rad]':>10} {'iteraciones':>12}")
    for e in (0.001, 0.01, 0.3, 0.7):
        E, it = kepler_newton(1.0, e)
        print(f"{e:>6} {1.0:>8} {E:>10.6f} {it:>12}")
    print("-> con e ~ 0.01 (GNSS) converge en 2-3 iteraciones: por eso las")
    print("   efemérides asumen que resolverla es 'gratis'.")

    print("\n=== Parte B: cadena M -> E -> nu (e = 0.7, M = 1 rad) ===")
    e, M = 0.7, 1.0
    E, _ = kepler_newton(M, e)
    nu = anomalia_verdadera(E, e)
    print(f"M = {M:.4f} -> E = {E:.4f} -> nu = {nu:.4f} rad "
          f"({np.degrees(nu):.1f}°)")
    assert np.isclose(E - e * np.sin(E), M), "Kepler no se satisface"
    print("verificación E - e·sin(E) = M: OK")

    print("\n=== Parte C: las órbitas que importan (T = 2π√(a³/μ)) ===")
    print(f"{'órbita':<22} {'a [km]':>9} {'T':>12} {'v [km/s]':>9}")
    orbitas = [("ISS (~420 km)", 6_798e3),
               ("GPS", 26_560e3),
               ("Galileo", 29_600e3),
               ("GEO", 42_164e3)]
    for nombre, a in orbitas:
        T = periodo(a)
        h, m = int(T // 3600), int(T % 3600 // 60)
        print(f"{nombre:<22} {a/1e3:>9.0f} {f'{h}h {m:02d}m':>12} "
              f"{vel_circular(a)/1e3:>9.2f}")
    T_gps = periodo(26_560e3)
    assert abs(T_gps - 43_077) < 30, "el periodo GPS debe dar ~11h58m"
    print("-> GPS: medio día SIDÉREO (11h58m): el ground track se repite cada")
    print("   día; Galileo eligió 14h05m justamente para NO resonar (ver caso).")

    print("\n=== Parte D: tercera ley (T²/a³ constante) ===")
    ctes = [periodo(a) ** 2 / a**3 for _, a in orbitas]
    print("T²/a³ =", " ".join(f"{c:.3e}" for c in ctes),
          f"| 4π²/μ = {4 * np.pi**2 / MU:.3e}")
    assert np.allclose(ctes, 4 * np.pi**2 / MU)
    print("OK: misma constante para todas.")

    print("\n=== Parte E: J2 — la Tierra achatada mueve el plano orbital ===")
    for nombre, a, i_deg in [("GPS", 26_560e3, 55.0),
                             ("Galileo", 29_600e3, 56.0),
                             ("ISS", 6_798e3, 51.6)]:
        od = regresion_nodal_J2(a, 0.01, np.radians(i_deg))
        print(f"{nombre:<8} i={i_deg}°: OMEGA_dot = {np.degrees(od)*86400:+.3f} °/día")
    print("-> por esto la efeméride broadcast incluye OMEGA_DOT: el plano")
    print("   orbital no se queda quieto. (La ISS lo usa a favor: heliosíncrono")
    print("   sería el caso extremo.)")

    print("\n=== Parte F: verificación del ejercicio a mano E2 ===")
    e, M = 0.1, 1.0
    E1 = M + (M - (M - e * np.sin(M))) / (1 - e * np.cos(M))
    E_exacto, it = kepler_newton(M, e)
    print(f"1 paso de Newton desde E0=M: E1 = {E1:.5f} | "
          f"exacto: {E_exacto:.5f} (en {it} it)")
    print(f"error tras UNA iteración: {abs(E1 - E_exacto):.2e} rad")
