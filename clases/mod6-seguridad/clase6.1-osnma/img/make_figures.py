#!/usr/bin/env python3
"""Figuras 6.1 — esquemas de las tres primitivas (autocontenidas)."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
aca = Path(__file__).resolve().parent

# fig1: cadena TESLA
fig, ax = plt.subplots(figsize=(9, 2.6))
for i, lbl in enumerate(["KROOT\nK0", "K1", "K2", "K3", "K4"]):
    ax.add_patch(FancyBboxPatch((i*1.9, 0), 1.2, 0.8, boxstyle="round,pad=0.05",
                 fc="#dce8f5" if i else "#f5d9a8", ec="#205080"))
    ax.text(i*1.9+0.6, 0.4, lbl, ha="center", va="center", fontsize=9, weight="bold" if not i else "normal")
    if i < 4:
        ax.add_patch(FancyArrowPatch((i*1.9+1.9, 0.4), (i*1.9+1.2, 0.4),
                     arrowstyle="-|>", mutation_scale=13, color="#c44"))
ax.text(4.3, 1.15, "se generan hacia atrás:  K[i] = SHA256(K[i+1])", fontsize=9, color="#c44")
ax.text(4.3, -0.5, "se revelan hacia adelante K1,K2,… (con retardo); cada una se verifica hasta la KROOT",
        fontsize=8, color="#555")
ax.set_xlim(-0.3, 9.5); ax.set_ylim(-0.8, 1.4); ax.axis("off")
ax.set_title("Primitiva 1 — cadena TESLA (revelación diferida)")
fig.tight_layout(); fig.savefig(aca/"fig1_tesla.svg")

# fig2: árbol de Merkle
fig, ax = plt.subplots(figsize=(8, 4))
pos = {"raiz": (4, 3), "n0": (2, 2), "n1": (6, 2),
       "h0": (1, 1), "h1": (3, 1), "h2": (5, 1), "h3": (7, 1)}
edges = [("raiz","n0"),("raiz","n1"),("n0","h0"),("n0","h1"),("n1","h2"),("n1","h3")]
for a,b in edges:
    ax.plot([pos[a][0],pos[b][0]],[pos[a][1],pos[b][1]], color="#999", lw=1)
labels = {"raiz":"RAÍZ\n(embebida)","n0":"H01","n1":"H23","h0":"pk0","h1":"pk1","h2":"pk2","h3":"pk3"}
for k,(x,y) in pos.items():
    c = "#f5d9a8" if k=="raiz" else ("#d8ecd8" if k=="h2" else "#dce8f5")
    ax.add_patch(FancyBboxPatch((x-0.5,y-0.28),1,0.56, boxstyle="round,pad=0.03", fc=c, ec="#205080"))
    ax.text(x,y,labels[k], ha="center", va="center", fontsize=8)
ax.text(5,0.35,"probar pk2: aporto H3 y H01 → reconstruyo la raíz", fontsize=8, color="#2a6")
ax.set_xlim(0,8); ax.set_ylim(0,3.6); ax.axis("off")
ax.set_title("Primitiva 2 — árbol de Merkle (prueba de inclusión)")
fig.tight_layout(); fig.savefig(aca/"fig2_merkle.svg")
print("figuras escritas: ['fig1_tesla.svg', 'fig2_merkle.svg']")
