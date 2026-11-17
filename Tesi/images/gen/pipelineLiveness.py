import matplotlib.pyplot as plt
import matplotlib.patches as patches

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 10,
    "mathtext.fontset": "cm"
})

fig, ax = plt.subplots(figsize=(13.5, 4.4), dpi=300)
ax.set_xlim(0, 15.8)
ax.set_ylim(0, 4.8)
ax.axis('off')

def draw_state_box(ax, x, y, w, h, title, facecolor, edgecolor):
    rect = patches.FancyBboxPatch((x - w/2, y - h/2), w, h,
                                  boxstyle="round,pad=0.06,rounding_size=0.14",
                                  facecolor=facecolor, edgecolor=edgecolor, linewidth=1.6, zorder=3)
    ax.add_patch(rect)
    ax.text(x, y, title, ha='center', va='center', fontsize=8.8, 
            fontweight='bold', color='#111111', zorder=5)

def draw_diamond(ax, x, y, w, h, text, facecolor='#fff8dc', edgecolor='#d95f02'):
    pts = [[x, y + h/2], [x + w/2, y], [x, y - h/2], [x - w/2, y]]
    poly = patches.Polygon(pts, closed=True, facecolor=facecolor, edgecolor=edgecolor, linewidth=1.6, zorder=3)
    ax.add_patch(poly)
    ax.text(x, y, text, ha='center', va='center', fontsize=8.6, fontweight='bold', color='#111111', zorder=5)

# Coordinate Y principali
y_main  = 3.3
y_low   = 0.95
y_match = 3.95
y_nomat = 2.65

# ==============================================================================
# 1. WAITING_FACE
# ==============================================================================
draw_state_box(ax, x=1.35, y=y_main, w=2.0, h=0.68,
               title="WAITING_FACE",
               facecolor="#f0f4f8", edgecolor="#4a6fa5")

# Freccia -> ANALYZING_LIVENESS
ax.annotate('', xy=(3.32, y_main), xytext=(2.42, y_main),
            arrowprops=dict(arrowstyle='->', lw=1.5, color='#333333'))
ax.text(2.87, y_main + 0.14, "Volto\nrilevato", ha='center', va='bottom', fontsize=8.2, style='italic', color='#333333')

# ==============================================================================
# 2. ANALYZING_LIVENESS
# ==============================================================================
draw_state_box(ax, x=4.65, y=y_main, w=2.5, h=0.68,
               title="ANALYZING_LIVENESS",
               facecolor="#e6f2ff", edgecolor="#1f77b4")

# Freccia -> Bivio Decisionale
ax.annotate('', xy=(6.85, y_main), xytext=(5.97, y_main),
            arrowprops=dict(arrowstyle='->', lw=1.5, color='#333333'))
ax.text(6.41, y_main + 0.14, "Buffer\ncompleto", ha='center', va='bottom', fontsize=8.2, style='italic', color='#333333')

# ==============================================================================
# 3. BIVIO DECISIONALE (ROMBO)
# ==============================================================================
draw_diamond(ax, x=7.85, y=y_main, w=1.9, h=1.35,
             text="Score\nmedio?")

# ==============================================================================
# 4. RAMO INFERIORE -> SPOOF_ATTACK
# ==============================================================================
ax.annotate('', xy=(7.85, y_low + 0.42), xytext=(7.85, y_main - 0.70),
            arrowprops=dict(arrowstyle='->', lw=1.5, color='#d62728'))
ax.text(8.02, 2.0, r"$\mathrm{Score\ medio} < \tau_{\mathrm{liveness}}$",
        ha='left', va='center', fontsize=8.6, fontweight='bold', color='#d62728')

draw_state_box(ax, x=7.85, y=y_low, w=2.1, h=0.68,
               title="SPOOF_ATTACK",
               facecolor="#fdecea", edgecolor="#d62728")

# ==============================================================================
# 5. RAMO DESTRO -> AUTHENTICATING
# ==============================================================================
ax.annotate('', xy=(10.55, y_main), xytext=(8.82, y_main),
            arrowprops=dict(arrowstyle='->', lw=1.5, color='#2ca02c'))
ax.text(9.68, y_main + 0.14, r"$\mathrm{Score\ medio} \geq \tau_{\mathrm{liveness}}$",
        ha='center', va='bottom', fontsize=8.6, fontweight='bold', color='#2ca02c')

draw_state_box(ax, x=11.75, y=y_main, w=2.25, h=0.68,
               title="AUTHENTICATING",
               facecolor="#eef7f2", edgecolor="#2ca02c")

# ==============================================================================
# 6. USCITE FINALI SEPARATE: MATCH e NO_MATCH (Stesso colore)
# ==============================================================================
# Freccia verso MATCH (alto-destra)
ax.annotate('', xy=(13.75, y_match), xytext=(12.95, y_main + 0.12),
            arrowprops=dict(arrowstyle='->', lw=1.5, color='#333333',
                            connectionstyle="arc3,rad=-0.12"))
ax.text(13.28, y_match + 0.08, r"$S_c \geq \tau$", ha='center', va='bottom', fontsize=8.2, color='#333333')

draw_state_box(ax, x=14.65, y=y_match, w=1.65, h=0.62,
               title="MATCH",
               facecolor="#f3e8ff", edgecolor="#7b2cbf")

# Freccia verso NO_MATCH (basso-destra)
ax.annotate('', xy=(13.75, y_nomat), xytext=(12.95, y_main - 0.12),
            arrowprops=dict(arrowstyle='->', lw=1.5, color='#333333',
                            connectionstyle="arc3,rad=0.12"))
ax.text(13.28, y_nomat - 0.12, r"$S_c < \tau$", ha='center', va='top', fontsize=8.2, color='#333333')

draw_state_box(ax, x=14.65, y=y_nomat, w=1.65, h=0.62,
               title="NO_MATCH",
               facecolor="#f3e8ff", edgecolor="#7b2cbf")

plt.tight_layout()
plt.savefig('pipeline-liveness.png', format='png', dpi=300, bbox_inches='tight')
plt.show()
