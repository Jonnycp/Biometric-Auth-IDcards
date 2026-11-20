import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
    "font.size": 10.5,
    "mathtext.fontset": "cm"
})

fig, ax = plt.subplots(figsize=(11.5, 8.2), dpi=300)
ax.set_xlim(-1.2, 11.8)
ax.set_ylim(-0.6, 9.8)
ax.axis('off')

# Funzione di proiezione isometrica/assonometrica per i piani 3D
def proj(u, v, z_base):
    x = 1.6 + u * 6.4 + v * 2.2
    y = z_base + v * 1.45 - u * 0.25
    return x, y

# ==============================================================================
# 1. DEFINIZIONE NODI E ARCHI DEI TRE PIANI (L0, L1, L2)
# ==============================================================================
nodes_L0 = [
    (0.10, 0.82), (0.28, 0.88), (0.52, 0.85), (0.78, 0.86), (0.92, 0.72),
    (0.08, 0.55), (0.25, 0.62), (0.45, 0.64), (0.66, 0.60), (0.85, 0.52),
    (0.14, 0.30), (0.34, 0.38), (0.55, 0.42), (0.74, 0.34), (0.90, 0.24),
    (0.22, 0.12), (0.46, 0.15), (0.68, 0.12), (0.84, 0.08)
]

# Sottoinsieme annidato per L1 (8 nodi)
idx_L1 = [0, 2, 4, 6, 8, 10, 12, 16]

# Sottoinsieme annidato per L2 (4 nodi - archi lunghi)
idx_L2 = [0, 2, 8, 16]

# Archi locali densi per L0
edges_L0 = [
    (0,1), (1,2), (2,3), (3,4), (0,5), (1,6), (2,7), (3,8), (4,9),
    (5,6), (6,7), (7,8), (8,9), (5,10), (6,11), (7,12), (8,13), (9,14),
    (10,11), (11,12), (12,13), (13,14), (10,15), (11,16), (12,16), (13,17), (14,18),
    (15,16), (16,17), (17,18), (6,12), (7,13)
]

# Archi medi per L1
edges_L1 = [
    (0,2), (2,4), (0,6), (2,8), (4,8), (6,8), (6,10), (6,12), (8,12), (10,16), (12,16)
]

# Archi lunghi per L2
edges_L2 = [
    (0,2), (2,8), (8,16), (0,16), (2,16)
]

# Posizione logica della query e_live (vicino al nodo 13)
q_uv = (0.79, 0.28)
target_idx = 13

levels = [
    {"z": 0.3, "name": r"Livello $L_0$", "sub": "Tutti i vettori (archi corti)",
     "nodes": list(range(len(nodes_L0))), "edges": edges_L0, "bg": "#f8fafc", "ec": "#64748b", "nc": "#3b82f6"},
    {"z": 3.5, "name": r"Livello $L_1$", "sub": "Sottoinsieme intermedio",
     "nodes": idx_L1, "edges": edges_L1, "bg": "#f0f9ff", "ec": "#0284c7", "nc": "#0284c7"},
    {"z": 6.7, "name": r"Livello $L_2$", "sub": "Pochi nodi (archi lunghi)",
     "nodes": idx_L2, "edges": edges_L2, "bg": "#eef2ff", "ec": "#4f46e5", "nc": "#4f46e5"}
]

# ==============================================================================
# 2. DISEGNO DEI TRE PIANI E DEI GRAFI DI PROSSIMITÀ
# ==============================================================================
for lvl in levels:
    z = lvl["z"]
    p00 = proj(-0.04, -0.04, z)
    p10 = proj(1.04,  -0.04, z)
    p11 = proj(1.04,   1.04, z)
    p01 = proj(-0.04,  1.04, z)
    
    shadow = patches.Polygon([(x+0.08, y-0.08) for x, y in [p00, p10, p11, p01]],
                             closed=True, facecolor="#e2e8f0", alpha=0.6, edgecolor="none", zorder=1)
    ax.add_patch(shadow)
    
    plane = patches.Polygon([p00, p10, p11, p01], closed=True,
                            facecolor=lvl["bg"], edgecolor=lvl["ec"], linewidth=1.6, alpha=0.92, zorder=2)
    ax.add_patch(plane)
    
    lx, ly = proj(-0.06, 0.50, z)
    ax.text(lx - 0.25, ly + 0.15, lvl["name"], ha='right', va='center',
            fontsize=12.5, fontweight='bold', color=lvl["ec"])
    ax.text(lx - 0.25, ly - 0.22, lvl["sub"], ha='right', va='center',
            fontsize=8.8, style='italic', color='#475569')
    
    for u_i, v_i in lvl["edges"]:
        x1, y1 = proj(*nodes_L0[u_i], z)
        x2, y2 = proj(*nodes_L0[v_i], z)
        ax.plot([x1, x2], [y1, y2], color="#94a3b8", lw=1.15, zorder=3)
        
    for idx in lvl["nodes"]:
        nx, ny = proj(*nodes_L0[idx], z)
        ax.scatter(nx, ny, s=75, facecolor="white", edgecolor=lvl["nc"], linewidth=2.0, zorder=5)

    qx, qy = proj(*q_uv, z)
    ax.scatter(qx, qy, s=110, marker='*', facecolor="#f59e0b", edgecolor="#b45309", linewidth=1.1, zorder=8)
    ax.text(qx + 0.18, qy - 0.05, r"$e_{\mathrm{live}}$", ha='left', va='center',
            fontsize=10.5, fontweight='bold', color='#b45309', zorder=9)

