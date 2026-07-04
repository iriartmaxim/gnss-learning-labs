#!/usr/bin/env python3
"""Solución 2.2 — adquisición PCPS: FFT en fase de código × grilla Doppler.

Corre sobre las capturas IQ oficiales de gnss-sdr (float32 I/Q, 4 Msps):
  GPS_L1_CA_ID_1_Fs_4Msps_2ms.dat            -> PRN1: delay 524, +1680 Hz
  Galileo_E1_ID_1_Fs_4Msps_8ms.dat           -> SV1 : delay 2920, -632 Hz
  GSoC_CTTC_capture_2012_07_26_4Msps_4ms.dat -> captura real: sky-search
Las verdades salen de los unit tests del propio gnss-sdr.
Bajar los datos con: python3 tools/fetch_iq.py
Correr desde la raíz del repo. Exporta data/resultados_2_2.json.
"""
import json
from pathlib import Path

import numpy as np

FS = 4_000_000.0
AQUI = Path(__file__).resolve().parents[2]
IQ = AQUI.parents[2] / "data" / "raw" / "iq"

# --- réplica GPS C/A (generador de la clase 2.1, autocontenido) -----------
TAPS_G2 = {1: (2, 6), 2: (3, 7), 3: (4, 8), 4: (5, 9), 5: (1, 9),
           6: (2, 10), 7: (1, 8), 8: (2, 9), 9: (3, 10), 10: (2, 3),
           11: (3, 4), 12: (5, 6), 13: (6, 7), 14: (7, 8), 15: (8, 9),
           16: (9, 10), 17: (1, 4), 18: (2, 5), 19: (3, 6), 20: (4, 7),
           21: (5, 8), 22: (6, 9), 23: (1, 3), 24: (4, 6), 25: (5, 7),
           26: (6, 8), 27: (7, 9), 28: (8, 10), 29: (1, 6), 30: (2, 7),
           31: (3, 8), 32: (4, 9)}


def ca_chips(prn: int) -> np.ndarray:
    """C/A del PRN como chips ±1 (LFSR G1/G2, ver clase 2.1)."""
    g1, g2 = [1] * 10, [1] * 10
    s1, s2 = TAPS_G2[prn]
    bits = np.empty(1023, dtype=np.int64)
    for i in range(1023):
        bits[i] = g1[9] ^ g2[s1 - 1] ^ g2[s2 - 1]
        f1 = g1[2] ^ g1[9]
        f2 = g2[1] ^ g2[2] ^ g2[5] ^ g2[7] ^ g2[8] ^ g2[9]
        g1 = [f1] + g1[:9]
        g2 = [f2] + g2[:9]
    return 1 - 2 * bits


def replica_gps(prn: int, fs: float = FS) -> np.ndarray:
    """Un período de C/A (1 ms) muestreado a fs."""
    c = ca_chips(prn).astype(float)
    idx = (np.arange(int(fs * 1e-3)) * 1.023e6 / fs).astype(int) % 1023
    return c[idx]


def replica_e1b(fs: float = FS) -> np.ndarray:
    """Un período de E1-B SV1 (4 ms) con subportadora BOC(1,1) seno.

    El código primario es de memoria (4092 chips, ICD anexo C); acá lo
    leemos del hex extraído de gnss-sdr. A 4 Msps la componente BOC(6,1)
    del CBOC no es representable: réplica BOC(1,1), pérdida ~0.4 dB.
    """
    hexstr = (AQUI / "data" / "e1b_prn1.hex").read_text().strip()
    bits = np.array([int(b) for b in bin(int(hexstr, 16))[2:].zfill(4092)])
    c = 1.0 - 2.0 * bits
    t = np.arange(int(fs * 4e-3)) / fs
    idx = (t * 1.023e6).astype(int) % 4092
    sub = np.sign(np.sin(2 * np.pi * 1.023e6 * t))
    sub[sub == 0] = 1.0
    return c[idx] * sub


