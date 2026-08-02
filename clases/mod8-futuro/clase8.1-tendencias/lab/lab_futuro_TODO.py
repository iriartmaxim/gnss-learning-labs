# %% [markdown]
# # Lab 8.1 — LEO-PNT vs MEO (ESQUELETO)
#
# Cuantificá por qué LEO cambia el juego: período, Doppler y ventaja de
# potencia. Física orbital de la clase 0.3. Completá los TODO.
#
#     python3 clases/mod8-futuro/clase8.1-tendencias/lab/lab_futuro_TODO.py

# %%
import numpy as np
MU = 3.986004418e14; RE = 6371e3; C = 299792458.0; F_L1 = 1575.42e6

# %% [markdown]
# ## TODO 1 — período y velocidad orbital (3ª ley, clase 0.3)
# a = RE + altitud ; T = 2π√(a³/μ) ; v = √(μ/a).

# %%
def periodo(alt_km):
    a = RE + alt_km*1e3
    # TODO 1a: return 2*pi*sqrt(a**3/MU)
    ...

def vel_orbital(alt_km):
    a = RE + alt_km*1e3
    # TODO 1b: return sqrt(MU/a)
    ...

# %% [markdown]
# ## TODO 2 — ventaja de potencia LEO (ley cuadrática inversa)
# Al cénit, la distancia usuario→satélite ES la altitud. Ganancia = 20·log10(alt_MEO/alt_LEO).

# %%
def ganancia_db(alt_meo, alt_leo):
    # TODO 2: return 20*np.log10(alt_meo/alt_leo)
    ...

# %%
MEO, LEO = 23222.0, 550.0
print(f"MEO período {periodo(MEO)/3600:.1f} h | LEO período {periodo(LEO)/3600:.2f} h")
print(f"ventaja de potencia LEO: +{ganancia_db(MEO, LEO):.0f} dB")
assert periodo(LEO)/3600 < 2 and ganancia_db(MEO, LEO) > 25
print("LISTO: futuro 8.1")
