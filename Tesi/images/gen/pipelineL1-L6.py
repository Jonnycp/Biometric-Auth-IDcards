import matplotlib.pyplot as plt
import matplotlib.patches as patches

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 9.5,
    "mathtext.fontset": "cm"
})

fig, ax = plt.subplots(figsize=(14, 5.4), dpi=300)
ax.set_xlim(0, 16.2)
ax.set_ylim(0, 6.2)
ax.axis('off')

# Funzioni di disegno
def draw_boundary(x, y, w, h, label):
    rect = patches.FancyBboxPatch((x, y), w, h,
                                  boxstyle="round,pad=0.05,rounding_size=0.2",
                                  facecolor="#f8fafc", edgecolor="#64748b",
                                  linestyle="--", linewidth=1.3, zorder=1)
    ax.add_patch(rect)
    ax.text(x + 0.2, y + h - 0.22, label, ha='left', va='top',
            fontsize=8.8, style='italic', fontweight='bold', color='#475569', zorder=2)

def draw_stage(x, y, w, h, title, subtitle):
    rect = patches.FancyBboxPatch((x - w/2, y - h/2), w, h,
                                  boxstyle="round,pad=0.05,rounding_size=0.15",
                                  facecolor="#e0f2fe", edgecolor="#0284c7",
                                  linewidth=1.7, zorder=3)
    ax.add_patch(rect)
    ax.text(x, y + 0.16, title, ha='center', va='center',
            fontsize=9.5, fontweight='bold', color='#0f172a', zorder=4)
    ax.text(x, y - 0.22, subtitle, ha='center', va='center',
            fontsize=8.2, color='#334155', zorder=4)

def draw_leakage(x, y, code, desc, high_risk=False):
    w, h = 1.15, 0.38
    fc = "#fee2e2" if high_risk else "#fef3c7"
    ec = "#dc2626" if high_risk else "#d97706"
    tc = "#991b1b" if high_risk else "#92400e"
    
    badge = patches.FancyBboxPatch((x - w/2, y - h/2), w, h,
                                   boxstyle="round,pad=0.03,rounding_size=0.1",
                                   facecolor=fc, edgecolor=ec, linewidth=1.4, zorder=4)
    ax.add_patch(badge)
    label_txt = f"{code} ▲" if high_risk else code
    ax.text(x, y, label_txt, ha='center', va='center',
            fontsize=8.5, fontweight='bold', color=tc, zorder=5)
    ax.text(x, y - 0.32, desc, ha='center', va='top',
            fontsize=7.8, color='#1e293b', linespacing=1.2, zorder=5)

# ==============================================================================
# 1. DOMINI DI FIDUCIA (TRUST BOUNDARIES)
# ==============================================================================
draw_boundary(0.3, 1.3, 6.2, 4.3, "Acquisizione / Client")
draw_boundary(6.8, 1.3, 3.3, 4.3, "Edge / Locale")
draw_boundary(10.4, 1.3, 5.5, 4.3, "Back-end / Servizi Remoti")

# ==============================================================================
# 2. STADI DELLA PIPELINE (5 BLOCCHI)
# ==============================================================================
y_stage = 4.1
st_w, st_h = 2.45, 1.1

stages = [
    {"x": 1.85, "title": "1. Acquisizione",        "sub": "Webcam / CIE"},
    {"x": 4.95, "title": "2. Pre-processing",      "sub": "Allineamento e crop"},
    {"x": 8.45, "title": "3. Estrazione Feature",  "sub": "Embedding $e \\in \\mathbb{R}^{512}$"},
    {"x": 11.85,"title": "4. Gestione Template",   "sub": "Archiviazione DB"},
    {"x": 14.65,"title": "5. Matching & Decisione","sub": "Confronto $S_c \\geq \\tau$"}
]

for i, st in enumerate(stages):
    draw_stage(st["x"], y_stage, st_w, st_h, st["title"], st["sub"])
    # Frecce di flusso tra gli stadi
    if i < len(stages) - 1:
        x_start = st["x"] + st_w/2 + 0.08
        x_end   = stages[i+1]["x"] - st_w/2 - 0.08
        ax.annotate('', xy=(x_end, y_stage), xytext=(x_start, y_stage),
                    arrowprops=dict(arrowstyle='->', lw=1.8, color='#0284c7'), zorder=4)

# ==============================================================================
# 3. LIVELLI DI ESPOSIZIONE / LEAKAGE (L1 - L6)
# ==============================================================================
y_leak = 2.65

draw_leakage(1.85, y_leak, "L1", "Raw biometrics\n(fotogrammi grezzi)", high_risk=True)
draw_leakage(4.95, y_leak, "L2", "Intermediate\nrepresentations", high_risk=False)

# L3 e L4 sotto Estrazione Feature
draw_leakage(7.72, y_leak, "L3", "Embeddings &\ntemplates", high_risk=False)
draw_leakage(9.18, y_leak, "L4", "Model\nparameters ($\\theta$)", high_risk=False)

draw_leakage(11.85, y_leak, "L5", "Database e\nmetadati", high_risk=False)
draw_leakage(14.65, y_leak, "L6", "Canali di\ncomunicazione", high_risk=True)

# ==============================================================================
# 4. LEGENDA INFERIORE COMPATTA
# ==============================================================================
y_leg = 0.55

# Elemento 1: Stadio pipeline
ax.add_patch(patches.FancyBboxPatch((0.6, y_leg - 0.15), 0.55, 0.3, boxstyle="round,pad=0.02,rounding_size=0.08",
                                    facecolor="#e0f2fe", edgecolor="#0284c7", linewidth=1.4))
ax.text(1.3, y_leg, "Stadio della pipeline", va='center', fontsize=8.5, color='#1e293b')

# Elemento 2: Trust boundary
ax.add_patch(patches.FancyBboxPatch((4.2, y_leg - 0.15), 0.55, 0.3, boxstyle="round,pad=0.02,rounding_size=0.08",
                                    facecolor="#f8fafc", edgecolor="#64748b", linestyle="--", linewidth=1.2))
ax.text(4.9, y_leg, "Dominio di fiducia (Trust boundary)", va='center', fontsize=8.5, color='#1e293b')

# Elemento 3: Esposizione L2-L5
ax.add_patch(patches.FancyBboxPatch((9.1, y_leg - 0.15), 0.55, 0.3, boxstyle="round,pad=0.02,rounding_size=0.08",
                                    facecolor="#fef3c7", edgecolor="#d97706", linewidth=1.3))
ax.text(9.8, y_leg, "Esposizione dati (L2–L5)", va='center', fontsize=8.5, color='#1e293b')

# Elemento 4: Massima esposizione L1, L6
ax.add_patch(patches.FancyBboxPatch((12.8, y_leg - 0.15), 0.55, 0.3, boxstyle="round,pad=0.02,rounding_size=0.08",
                                    facecolor="#fee2e2", edgecolor="#dc2626", linewidth=1.3))
ax.text(13.5, y_leg, "Massima esposizione operativa (L1, L6)", va='center', fontsize=8.5, color='#1e293b')

plt.tight_layout()
plt.savefig('pipeline_leakage_L1_L6.png', format='png', dpi=300, bbox_inches='tight')
plt.show()
