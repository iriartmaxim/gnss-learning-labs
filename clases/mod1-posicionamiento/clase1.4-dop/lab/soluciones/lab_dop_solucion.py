"""Clase 1.4 — SOLUCIÓN del laboratorio: DOP y geometría.

Calcula todos los DOP del escenario de 10 satélites, verifica la identidad
GDOP² = PDOP² + TDOP², rota a ENU para HDOP/VDOP, barre la máscara de
elevación, busca el mejor y el peor subconjunto de 4, y verifica por
Monte Carlo que el error real ≈ PDOP × sigma. También verifica el
ejercicio a mano E1 (la G de 3×3 de la clase 1.2).

Uso: python lab_dop_solucion.py   (desde lab/soluciones/)
"""
import json
from itertools import combinations
from pathlib import Path

import numpy as np


# ---------------------------------------------------------------- funciones
def cargar_escenario():
    ruta = Path(__file__).resolve().parents[2] / "data" / "escenario_10sats.json"
    with open(ruta) as f:
        return json.load(f)


def matriz_G(x, sats):
    """G de pseudodistancias: fila i = [-u_i^T, 1] (n x 4). Igual que en 1.2."""
    rho = np.linalg.norm(sats - x[:3], axis=1)
    u = (sats - x[:3]) / rho[:, None]
    return np.hstack([-u, np.ones((len(sats), 1))])


def dops_ecef(G):
    Q = np.linalg.inv(G.T @ G)
    gdop = np.sqrt(np.trace(Q))
    pdop = np.sqrt(np.trace(Q[:3, :3]))
    tdop = np.sqrt(Q[3, 3])
    return Q, gdop, pdop, tdop


def rot_ecef_a_enu(lat_deg, lon_deg):
    la, lo = np.radians(lat_deg), np.radians(lon_deg)
    return np.array([
        [-np.sin(lo), np.cos(lo), 0.0],
        [-np.sin(la) * np.cos(lo), -np.sin(la) * np.sin(lo), np.cos(la)],
        [np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)],
    ])


def hdop_vdop(Q, lat_deg, lon_deg):
    R = rot_ecef_a_enu(lat_deg, lon_deg)
    Q_enu = R @ Q[:3, :3] @ R.T
    hdop = np.sqrt(Q_enu[0, 0] + Q_enu[1, 1])
    vdop = np.sqrt(Q_enu[2, 2])
    return Q_enu, hdop, vdop


def resolver_pvt(sats, pr, x0=None, tol=1e-4, max_iter=30):
    """Solver de la clase 1.2 (posición + c*dt)."""
    x = np.zeros(4) if x0 is None else np.array(x0, dtype=float)
    for _ in range(max_iter):
        rho = np.linalg.norm(sats - x[:3], axis=1)
        pred = rho + x[3]
        G = matriz_G(x, sats)
        delta, *_ = np.linalg.lstsq(G, pr - pred, rcond=None)
        x = x + delta
        if np.linalg.norm(delta) < tol:
            break
    return x


