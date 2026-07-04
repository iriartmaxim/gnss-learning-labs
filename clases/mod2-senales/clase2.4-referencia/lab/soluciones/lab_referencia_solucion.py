#!/usr/bin/env python3
"""Solución 2.4 — validar tu receptor contra gnss-sdr (referencia).

Cierra el módulo 2: corre tu cadena propia (adquisición de la 2.2 sobre
las capturas IQ reales) y la compara contra el receptor de referencia
gnss-sdr, tanto contra sus valores publicados como corriéndolo de verdad.

Niveles:
  - SIEMPRE: compara tu adquisición contra los valores de los tests de
    gnss-sdr (PRN1=(524,+1680), SV1=(2920,-632)). No instala nada.
  - SI gnss-sdr está instalado: además lo corre sobre la misma captura
    (repetida para darle material) y parsea el Doppler/PRN que detecta.

Correr desde la raíz del repo. Exporta data/resultados_2_4.json.
"""
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import numpy as np

FS = 4_000_000.0
FC = 1.023e6
CODE_LEN = 1023
IQ = Path("data/raw/iq")
BASE24 = Path("clases/mod2-senales/clase2.4-referencia")

# --- verdad publicada por los unit tests de gnss-sdr -----------------------
VERDAD_GNSS_SDR = {
    "GPS_L1_CA_ID_1_Fs_4Msps_2ms.dat": {
        "sistema": "GPS L1 C/A", "prn": 1, "delay": 524, "doppler": 1680},
    "Galileo_E1_ID_1_Fs_4Msps_8ms.dat": {
        "sistema": "Galileo E1-B", "prn": 1, "delay": 2920, "doppler": -632},
}

TAPS_G2 = {1: (2, 6), 2: (3, 7), 3: (4, 8), 4: (5, 9), 5: (1, 9),
           6: (2, 10), 7: (1, 8), 8: (2, 9), 9: (3, 10), 10: (2, 3)}


def ca_chips(prn):
    g1, g2 = [1] * 10, [1] * 10
    s1, s2 = TAPS_G2[prn]
    b = np.empty(CODE_LEN, dtype=np.int64)
    for i in range(CODE_LEN):
        b[i] = g1[9] ^ g2[s1 - 1] ^ g2[s2 - 1]
        g1 = [g1[2] ^ g1[9]] + g1[:9]
        g2 = [g2[1] ^ g2[2] ^ g2[5] ^ g2[7] ^ g2[8] ^ g2[9]] + g2[:9]
    return 1 - 2 * b


def replica_gps(prn, fs=FS):
    c = ca_chips(prn).astype(float)
    idx = (np.arange(int(fs * 1e-3)) * FC / fs).astype(int) % CODE_LEN
    return c[idx]


def replica_e1b():
    hexstr = (BASE24.parent / "clase2.2-adquisicion" / "data" /
              "e1b_prn1.hex").read_text().strip()
    bits = np.array([int(b) for b in bin(int(hexstr, 16))[2:].zfill(4092)])
    cc = 1.0 - 2.0 * bits
    t = np.arange(int(FS * 4e-3)) / FS
    idx = (t * FC).astype(int) % 4092
    sub = np.sign(np.sin(2 * np.pi * FC * t))
    sub[sub == 0] = 1.0
    return cc[idx] * sub


def adquirir(iq, replica, fs=FS, dmax=10_000, dstep=250, no_coh=2):
    """PCPS de la 2.2: FFT en fase de código × grilla Doppler."""
    n = replica.size
    R = np.conj(np.fft.fft(replica))
    dops = np.arange(-dmax, dmax + 1, dstep)
    grid = np.zeros((dops.size, n))
    t = np.arange(n) / fs
    for k in range(no_coh):
        seg = iq[k * n:(k + 1) * n]
        if seg.size < n:
            break
        X = seg * np.exp(-2j * np.pi * np.outer(dops, t))
        grid += np.abs(np.fft.ifft(np.fft.fft(X, axis=1) * R, axis=1)) ** 2
    i, j = np.unravel_index(np.argmax(grid), grid.shape)
    resto = np.delete(grid[i], j)
    return int(j), int(dops[i]), float(grid[i, j] / resto.mean())


def cargar_iq(nombre):
    ruta = IQ / nombre
    if not ruta.exists():
        raise SystemExit(f"falta {ruta} — corré: python3 tools/fetch_iq.py")
    return np.fromfile(ruta, dtype=np.complex64)