# --- el algoritmo: PCPS ----------------------------------------------------
def adquirir(iq, replica, fs=FS, dmax=10_000, dstep=250, no_coherentes=1):
    """Búsqueda paralela en fase de código (FFT) × grilla Doppler.

    Devuelve (delay_muestras, doppler_hz, metrica, grid). La métrica es
    pico / media del resto de su fila (proxy simple de detección).
    """
    n = replica.size
    R = np.conj(np.fft.fft(replica))
    dops = np.arange(-dmax, dmax + 1, dstep)
    grid = np.zeros((dops.size, n))
    t = np.arange(n) / fs
    for k in range(no_coherentes):
        seg = iq[k * n:(k + 1) * n]
        if seg.size < n:
            break
        X = seg * np.exp(-2j * np.pi * np.outer(dops, t))
        grid += np.abs(np.fft.ifft(np.fft.fft(X, axis=1) * R, axis=1)) ** 2
    i, j = np.unravel_index(np.argmax(grid), grid.shape)
    resto = np.delete(grid[i], j)
    return int(j), int(dops[i]), float(grid[i, j] / resto.mean()), grid


def cargar_iq(nombre: str) -> np.ndarray:
    """Captura gr_complex: float32 I/Q intercalado."""
    ruta = IQ / nombre
    if not ruta.exists():
        raise SystemExit(f"falta {ruta} — corré: "
                         "python3 tools/fetch_iq.py")
    return np.fromfile(ruta, dtype=np.complex64)


def main() -> None:
    out = {}

    # --- [A] GPS PRN1 con TUS códigos de la 2.1 ---------------------------
    iq = cargar_iq("GPS_L1_CA_ID_1_Fs_4Msps_2ms.dat")
    d, f, m, grid = adquirir(iq, replica_gps(1), no_coherentes=2)
    print(f"[A] GPS PRN1 : delay={d} muestras, doppler={f:+d} Hz, "
          f"métrica={m:.1f}  (esperado 524, +1680)")
    assert abs(d - 524) <= 2 and abs(f - 1680) <= 250
    out["gps"] = {"delay": d, "doppler": f, "metrica": m}

    # --- [B] Galileo E1-B SV1 (código de memoria + BOC) --------------------
    iq = cargar_iq("Galileo_E1_ID_1_Fs_4Msps_8ms.dat")
    d, f, m, _ = adquirir(iq, replica_e1b(), dstep=125, no_coherentes=2)
    print(f"[B] GAL  SV1 : delay={d} muestras, doppler={f:+d} Hz, "
          f"métrica={m:.1f}  (esperado 2920, -632)")
    assert abs(d - 2920) <= 2 and abs(f + 632) <= 125
    out["galileo"] = {"delay": d, "doppler": f, "metrica": m}

    # --- [C] Sky-search sobre la captura real (CTTC 2012) ------------------
    iq = cargar_iq("GSoC_CTTC_capture_2012_07_26_4Msps_4ms.dat")
    print("[C] sky-search CTTC (32 PRN, 4 ms no coherentes):")
    sky = {}
    for prn in range(1, 33):
        d, f, m, _ = adquirir(iq, replica_gps(prn), no_coherentes=4)
        sky[str(prn)] = {"delay": d, "doppler": f, "metrica": round(m, 2)}
    orden = sorted(sky, key=lambda p: -sky[p]["metrica"])
    for p in orden[:8]:
        s = sky[p]
        print(f"    PRN{int(p):02d}: métrica={s['metrica']:6.1f}  "
              f"delay={s['delay']:5d}  doppler={s['doppler']:+6d} Hz")
    out["sky_cttc"] = sky

    # grilla GPS achicada para la figura 1 (cada 4ta muestra)
    out["grid_gps"] = grid[:, ::4].round(1).tolist()
    out["grid_meta"] = {"dstep": 250, "dmax": 10_000, "dec": 4}

    dest = AQUI / "data" / "resultados_2_2.json"
    dest.write_text(json.dumps(out))
    print(f"exportado -> {dest.name}")
    print("OK: todos los asserts pasaron")


if __name__ == "__main__":
    main()
