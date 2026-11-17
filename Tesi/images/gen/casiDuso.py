import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
    "font.size": 9.5
})

fig, ax = plt.subplots(figsize=(14, 8.4), dpi=300)
ax.set_xlim(0, 15.8)
ax.set_ylim(0, 9.8)
ax.axis('off')

# ==============================================================================
# 1. SYSTEM BOUNDARY
# ==============================================================================
boundary = patches.Rectangle((2.2, 0.35), 13.3, 9.1,
                             facecolor="#f2f3f5", edgecolor="#333333", linewidth=1.3, zorder=1)
ax.add_patch(boundary)
ax.text(8.85, 9.22, "Sistema di Autenticazione Biometrica Cross-Domain",
        ha='center', va='top', fontsize=10.5, fontweight='bold', color='#222222', zorder=2)

# ==============================================================================
# 2. ATTORE UML (Utente a sinistra)
# ==============================================================================
def draw_actor(ax, x, y, label, color="#2e7d32"):
    head = patches.Circle((x, y + 0.65), 0.22, facecolor="white", edgecolor="#222222", linewidth=1.4, zorder=4)
    ax.add_patch(head)
    ax.plot([x, x], [y + 0.43, y - 0.15], color="#222222", lw=1.4, zorder=4)
    ax.plot([x - 0.35, x + 0.35], [y + 0.25, y + 0.25], color="#222222", lw=1.4, zorder=4)
    ax.plot([x, x - 0.25], [y - 0.15, y - 0.65], color="#222222", lw=1.4, zorder=4)
    ax.plot([x, x + 0.25], [y - 0.15, y - 0.65], color="#222222", lw=1.4, zorder=4)
    ax.text(x, y - 0.88, label, ha='center', va='top', fontsize=10, fontweight='bold', color=color, zorder=4)

draw_actor(ax, x=0.95, y=4.8, label="Utente", color="#2e7d32")

# ==============================================================================
# 3. FUNZIONI PER CASI D'USO E RELAZIONI UML
# ==============================================================================
def draw_usecase(ax, x, y, w, h, text):
    ellipse = patches.Ellipse((x, y), w, h, facecolor="white", edgecolor="#111111", linewidth=1.4, zorder=3)
    ax.add_patch(ellipse)
    ax.text(x, y, text, ha='center', va='center', fontsize=8.8, color="#111111", linespacing=1.22, zorder=4)

def get_ellipse_edge(cx, cy, w, h, target_x, target_y):
    dx = target_x - cx
    dy = target_y - cy
    angle = np.arctan2(dy, dx)
    ex = cx + (w / 2.0) * np.cos(angle)
    ey = cy + (h / 2.0) * np.sin(angle)
    return ex, ey

def draw_uml_relation(ax, p1, p2, label, text_offset=(0.0, 0.12)):
    ax.annotate('', xy=p2, xytext=p1,
                arrowprops=dict(arrowstyle='-|>', lw=1.3, ls=':', color='#111111', mutation_scale=13),
                zorder=3)
    mx = (p1[0] + p2[0]) / 2.0 + text_offset[0]
    my = (p1[1] + p2[1]) / 2.0 + text_offset[1]
    ax.text(mx, my, label, ha='center', va='center', fontsize=7.8, color='#111111',
            bbox=dict(boxstyle='round,pad=0.10', facecolor='#f2f3f5', edgecolor='none', alpha=0.88), zorder=5)

# ==============================================================================
# 4. CASI D'USO PRINCIPALI (Colonna sinistra)
# ==============================================================================
uc_reg = (4.35, 6.65, 3.0, 1.25)   # Registrazione Identità
uc_aut = (4.35, 2.35, 3.0, 1.25)   # Autenticazione Biometrica Live

draw_usecase(ax, *uc_reg, "Registrazione Identità\n(Enrollment)")
draw_usecase(ax, *uc_aut, "Autenticazione\nBiometrica Live")

actor_hand = (1.45, 4.95)
p_reg_left = get_ellipse_edge(uc_reg[0], uc_reg[1], uc_reg[2], uc_reg[3], *actor_hand)
p_aut_left = get_ellipse_edge(uc_aut[0], uc_aut[1], uc_aut[2], uc_aut[3], *actor_hand)