# ==============================================================================
# 3. PROIEZIONI VERTICALI TRA I LIVELLI E DISCESA GREEDY
# ==============================================================================
def draw_vertical_drop(node_idx, z_from, z_to):
    x1, y1 = proj(*nodes_L0[node_idx], z_from)
    x2, y2 = proj(*nodes_L0[node_idx], z_to)
    ax.annotate('', xy=(x2, y2 + 0.08), xytext=(x1, y1 - 0.08),
                arrowprops=dict(arrowstyle='->,head_width=0.3,head_length=0.3',
                                lw=1.6, ls='--', color='#dc2626'), zorder=6)

def draw_greedy_step(idx_from, idx_to, z):
    x1, y1 = proj(*nodes_L0[idx_from], z)
    x2, y2 = proj(*nodes_L0[idx_to], z)
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->,head_width=0.32,head_length=0.32',
                                lw=2.3, color='#dc2626', shrinkA=4, shrinkB=4), zorder=7)

# L2: Entry point (nodo 0) -> nodo 8 -> nodo 16
ep_x, ep_y = proj(*nodes_L0[0], 6.7)
ax.scatter(ep_x, ep_y, s=95, facecolor="#dc2626", edgecolor="#7f1d1d", linewidth=1.5, zorder=7)
ax.text(ep_x - 0.12, ep_y + 0.25, "Entry point", ha='center', va='bottom',
        fontsize=9.2, fontweight='bold', color='#991b1b', zorder=9)

draw_greedy_step(0, 8, 6.7)
draw_greedy_step(8, 16, 6.7)

# Discesa L2 -> L1 sul nodo 16
draw_vertical_drop(16, 6.7, 3.5)

# L1: nodo 16 -> nodo 12 -> nodo 8
draw_greedy_step(16, 12, 3.5)
draw_greedy_step(12, 8, 3.5)

# Discesa L1 -> L0 sul nodo 8
draw_vertical_drop(8, 3.5, 0.3)

# L0: nodo 8 -> nodo 13 (vicino più prossimo e_j*)
draw_greedy_step(8, 13, 0.3)

# Evidenziazione nodo ottimo trovato e_j* su L0
tx, ty = proj(*nodes_L0[target_idx], 0.3)
ax.scatter(tx, ty, s=115, facecolor="#dc2626", edgecolor="#7f1d1d", linewidth=1.8, zorder=8)
ax.text(tx + 0.15, ty + 0.22, r"$e_j^*$ (Nearest Neighbor)", ha='left', va='bottom',
        fontsize=10.2, fontweight='bold', color='#991b1b', zorder=9)

# ==============================================================================
# 4. LEGENDA INFERIORE PULITA
# ==============================================================================
y_leg = -0.35
ax.scatter(0.5, y_leg, s=110, marker='*', facecolor="#f59e0b", edgecolor="#b45309", linewidth=1.1)
ax.text(0.8, y_leg, r"Query $e_{\mathrm{live}}$", va='center', fontsize=9.8, color='#1e293b')

ax.scatter(3.3, y_leg, s=75, facecolor="white", edgecolor="#0284c7", linewidth=2.0)
ax.text(3.6, y_leg, "Vettori indicizzati", va='center', fontsize=9.8, color='#1e293b')

ax.plot([6.6, 7.3], [y_leg, y_leg], color="#dc2626", lw=2.3)
ax.text(7.5, y_leg, r"Percorso greedy ($O(\log N)$)", va='center', fontsize=9.8, color='#1e293b')

ax.scatter(10.5, y_leg, s=95, facecolor="#dc2626", edgecolor="#7f1d1d", linewidth=1.5)
ax.text(10.8, y_leg, r"Vicino $e_j^*$", va='center', fontsize=9.8, color='#1e293b')

plt.tight_layout()
plt.savefig('../hnsw_multilivello.png', format='png', dpi=300, bbox_inches='tight')
plt.show()