# ------------------------------------------------------------------- script
if __name__ == "__main__":
    esc = cargar_escenario()
    sats = np.array(esc["sat_ecef_m"])
    azel = np.array(esc["sat_azel_deg"])
    pr = np.array(esc["pseudodistancias_m"])
    r_true = np.array(esc["verdad"]["receptor_ecef_m"])
    lat, lon, _ = esc["verdad"]["receptor_geodetico"]
    x_true = np.append(r_true, esc["verdad"]["c_dt_m"])

    print("=== Parte A: DOPs del escenario completo (10 satélites) ===")
    G = matriz_G(x_true, sats)
    Q, gdop, pdop, tdop = dops_ecef(G)
    print(f"GDOP = {gdop:.3f} | PDOP = {pdop:.3f} | TDOP = {tdop:.3f}")
    assert abs(gdop**2 - (pdop**2 + tdop**2)) < 1e-9
    print("identidad GDOP^2 = PDOP^2 + TDOP^2: OK")

    _, hdop, vdop = hdop_vdop(Q, lat, lon)
    print(f"HDOP = {hdop:.3f} | VDOP = {vdop:.3f}")
    assert vdop > hdop, "la vertical siempre es peor: no hay satélites debajo"
    print(f"VDOP/HDOP = {vdop / hdop:.2f} (la vertical es peor: OK)")

    print("\n=== Parte B: barrido de la máscara de elevación ===")
    print(f"{'máscara':>8} {'n sats':>7} {'PDOP':>7} {'HDOP':>7} {'VDOP':>7}")
    for mask in (0, 5, 10, 15, 20, 25, 30, 35, 40, 45):
        vis = azel[:, 1] >= mask
        if vis.sum() < 4:
            print(f"{mask:>7}° {vis.sum():>7}   — menos de 4 satélites —")
            continue
        Gm = matriz_G(x_true, sats[vis])
        Qm, _, pd_m, _ = dops_ecef(Gm)
        _, hd_m, vd_m = hdop_vdop(Qm, lat, lon)
        print(f"{mask:>7}° {vis.sum():>7} {pd_m:>7.2f} {hd_m:>7.2f} {vd_m:>7.2f}")

    print("\n=== Parte C: mejor y peor subconjunto de 4 (de C(10,4)=210) ===")
    resultados = []
    for idx in combinations(range(10), 4):
        Gs = matriz_G(x_true, sats[list(idx)])
        try:
            _, g, _, _ = dops_ecef(Gs)
        except np.linalg.LinAlgError:
            g = np.inf
        resultados.append((g, idx))
    resultados.sort()
    g_min, idx_min = resultados[0]
    g_max, idx_max = resultados[-1]
    print(f"mejor 4:  GDOP = {g_min:.2f}  sats {list(idx_min)} "
          f"az/el {[tuple(map(int, azel[i])) for i in idx_min]}")
    print(f"peor 4:   GDOP = {g_max:.1f}  sats {list(idx_max)} "
          f"az/el {[tuple(map(int, azel[i])) for i in idx_max]}")
    print(f"con 10 sats el GDOP era {gdop:.2f}: la redundancia protege de "
          f"los subconjuntos malos")

    print("\n=== Parte D: Monte Carlo — el DOP predice el error ===")
    rng = np.random.default_rng(11)
    N, sigma = 300, 1.0
    errs = []
    for _ in range(N):
        prn = pr + rng.normal(0, sigma, len(pr))
        xs = resolver_pvt(sats, prn, x0=x_true + 10.0)
        errs.append(np.linalg.norm(xs[:3] - r_true))
    rms3d = np.sqrt(np.mean(np.square(errs)))
    print(f"error RMS 3D empírico ({N} corridas, sigma={sigma} m): {rms3d:.2f} m")
    print(f"predicción PDOP x sigma: {pdop * sigma:.2f} m")
    ratio = rms3d / (pdop * sigma)
    print(f"cociente empírico/predicho: {ratio:.2f}")
    assert 0.6 < ratio < 1.6, "el DOP debería predecir el error"
    print("-> el DOP no es una abstracción: PREDICE el error real. OK")

    print("\n=== Verificación del ejercicio a mano E1 (G de la clase 1.2) ===")
    G3 = np.array([[-0.6, -0.8, 1.0], [0.8, -0.6, 1.0], [0.0, 1.0, 1.0]])
    GtG = G3.T @ G3
    Q3 = np.linalg.inv(GtG)
    print("G'G =\n", np.round(GtG, 3))
    print("det(G'G) =", round(np.linalg.det(GtG), 4),
          "| det(G)^2 =", round(np.linalg.det(G3) ** 2, 4))
    print("diagonal de (G'G)^-1 =", np.round(np.diag(Q3), 4))
    print(f"'GDOP' 2D+t = {np.sqrt(np.trace(Q3)):.4f} | "
          f"'PDOP' 2D = {np.sqrt(Q3[0,0] + Q3[1,1]):.4f} | "
          f"TDOP = {np.sqrt(Q3[2,2]):.4f}")
