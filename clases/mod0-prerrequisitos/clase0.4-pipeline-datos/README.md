# Clase 0.4 — Pipeline de datos GNSS reales

Cierre del Módulo 0: dejar funcionando la descarga automática de datos
GNSS reales para que **todas** las clases que siguen (1.3, 1.5, y el
módulo 4 de OSNMA) trabajen con archivos de verdad y no con juguetes.

## Objetivos

- [ ] Distinguir los formatos: RINEX nav, RINEX obs, Hatanaka, SP3, CLK
- [ ] Conocer las fuentes públicas y sus latencias (broadcast / rapid / final)
- [ ] Usar `tools/fetch_data.py` para bajar un día real de datos
- [ ] Verificar el contenido con un censo por constelación y georinex

## Los formatos (qué es cada archivo)

| Formato | Extensión típica | Qué contiene | Lo usamos en |
|---|---|---|---|
| RINEX nav | `.rnx` (`_MN` = mixto) | Efemérides broadcast: los parámetros keplerianos + correcciones que transmite cada satélite | 1.3 |
| RINEX obs | `.rnx` / `.crx` | Observables del receptor: pseudodistancias, fase, Doppler, C/N0 | 1.5 |
| Hatanaka | `.crx` | RINEX obs comprimido (formato de Yuki Hatanaka); se descomprime con `hatanaka` | 1.5 |
| SP3 | `.SP3` | Órbitas **precisas** post-procesadas: posición ECEF de cada satélite cada 5–15 min | 1.3 (verdad de referencia) |
| CLK | `.CLK` | Relojes precisos de satélites y estaciones, cada 30 s | 1.5 |

La pareja clave del curso: la **efeméride broadcast** (lo que el satélite
dice de sí mismo, disponible al instante) contra el **SP3 final** (lo que
una red global de análisis calculó después, con error de ~2–3 cm). La
clase 1.3 es exactamente ese versus.

## Las fuentes (verificadas por HTTP el 2026-07-02)

| Fuente | Acceso | Qué tiene | Latencia |
|---|---|---|---|
| **BKG** (Alemania) `igs.bkg.bund.de/root_ftp/IGS/BRDC/` | HTTPS anónimo | BRDC nav multi-GNSS diario | horas |
| **CODE/AIUB** (Berna) `ftp.aiub.unibe.ch/CODE_MGEX/CODE/` | HTTP anónimo | SP3 + CLK **MGEX finales** (GPS+GLO+GAL+BDS+QZSS) | ~2 semanas |
| **BKG** `.../IGS/products/<semana>/` | HTTPS anónimo | SP3 rápido IGS (**solo GPS**) | ~1 día |
| CDDIS (NASA) | cuenta Earthdata | todo el archivo IGS | — |
| **RAMSAC** (IGN Argentina) | portal con formulario | RINEX obs de la red CORS argentina (para la 1.5: estación con coordenadas oficiales) | ~1 día |
| galmon.eu | web/API | telemetría Galileo en vivo, páginas OSNMA | tiempo real |

Regla práctica: para tener **Galileo con órbita precisa** hay que usar los
finales MGEX de CODE → el lab trabaja con una fecha ~3 semanas atrás
(2026-06-15, DOY 166) donde ya está todo publicado.

## Uso de `tools/fetch_data.py`

```bash
# desde la raíz del repo — baja nav + órbitas + relojes de un día
python3 tools/fetch_data.py --date 2026-06-15 --que brdc,sp3,clk

# observación RINEX 30 s de una estación IGS (p. ej. las argentinas
# LPGS/CORD/UNSA/MGUE/RIO2/RGDG) — usada desde la clase 1.5:
python3 tools/fetch_data.py --date 2026-06-15 --que obs --estacion CORD00ARG

# deja todo descomprimido en data/raw/2026/166/ (ignorado por git)
```

El script es idempotente (saltea lo ya bajado), usa solo stdlib, y si el
final MGEX todavía no existe cae solo al SP3 rápido de IGS avisando que
es solo GPS. Para `--que obs` el archivo viene en Hatanaka: si el
paquete `hatanaka` está instalado queda directamente el `.rnx`; si no,
queda el `.crx` y el script imprime cómo convertirlo.

## Lab: verificar lo bajado

```bash
python3 clases/mod0-prerrequisitos/clase0.4-pipeline-datos/lab/inspeccionar_datos.py data/raw/2026/166
```

Salida real (2026-06-15, recortada):

```
== BRDC00IGS_R_20261660000_01D_MN.rnx
  BeiDou      901 efemerides
  Galileo   11119 efemerides
  GPS         450 efemerides
  ...
== COD0MGXFIN_20261660000_01D_05M_ORB.SP3
  116 satelites: BeiDou 30, Galileo 30, GPS 32, QZSS 3, GLONASS 21
== georinex (solo Galileo; puede tardar ~1 min)
  30 satelites Galileo unicos (120 registros; los sufijos
  _N que agrega georinex son mensajes duplicados del mismo sv/epoca,
  p.ej. I/NAV vs F/NAV -- ojo con esto en la clase 1.3):
  E02 E03 E04 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15 E16 E18
  E19 E21 E23 E25 E26 E27 E28 E29 E30 E31 E32 E33 E34 E36
```

Chequeos que importan:

1. **Los 30 Galileo del nav coinciden con los 30 del SP3** — dos fuentes
   independientes describen la misma constelación.
2. ¿Por qué Galileo tiene 11 119 efemérides y GPS 450? GPS emite una
   efeméride cada 2 h; Galileo re-emite cada ~10 min **y** por varios
   canales (I/NAV en E1/E5b, F/NAV en E5a), y el archivo mixto guarda todo.
3. La trampa `_N` de georinex: mismo satélite + misma época por distinto
   tipo de mensaje → registros "duplicados" con sufijo. En la 1.3 hay que
   elegir **un** tipo de mensaje antes de propagar la órbita.

## Checkpoint del Módulo 0

Antes de pasar al Módulo 1, respondé sin mirar:

> ¿Por qué linealizar el problema PVT lo convierte en mínimos cuadrados
> **iterativo**, y qué papel juega el jacobiano en cada iteración?

(Pista: clase 0.2 Parte C — el modelo de pseudodistancia no es lineal en
la posición; el jacobiano son las derivadas geométricas y su geometría
define el DOP.)

## Próxima clase

**1.3 — Efemérides**: parsear una efeméride Galileo real de este mismo
BRDC, propagar la órbita con Kepler (clase 0.3) según el ICD, y validar
contra el SP3 de este mismo día. Los datos ya están en tu disco.