ax.plot([actor_hand[0], p_reg_left[0]], [actor_hand[1], p_reg_left[1]], color="#2e7d32", lw=1.3, zorder=3)
ax.plot([actor_hand[0], p_aut_left[0]], [actor_hand[1], p_aut_left[1]], color="#2e7d32", lw=1.3, zorder=3)

# ==============================================================================
# 5. SOTTO-CASI D'USO INCLUSI ED ESTESI
# ==============================================================================
# 4 Inclusioni di Registrazione Identità (Enrollment)
uc_cie  = (9.7, 8.45, 3.2, 0.95)
uc_warp = (9.7, 7.25, 3.2, 0.95)
uc_bioh = (9.7, 6.05, 3.4, 1.00)
uc_uniq = (9.7, 4.85, 3.4, 1.00)

draw_usecase(ax, *uc_cie,  "Acquisizione\nFronte CIE")
draw_usecase(ax, *uc_warp, "Pre-processing Ottico\n(Warp + CLAHE)")
draw_usecase(ax, *uc_bioh, "Estrazione Embedding\ne Protezione BioHashing")
draw_usecase(ax, *uc_uniq, "Verifica Unicità Utente\n(Deduplicazione 1:N)")

# 3 Inclusioni di Autenticazione Biometrica Live
uc_str  = (9.7, 3.55, 3.2, 0.95)
uc_liv  = (9.7, 2.30, 3.4, 1.05)
uc_ver  = (9.7, 1.05, 3.4, 0.95)

draw_usecase(ax, *uc_str,  "Streaming Video\nReal-Time")
draw_usecase(ax, *uc_liv,  "Validazione Liveness su Buffer\n(MiniFASNet + KPS)")
draw_usecase(ax, *uc_ver,  "Verifica Vettoriale\nCross-Domain")

# Estensione <<extend>> Blocco per Spoof Attack (a destra)
uc_spf  = (13.85, 2.30, 2.7, 1.10)
draw_usecase(ax, *uc_spf,  "Blocco per\nSpoof Attack")

# ==============================================================================
# 6. COLLEGAMENTI <<include>> E <<extend>>
# ==============================================================================
reg_targets = [
    (uc_cie,  (-0.15, 0.16)),
    (uc_warp, (0.0,   0.13)),
    (uc_bioh, (0.0,  -0.13)),
    (uc_uniq, (-0.15, -0.16))
]
for target, off in reg_targets:
    p_start = get_ellipse_edge(uc_reg[0], uc_reg[1], uc_reg[2], uc_reg[3], target[0], target[1])
    p_end   = get_ellipse_edge(target[0], target[1], target[2], target[3], uc_reg[0], uc_reg[1])
    draw_uml_relation(ax, p_start, p_end, "<<include>>", text_offset=off)

aut_targets = [
    (uc_str, (-0.1,  0.15)),
    (uc_liv, (0.0,   0.13)),
    (uc_ver, (-0.1, -0.15))
]
for target, off in aut_targets:
    p_start = get_ellipse_edge(uc_aut[0], uc_aut[1], uc_aut[2], uc_aut[3], target[0], target[1])
    p_end   = get_ellipse_edge(target[0], target[1], target[2], target[3], uc_aut[0], uc_aut[1])
    draw_uml_relation(ax, p_start, p_end, "<<include>>", text_offset=off)

# Freccia <<extend>> da Blocco per Spoof Attack verso Validazione Liveness su Buffer
p_ext_start = get_ellipse_edge(uc_spf[0], uc_spf[1], uc_spf[2], uc_spf[3], uc_liv[0], uc_liv[1])
p_ext_end   = get_ellipse_edge(uc_liv[0], uc_liv[1], uc_liv[2], uc_liv[3], uc_spf[0], uc_spf[1])
draw_uml_relation(ax, p_ext_start, p_ext_end, "<<extend>>", text_offset=(0.0, 0.18))

plt.tight_layout()
plt.savefig('diagramma-casi-duso.png', format='png', dpi=300, bbox_inches='tight')
plt.show()