def correr_gnss_sdr(captura_larga):
    """Corre gnss-sdr sobre la captura y parsea Doppler/PRN de su log.

    gnss-sdr necesita más de 2 ms para completar el flujo, así que
    repetimos la captura ~100× en un archivo temporal. Devuelve un dict
    con lo que detectó (doppler, code_phase, test_statistic) o None.
    """
    with tempfile.TemporaryDirectory() as tmp:
        conf = Path(tmp) / "run.conf"
        conf.write_text(f"""[GNSS-SDR]
GNSS-SDR.internal_fs_sps=4000000
SignalSource.implementation=File_Signal_Source
SignalSource.filename={captura_larga}
SignalSource.item_type=gr_complex
SignalSource.sampling_frequency=4000000
SignalSource.repeat=false
SignalSource.enable_throttle_control=false
SignalConditioner.implementation=Pass_Through
Channels_1C.count=1
Channels.in_acquisition=1
Channel.signal=1C
Acquisition_1C.implementation=GPS_L1_CA_PCPS_Acquisition
Acquisition_1C.item_type=gr_complex
Acquisition_1C.coherent_integration_time_ms=1
Acquisition_1C.threshold=0.008
Acquisition_1C.doppler_max=10000
Acquisition_1C.doppler_step=250
Tracking_1C.implementation=GPS_L1_CA_DLL_PLL_Tracking
Tracking_1C.item_type=gr_complex
Tracking_1C.pll_bw_hz=40.0
Tracking_1C.dll_bw_hz=4.0
TelemetryDecoder_1C.implementation=GPS_L1_CA_Telemetry_Decoder
Observables.implementation=Hybrid_Observables
PVT.implementation=RTKLIB_PVT
""")
        try:
            r = subprocess.run(
                ["gnss-sdr", "--config_file", str(conf),
                 "--log_dir", tmp],
                capture_output=True, text=True, timeout=180)
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            return {"error": str(e)}
        texto = r.stdout + "\n" + r.stderr
        logs = list(Path(tmp).glob("*INFO*"))
        if logs:
            texto += "\n" + logs[0].read_text(errors="ignore")
        det = {"trackeo": "Tracking of GPS L1" in texto}
        m = re.search(r"positive acquisition.*?code phase (\d+), "
                      r"doppler (-?\d+)", texto)
        if m:
            det["code_phase"] = int(m.group(1))
            det["doppler"] = int(m.group(2))
        ts = re.search(r"test statistics value ([\d.]+)", texto)
        if ts:
            det["test_statistic"] = float(ts.group(1))
        prn = re.search(r"satellite GPS PRN (\d+)", texto)
        if prn:
            det["prn"] = int(prn.group(1))
        return det


def main():
    out = {"comparacion": [], "gnss_sdr_instalado":
           shutil.which("gnss-sdr") is not None}
    print("=== Validación contra gnss-sdr (receptor de referencia) ===\n")

    for nombre, verdad in VERDAD_GNSS_SDR.items():
        iq = cargar_iq(nombre)
        if verdad["sistema"].startswith("GPS"):
            d, f, m = adquirir(iq, replica_gps(verdad["prn"]))
        else:
            d, f, m = adquirir(iq, replica_e1b(), dstep=125)
        ed = abs(d - verdad["delay"])
        ef = abs(f - verdad["doppler"])
        ok = ed <= 2 and ef <= 250
        print(f"[{verdad['sistema']}] PRN{verdad['prn']}")
        print(f"  tu cadena : delay={d:5d}  doppler={f:+5d} Hz  métrica={m:.0f}")
        print(f"  gnss-sdr  : delay={verdad['delay']:5d}  "
              f"doppler={verdad['doppler']:+5d} Hz  (verdad publicada)")
        print(f"  Δ         : delay={ed}, doppler={ef} Hz  "
              f"-> {'OK COINCIDE' if ok else 'revisar'}\n")
        out["comparacion"].append({
            "sistema": verdad["sistema"], "prn": verdad["prn"],
            "propio": {"delay": d, "doppler": f, "metrica": m},
            "gnss_sdr_publicado": {"delay": verdad["delay"],
                                   "doppler": verdad["doppler"]},
            "delta_delay": ed, "delta_doppler": ef, "coincide": ok})
        assert ok, f"tu adquisición no coincide con gnss-sdr para {nombre}"

    # nivel 2: correr gnss-sdr de verdad sobre la captura GPS
    if out["gnss_sdr_instalado"]:
        print("gnss-sdr detectado: corriendo el receptor real sobre GPS "
              "(captura repetida 100x para darle material)...")
        iqg = cargar_iq("GPS_L1_CA_ID_1_Fs_4Msps_2ms.dat")
        largo = Path(tempfile.gettempdir()) / "gps_long_2_4.dat"
        np.tile(iqg, 100).tofile(largo)
        det = correr_gnss_sdr(largo)
        out["gnss_sdr_real"] = det
        if det.get("doppler") is not None:
            print(f"  gnss-sdr REAL detectó: PRN{det.get('prn','?')}, "
                  f"Doppler={det['doppler']:+d} Hz, "
                  f"test_stat={det.get('test_statistic', 0):.0f}")
            mine = out["comparacion"][0]["propio"]["doppler"]
            coincide = abs(det["doppler"] - mine) <= 250
            print(f"  tu Doppler={mine:+d} Hz  ->  "
                  f"{'MISMO Doppler' if coincide else 'difiere'}")
            print(f"  (el code phase difiere: gnss-sdr arranca en otro "
                  f"sample_stamp; es el mismo satélite mod 1023)")
        if det.get("trackeo"):
            print("  gnss-sdr enganchó el tracking de PRN1")
    else:
        print("gnss-sdr NO instalado: comparación contra valores publicados.")
        print("Para el nivel estrella: sudo apt install gnss-sdr y recorré.")

    dest = BASE24 / "data" / "resultados_2_4.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=1))
    print(f"\nexportado -> {dest.name}")
    print("OK: tu cadena 2.1->2.3 concuerda con el receptor de referencia")


if __name__ == "__main__":
    main()
