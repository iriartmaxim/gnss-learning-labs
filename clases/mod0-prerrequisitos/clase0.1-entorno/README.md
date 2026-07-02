# Clase 0.1 — Entorno de trabajo

> **Módulo 0 — Prerrequisitos** · Prerrequisito de: todo · Duración: 30–60 min

Clase corta y utilitaria: dejar el entorno listo y **verificado por
script**, no por fe. Sin teoría, sin ejercicios — un checklist y un
verificador.

## Objetivos

- [ ] Python ≥ 3.10 con las librerías del curso instaladas.
- [ ] `git` configurado y el repo clonado.
- [ ] `lab/verificar_entorno.py` termina con "entorno LISTO" (exit 0).

## Setup

### Opción A — entorno del sistema (WSL2 / Linux)

```bash
pip install numpy scipy matplotlib pandas cryptography \
            georinex hatanaka unlzw3 nbformat jupyter \
            --break-system-packages   # solo si tu distro lo exige (PEP 668)
```

### Opción B — venv (recomendado si compartís la máquina)

```bash
python3 -m venv ~/.venvs/gnss
source ~/.venvs/gnss/bin/activate
pip install numpy scipy matplotlib pandas cryptography \
            georinex hatanaka unlzw3 nbformat jupyter
```

> El `.gitignore` del repo ya excluye `venv/` — no lo comitees.

### Para qué es cada cosa

| Paquete | Se usa en |
|---|---|
| numpy, matplotlib | todos los labs |
| scipy | módulo 2 (señales: correlación, filtros) |
| pandas | tablas de observables (1.5) |
| cryptography | OSNMA: ECDSA, HMAC, SHA (módulo 4) |
| georinex | parsear RINEX nav/obs (1.3, 1.5) |
| hatanaka, unlzw3 | descomprimir RINEX Hatanaka / .Z (0.4) |
| nbformat, jupyter | notebooks |

## Verificación

```bash
cd clases/mod0-prerrequisitos/clase0.1-entorno/lab
python3 verificar_entorno.py
```

Salida esperada (versiones pueden variar):

```text
=== Verificación del entorno gnss-learning-labs ===

Python         3.12.3       OK
numpy          2.5.0        OK    (todo el curso)
scipy          1.18.0       OK    (señales (módulo 2) y utilidades)
...
VEREDICTO: entorno LISTO para los módulos 0 y 1.
```

Si algo da FALTA, el propio script te dice qué instalar. El exit code
(0 = listo, 1 = falta algo) permite usarlo en CI o en un hook.

**Próxima clase → 0.2 Mínimos cuadrados**: el motor matemático de todo
el módulo 1.
